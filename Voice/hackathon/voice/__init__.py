# voice/__init__.py
import os
import time
from io import BytesIO
from typing import Optional, Callable, List, Tuple

import numpy as np
import sounddevice as sd
import soundfile as sf
from dotenv import load_dotenv

load_dotenv()

SAMPLE_RATE = 16000
CHANNELS = 1

def float_to_wav_bytes(audio_float: np.ndarray, samplerate: int = SAMPLE_RATE) -> BytesIO:
    """Convert a float32 mono array [-1,1] into 16-bit PCM WAV in memory."""
    if audio_float.ndim > 1:
        audio_float = np.mean(audio_float, axis=1)
    audio_float = audio_float.astype(np.float32)
    bio = BytesIO()
    sf.write(bio, audio_float, samplerate, format="WAV", subtype="PCM_16")
    bio.seek(0)
    return bio

def list_input_devices() -> List[Tuple[int, str]]:
    """Return [(index, label), ...] of audio input devices."""
    devs = sd.query_devices()
    hostapis = sd.query_hostapis()
    out = []
    for i, d in enumerate(devs):
        if d.get("max_input_channels", 0) > 0:
            name = d.get("name", f"Device {i}")
            host = hostapis[d["hostapi"]]["name"]
            out.append((i, f"[{i}] {name} — {host}"))
    return out

class VoiceTranscriber:
    """
    ElevenLabs STT wrapper (English-only) + simple microphone recorder.
    Designed to be used programmatically or via a thin HTTP layer.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_id: str = "scribe_v1",
        diarize: bool = False,
        tag_audio_events: bool = True,
        language_code: str = "eng",  # English only per your requirement
    ):
        try:
            from elevenlabs import ElevenLabs
        except Exception as e:
            raise RuntimeError(f"Could not import ElevenLabs SDK: {e}")

        self.api_key = api_key or os.getenv("ELEVEN_API_KEY")
        if not self.api_key:
            raise RuntimeError("ELEVEN_API_KEY missing. Put it in .env or pass api_key=...")

        try:
            self.client = ElevenLabs(api_key=self.api_key)
        except Exception as e:
            raise RuntimeError(f"Failed to create ElevenLabs client: {e}")

        self.model_id = model_id
        self.diarize = diarize
        self.tag_audio_events = tag_audio_events
        self.language_code = language_code

    # -------- Recording (server-side mic) --------
    def record(
        self,
        seconds: Optional[float] = None,
        samplerate: int = SAMPLE_RATE,
        channels: int = CHANNELS,
        device: Optional[int] = None,
        level_callback: Optional[Callable[[float], None]] = None,
        stop_flag: Optional[Callable[[], bool]] = None,
    ) -> np.ndarray:
        """
        Record from default (or given) input device.
        - If seconds is provided, records fixed duration.
        - Else, records until stop_flag() returns True.
        Returns mono float32 array in range [-1, 1].
        """
        frames = []

        def _cb(indata, frames_count, time_info, status):
            if status:
                # status._flag gives PortAudio warnings; we ignore or log if needed
                pass
            mono = indata
            if mono.ndim == 2 and mono.shape[1] > 1:
                mono = np.mean(mono, axis=1, keepdims=True)
            frames.append(mono.copy())
            if level_callback is not None:
                lvl = float(np.sqrt(np.mean(np.square(mono)))) if mono.size else 0.0
                level_callback(lvl)

        stream = sd.InputStream(
            samplerate=samplerate,
            channels=channels,
            dtype="float32",
            device=device,  # None = default device
            callback=_cb,
        )

        stream.start()
        try:
            if seconds is not None:
                sd.sleep(int(seconds * 1000))
            else:
                # indefinite until stop_flag() is True
                while True:
                    sd.sleep(50)
                    if stop_flag is not None and stop_flag():
                        break
        finally:
            stream.stop()
            stream.close()

        audio = np.concatenate(frames, axis=0).squeeze(-1).astype(np.float32) if frames else np.zeros(0, np.float32)
        return audio

    # -------- Transcription helpers --------
    def _convert_any(self, file_like) -> str:
        """
        Pass-through conversion using ElevenLabs.
        Accepts file-like (BytesIO, SpooledTemporaryFile, etc.) or raw bytes.
        """
        try:
            # elevenlabs SDK accepts a file-like with .read()
            resp = self.client.speech_to_text.convert(
                file=file_like,
                model_id=self.model_id,
                diarize=self.diarize,
                tag_audio_events=self.tag_audio_events,
                language_code=self.language_code,
            )
            return getattr(resp, "text", "") or ""
        except Exception as e:
            raise RuntimeError(f"Transcription error: {e}")

    def transcribe_ndarray(self, audio_float: np.ndarray, samplerate: int = SAMPLE_RATE) -> str:
        """
        Convert numpy float32 audio -> WAV bytes -> transcribe.
        """
        wav_io = float_to_wav_bytes(audio_float, samplerate)
        return self._convert_any(wav_io)

    def transcribe_file(self, path: str) -> str:
        """
        Transcribe an on-disk audio file (wav/mp3/m4a/etc. – SDK handles formats).
        """
        try:
            with open(path, "rb") as f:
                return self._convert_any(f)
        except Exception as e:
            raise RuntimeError(f"Failed to open file '{path}': {e}")

    def transcribe_bytes(self, data: bytes) -> str:
        """
        Transcribe raw bytes from the client (e.g., React MediaRecorder Blob).
        """
        bio = BytesIO(data)
        bio.seek(0)
        return self._convert_any(bio)

    # -------- Convenience --------
    def record_and_transcribe(
        self,
        seconds: float = 5.0,
        samplerate: int = SAMPLE_RATE,
        channels: int = CHANNELS,
        device: Optional[int] = None,
    ) -> str:
        """One-call mic -> text."""
        audio = self.record(seconds=seconds, samplerate=samplerate, channels=channels, device=device)
        if audio.size == 0:
            return ""
        return self.transcribe_ndarray(audio, samplerate=samplerate)
    
    def record_with_vad(
        self,
        max_seconds: float = 30.0,
        silence_threshold: float = 0.01,
        silence_duration: float = 1.0,
        samplerate: int = SAMPLE_RATE,
        channels: int = CHANNELS,
        device: Optional[int] = None,
    ) -> np.ndarray:
        """
        Record audio with Voice Activity Detection (VAD).
        Stops recording after silence_duration seconds of silence.
        
        Args:
            max_seconds: Maximum recording duration
            silence_threshold: RMS level below which audio is considered silence
            silence_duration: Seconds of silence before stopping
            samplerate: Sample rate
            channels: Number of channels
            device: Audio input device
            
        Returns:
            Recorded audio as numpy array
        """
        frames = []
        silence_frames = 0
        silence_frames_needed = int(silence_duration * samplerate / 1024)  # assuming 1024 frame chunks
        has_speech = False
        should_stop = False
        
        def _cb(indata, frames_count, time_info, status):
            nonlocal silence_frames, has_speech, should_stop
            
            if should_stop:
                return
                
            mono = indata
            if mono.ndim == 2 and mono.shape[1] > 1:
                mono = np.mean(mono, axis=1, keepdims=True)
            
            frames.append(mono.copy())
            
            # Calculate RMS level
            rms = float(np.sqrt(np.mean(np.square(mono)))) if mono.size else 0.0
            
            if rms > silence_threshold:
                has_speech = True
                silence_frames = 0
            elif has_speech:
                # Only count silence after we've detected speech
                silence_frames += 1
                if silence_frames >= silence_frames_needed:
                    should_stop = True
        
        stream = sd.InputStream(
            samplerate=samplerate,
            channels=channels,
            dtype="float32",
            device=device,
            callback=_cb,
        )
        
        stream.start()
        try:
            start_time = time.time()
            while time.time() - start_time < max_seconds:
                sd.sleep(50)
                if should_stop:
                    break
        finally:
            stream.stop()
            stream.close()
        
        audio = np.concatenate(frames, axis=0).squeeze(-1).astype(np.float32) if frames else np.zeros(0, np.float32)
        return audio
    
    def record_and_transcribe_vad(
        self,
        max_seconds: float = 30.0,
        silence_threshold: float = 0.01,
        silence_duration: float = 1.0,
        samplerate: int = SAMPLE_RATE,
        channels: int = CHANNELS,
        device: Optional[int] = None,
    ) -> str:
        """
        Record with VAD and transcribe. Stops automatically after silence_duration of silence.
        
        Args:
            max_seconds: Maximum recording duration
            silence_threshold: RMS level below which audio is considered silence
            silence_duration: Seconds of silence before stopping (default 1.0)
            samplerate: Sample rate
            channels: Number of channels
            device: Audio input device
            
        Returns:
            Transcribed text
        """
        audio = self.record_with_vad(
            max_seconds=max_seconds,
            silence_threshold=silence_threshold,
            silence_duration=silence_duration,
            samplerate=samplerate,
            channels=channels,
            device=device
        )
        if audio.size == 0:
            return ""
        return self.transcribe_ndarray(audio, samplerate=samplerate)
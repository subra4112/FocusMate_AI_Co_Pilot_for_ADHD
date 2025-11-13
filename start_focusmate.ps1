param(
    [string]$ApiHost = "http://127.0.0.1:8000",
    [int]$CalendarPort = 5173,
    [string]$VoiceApiHost = "http://127.0.0.1:8001",
    [switch]$Tunnel
)

$backendPath = "E:\FocusMate\Email"
$calendarPath = "E:\FocusMate\Calendar\focusmate-final-changed-api\focusmate-final\focusmate-app"
$mobilePath = "E:\FocusMate\Frontend\FocusMateMailApp"
$voicePath = "E:\FocusMate\Voice\hackathon"
$backendPython = Join-Path $backendPath "my_env\Scripts\python.exe"
$voiceUri = [System.Uri]$VoiceApiHost
$voicePort = $voiceUri.Port
if ($voicePort -eq -1) {
    $voicePort = if ($voiceUri.Scheme -eq "https") { 443 } else { 80 }
}

if (-not (Test-Path $backendPython)) {
    Write-Error "Cannot find virtual environment python at $backendPython. Create the venv first."
    exit 1
}

Write-Host "Starting FocusMate stack..."
Write-Host "API base: $ApiHost"
Write-Host "Voice API base: $VoiceApiHost"

# Launch FastAPI in the background so this shell can keep running the front-ends.
$backendJob = Start-Job -Name "focusmate-backend" -ScriptBlock {
    param($pythonPath, $workingDir)
    Set-Location $workingDir
    & $pythonPath -m uvicorn api.server:app --reload --host 0.0.0.0 --port 8000
} -ArgumentList $backendPython, $backendPath

# Launch the web calendar (Vite) dev server in a background job.
$calendarJob = Start-Job -Name "focusmate-calendar" -ScriptBlock {
    param($appPath, $port, $apiHost)
    Set-Location $appPath
    $env:VITE_API_BASE_URL = $apiHost
    npm run dev -- --host 0.0.0.0 --port $port
} -ArgumentList $calendarPath, $CalendarPort, $ApiHost

# Launch the voice transcription FastAPI backend.
$voiceJob = Start-Job -Name "focusmate-voice" -ScriptBlock {
    param($workingDir, $port)
    Set-Location $workingDir
    & python -m uvicorn enhanced_server:app --reload --host 0.0.0.0 --port $port
} -ArgumentList $voicePath, $voicePort

try {
    # Run the mobile (Expo) app in the current shell so QR code and logs stay visible.
    Set-Location $mobilePath
    $env:EXPO_PUBLIC_API_URL = $ApiHost
    $env:EXPO_PUBLIC_VOICE_API_URL = $VoiceApiHost

    if ($Tunnel.IsPresent) {
        npm start -- --tunnel
    } else {
        npm start
    }
}
finally {
    Write-Host "`nShutting down background services..."
    foreach ($job in @($calendarJob, $backendJob, $voiceJob)) {
        if ($job -and (Get-Job -Id $job.Id -ErrorAction SilentlyContinue)) {
            Stop-Job $job -Force | Out-Null
            Remove-Job $job | Out-Null
        }
    }
    Write-Host "All services stopped."
}

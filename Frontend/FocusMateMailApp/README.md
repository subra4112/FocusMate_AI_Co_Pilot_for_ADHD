# FocusMate Mail Mobile Frontend

Mobile-first Expo app that visualizes the FocusMate email triage experience. It renders task, instruction, and article classifications with ADHD-friendly summaries, quick actions, and a detail sheet, so the UX can be previewed directly from Expo Go.

## Prerequisites

- Node.js 18+ (ships with npm).
- Expo CLI (`npm install -g expo-cli`) is optional but handy.
- Expo Go app installed on your Android or iOS device for live previews.

## Getting Started

1. **Run the backend** (from `E:\FocusMate\Email`)
   ```bash
   .\my_env\Scripts\Activate.ps1
   uvicorn api.server:app --reload --port 8000
   ```

2. **Expose the backend to your device**  
   When using Expo Go on Android/iOS, `localhost` refers to the device. Either:
   - Run Expo in tunnel mode: `npm start -- --tunnel`, or
   - Replace `EXPO_PUBLIC_API_URL` with your PC's LAN IP (e.g. `http://192.168.0.25:8000`).

3. **Configure the Expo app**
   - Create `E:\FocusMate\Frontend\FocusMateMailApp\.env` with:
     ```
     EXPO_PUBLIC_API_URL=http://127.0.0.1:8000
     ```
     Update the host/IP as noted in step 2.

4. **Start Expo**
   ```bash
   cd E:\FocusMate\Frontend\FocusMateMailApp
   npm install        # already run during project creation, rerun if needed
   npm start          # launches the Expo dev server
   ```

5. **Open on device**
   Scan the QR code with Expo Go (Android) or the Expo mobile camera (iOS). You can also run the web preview with `npm run web`.

### One-command launcher (optional)

From the repository root you can run:

```powershell
.\start_focusmate.ps1 -ApiHost http://192.168.0.78:8000 -Tunnel
```

The script starts the FastAPI backend in the background and then boots Expo (with tunnel if you pass `-Tunnel`). Adjust the `-ApiHost` parameter to match the value you place in `.env`.

## Project Structure

- `App.js` – wraps the home experience in a safe area view.
- `src/screens/HomeScreen.js` – main screen with inbox spotlight and detail sheet.
- `src/components/` – reusable UI building blocks (headers, filters, cards, sheets).
- `src/services/emails.js` – fetches and normalizes responses from the FastAPI backend.
- `src/data/sampleEmails.js` – quick action metadata (no longer used for email content).
- `src/theme/` – shared colors, spacing, and typography tokens.
- `src/utils/dates.js` – helpers for relative and due-date formatting.

## Next Steps

- Add React Navigation for multi-screen flows (settings, search, etc.).
- Implement context/state to sync with the backend task list and calendar holds.
- Create theming toggles (dark/light) if you plan to ship beyond prototypes.


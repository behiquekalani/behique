# Behike Wellness

Circadian wellness for your screen, your focus, and your sleep.
A native Mac (and Windows) desktop app built with Electron.

Copyright 2026 Behike. All rights reserved.

## Features

- Blue light filter with auto circadian adjustments
- Ambient sound generator (rain, ocean, forest, wind, fire, white noise)
- ADHD Focus Mode (Pomodoro timer with screen dimming)
- Sleep coach with bedtime countdown and consistency tracking
- Guided breathing exercises (4-7-8, Box, 2-4 Quick Calm)
- Smart schedule mapped to your local sunrise/sunset
- Mood check-in with 30-day chart
- Daily journal with prompts and weekly reflections
- Habit tracker with streaks and GitHub-style heatmap
- Achievement badges
- System tray app with global shortcut (Cmd+Shift+W)

## Development Setup

```bash
npm install
npm start
```

The app opens as a menu bar app (system tray). Use Cmd+Shift+W to toggle the window, or click the tray icon.

## Build for Mac

```bash
npm run build-mac
```

Output: `dist/Behike Wellness-1.0.0-universal.dmg`

For code signing and notarization, set the environment variables documented in `build-config.js`.

## Build for Windows

```bash
npm run build-win
```

Output: `dist/Behike Wellness Setup 1.0.0.exe`

## Distribution

Two channels:

1. Direct download from your website (free or gated)
2. Gumroad at $9.99 (upload the .dmg and .exe)

## Auto-Update (future)

Add `electron-updater` and configure a release server (GitHub Releases or S3). See `build-config.js` for details.

## App Icon

1. Open `icon.html` in a browser
2. Screenshot the 512x512 icon
3. Save as `icon.png` in this directory
4. For Mac, convert to .icns using iconutil
5. For Windows, convert to .ico

## Tech Stack

- Electron 33+
- Pure HTML/CSS/JS (no framework, single file)
- Web Audio API for ambient sounds
- localStorage for all data persistence
- auto-launch for login startup

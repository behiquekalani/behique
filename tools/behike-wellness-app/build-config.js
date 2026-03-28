// Behike Wellness - Build Configuration
// Copyright 2026 Behike. All rights reserved.
//
// This file documents the electron-builder configuration.
// The actual config lives in package.json under the "build" key.
//
// To build:
//   npm run build-mac    -> outputs .dmg in /dist
//   npm run build-win    -> outputs .exe in /dist
//
// Code signing (Mac):
//   Set these environment variables before building:
//     CSC_LINK=path/to/your/certificate.p12
//     CSC_KEY_PASSWORD=your-password
//     APPLE_ID=your@apple.id
//     APPLE_APP_SPECIFIC_PASSWORD=xxxx-xxxx-xxxx-xxxx
//     APPLE_TEAM_ID=your-team-id
//
//   Without code signing, the app will still build but users
//   will see a Gatekeeper warning on first launch.
//
// Code signing (Windows):
//   Set CSC_LINK and CSC_KEY_PASSWORD for your .pfx certificate.
//
// Auto-update (future):
//   Add electron-updater dependency and configure a release server.
//   Options: GitHub Releases, S3, or your own server.
//   See: https://www.electron.build/auto-update
//
// Icon generation:
//   1. Open icon.html in a browser
//   2. Screenshot the 512x512 canvas
//   3. Save as icon.png in this directory
//   4. For Mac .icns: use iconutil or an online converter
//   5. For Windows .ico: use an online converter
//
// Notarization (Mac, required for distribution):
//   Install @electron/notarize and add an afterSign hook.
//   See: https://www.electron.build/code-signing

module.exports = {
  // Re-exported for programmatic use if needed
  getConfig: () => require('./package.json').build
};

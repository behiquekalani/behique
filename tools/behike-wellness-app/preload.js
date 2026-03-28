// Behike Wellness - Preload Script
// Copyright 2026 Behike. All rights reserved.
// Security bridge between renderer and main process.

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('behikeAPI', {
  // Window controls
  toggleAlwaysOnTop: () => ipcRenderer.invoke('toggle-always-on-top'),
  getAlwaysOnTop: () => ipcRenderer.invoke('get-always-on-top'),

  // Auto-launch
  toggleAutoLaunch: () => ipcRenderer.invoke('toggle-auto-launch'),
  getAutoLaunch: () => ipcRenderer.invoke('get-auto-launch'),

  // Notifications
  notify: (title, body) => ipcRenderer.invoke('show-notification', title, body),

  // Focus timer from tray
  onQuickFocus: (callback) => ipcRenderer.on('quick-focus', () => callback()),
  onToggleFilter: (callback) => ipcRenderer.on('toggle-filter', () => callback()),

  // Platform info
  platform: process.platform,

  // Theme
  onThemeChange: (callback) => {
    ipcRenderer.on('native-theme-changed', (_, isDark) => callback(isDark));
  },
  getNativeTheme: () => ipcRenderer.invoke('get-native-theme')
});

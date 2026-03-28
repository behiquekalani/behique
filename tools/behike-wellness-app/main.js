// Behike Wellness - Electron Main Process
// Copyright 2026 Behike. All rights reserved.

const {
  app,
  BrowserWindow,
  Tray,
  Menu,
  globalShortcut,
  ipcMain,
  nativeTheme,
  Notification,
  nativeImage
} = require('electron');
const path = require('path');

// Keep references to prevent garbage collection
let mainWindow = null;
let tray = null;
let autoLauncher = null;
let isQuitting = false;

// ---- AUTO LAUNCH ----
function getAutoLauncher() {
  if (!autoLauncher) {
    try {
      const AutoLaunch = require('auto-launch');
      autoLauncher = new AutoLaunch({
        name: 'Behike Wellness',
        path: app.getPath('exe')
      });
    } catch (e) {
      // auto-launch not available in dev mode
      console.log('auto-launch not available:', e.message);
    }
  }
  return autoLauncher;
}

// ---- WINDOW ----
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 400,
    height: 600,
    minWidth: 360,
    minHeight: 500,
    maxWidth: 500,
    frame: false,
    titleBarStyle: 'hidden',
    vibrancy: 'under-window',
    visualEffectState: 'active',
    transparent: true,
    backgroundColor: '#00000000',
    show: false,
    skipTaskbar: true,
    resizable: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true
    }
  });

  mainWindow.loadFile('index.html');

  // Don't show in dock on Mac
  if (process.platform === 'darwin') {
    app.dock.hide();
  }

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    // Position near tray icon (top right on Mac)
    positionWindowNearTray();
  });

  // Hide instead of close
  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });

  // Send theme changes to renderer
  nativeTheme.on('updated', () => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('native-theme-changed', nativeTheme.shouldUseDarkColors);
    }
  });
}

function positionWindowNearTray() {
  if (!tray || !mainWindow) return;
  const trayBounds = tray.getBounds();
  const windowBounds = mainWindow.getBounds();

  // Position below the tray icon, centered horizontally
  const x = Math.round(trayBounds.x + (trayBounds.width / 2) - (windowBounds.width / 2));
  const y = Math.round(trayBounds.y + trayBounds.height + 4);

  mainWindow.setPosition(x, y, false);
}

function toggleWindow() {
  if (!mainWindow) return;
  if (mainWindow.isVisible()) {
    mainWindow.hide();
  } else {
    positionWindowNearTray();
    mainWindow.show();
    mainWindow.focus();
  }
}

// ---- TRAY ----
function createTray() {
  // Create a simple tray icon (16x16 template image for macOS)
  const iconPath = path.join(__dirname, 'icon.png');
  let trayIcon;

  try {
    trayIcon = nativeImage.createFromPath(iconPath);
    trayIcon = trayIcon.resize({ width: 18, height: 18 });
    if (process.platform === 'darwin') {
      trayIcon.setTemplateImage(true);
    }
  } catch (e) {
    // Fallback: create a simple circle icon programmatically
    trayIcon = createDefaultTrayIcon();
  }

  tray = new Tray(trayIcon);
  tray.setToolTip('Behike Wellness');

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Open Dashboard',
      click: () => {
        if (mainWindow) {
          positionWindowNearTray();
          mainWindow.show();
          mainWindow.focus();
        }
      }
    },
    {
      label: 'Quick Focus (25 min)',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
          mainWindow.webContents.send('quick-focus');
        }
      }
    },
    {
      label: 'Toggle Filter',
      click: () => {
        if (mainWindow) {
          mainWindow.webContents.send('toggle-filter');
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        isQuitting = true;
        app.quit();
      }
    }
  ]);

  tray.setContextMenu(contextMenu);

  // Click tray icon to toggle window
  tray.on('click', () => {
    toggleWindow();
  });
}

function createDefaultTrayIcon() {
  // Create a minimal 18x18 icon if icon.png is missing
  const canvas = nativeImage.createEmpty();
  return canvas;
}

// ---- IPC HANDLERS ----
function setupIPC() {
  ipcMain.handle('toggle-always-on-top', () => {
    if (!mainWindow) return false;
    const current = mainWindow.isAlwaysOnTop();
    mainWindow.setAlwaysOnTop(!current);
    return !current;
  });

  ipcMain.handle('get-always-on-top', () => {
    return mainWindow ? mainWindow.isAlwaysOnTop() : false;
  });

  ipcMain.handle('toggle-auto-launch', async () => {
    const launcher = getAutoLauncher();
    if (!launcher) return false;
    try {
      const isEnabled = await launcher.isEnabled();
      if (isEnabled) {
        await launcher.disable();
        return false;
      } else {
        await launcher.enable();
        return true;
      }
    } catch (e) {
      console.error('Auto-launch toggle failed:', e);
      return false;
    }
  });

  ipcMain.handle('get-auto-launch', async () => {
    const launcher = getAutoLauncher();
    if (!launcher) return false;
    try {
      return await launcher.isEnabled();
    } catch (e) {
      return false;
    }
  });

  ipcMain.handle('show-notification', (_, title, body) => {
    if (Notification.isSupported()) {
      const notif = new Notification({ title, body, silent: false });
      notif.show();
      // Clicking notification opens the app
      notif.on('click', () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        }
      });
    }
    return true;
  });

  ipcMain.handle('get-native-theme', () => {
    return nativeTheme.shouldUseDarkColors;
  });
}

// ---- APP LIFECYCLE ----
app.whenReady().then(() => {
  setupIPC();
  createWindow();
  createTray();

  // Global shortcut: Cmd+Shift+W (Mac) / Ctrl+Shift+W (Win/Linux)
  const shortcut = process.platform === 'darwin' ? 'CommandOrControl+Shift+W' : 'Ctrl+Shift+W';
  globalShortcut.register(shortcut, () => {
    toggleWindow();
  });
});

app.on('window-all-closed', () => {
  // Don't quit when window closes, we're a tray app
});

app.on('before-quit', () => {
  isQuitting = true;
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});

app.on('activate', () => {
  if (!mainWindow) {
    createWindow();
  } else {
    mainWindow.show();
  }
});

// Prevent multiple instances
const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    if (mainWindow) {
      mainWindow.show();
      mainWindow.focus();
    }
  });
}

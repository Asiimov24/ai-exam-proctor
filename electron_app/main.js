const { app, BrowserWindow, globalShortcut, ipcMain } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {

    mainWindow = new BrowserWindow({
        width: 1920,
        height: 1080,
        fullscreen: true,
        alwaysOnTop: true,
        resizable: false,
        minimizable: false,
        maximizable: false,
        closable: false,
        kiosk: true,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false
        }
    });

    mainWindow.removeMenu();
    mainWindow.setMenuBarVisibility(false);
    mainWindow.loadFile('screens/login.html');
    mainWindow.webContents.openDevTools();

    // Block DevTools
    mainWindow.webContents.on('before-input-event', (event, input) => {
        if (
            input.key === 'F12' ||
            (input.control && input.shift && input.key.toLowerCase() === 'i') ||
            (input.control && input.key.toLowerCase() === 'r') ||
            (input.control && input.key.toLowerCase() === 'w') ||
            (input.alt && input.key === 'F4')
        ) {
            event.preventDefault();
        }
    });

    // Prevent navigation
    mainWindow.webContents.on('will-navigate', (event) => {
        event.preventDefault();
    });

    // Prevent new windows
    mainWindow.webContents.setWindowOpenHandler(() => {
        return { action: 'deny' };
    });
}

app.whenReady().then(() => {
    const { ipcMain } = require('electron');

    createWindow();
    ipcMain.on('navigate', (event, page) => {
    mainWindow.loadFile(`screens/${page}`);
    });

    // Block common shortcuts
    globalShortcut.register('Alt+Tab', () => {});
    globalShortcut.register('Control+Escape', () => {});
    globalShortcut.register('CommandOrControl+Shift+I', () => {});
    globalShortcut.register('F12', () => {});
});

app.on('window-all-closed', () => {
    app.quit();
});
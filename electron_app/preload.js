const { contextBridge, ipcRenderer } = require('electron');

console.log("PRELOAD LOADED");

contextBridge.exposeInMainWorld('api', {
    navigate: (page) => {
        console.log("NAVIGATE CALLED:", page);
        ipcRenderer.send('navigate', page);
    }
});
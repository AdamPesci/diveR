const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn, execFile} = require('child_process');

let DISPLAY_SETTINGS_PATH;
let LANGUAGE_FILE_PATH;

if (process.env.RUN_DEV === "true") {
    LANGUAGE_FILE_PATH = './settings/languages.json';
    DISPLAY_SETTINGS_PATH = './settings/display.json';
} else {
    LANGUAGE_FILE_PATH = './resources/app/settings/languages.json';
    DISPLAY_SETTINGS_PATH = './resources/app/settings/display.json';
}
let file_path = "no file"
// From electron-forge
// if (require('electron-squirrel-startup')) { // eslint-disable-line global-require
//   app.quit();
// }

//Ignore windows display scaling.
app.commandLine.appendSwitch('high-dpi-support', 1)
app.commandLine.appendSwitch('force-device-scale-factor', 1)

//Code for setting up electron window
function createWindow() {
    const win = new BrowserWindow({
        autoHideMenuBar: true,
        width: 1500,
        height: 900,
        minWidth: 1100,
        minHeight: 775,
        name: "diveR",
        icon: __dirname + '\\Resources\\diveR_Logo.ico',
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: true,
            contextIsolation: false,
            enableRemoteModule: true
        }
    })

    win.loadFile(path.join(__dirname, 'index.html'));
}

app.whenReady().then(() => {
    createWindow();

    app.on('activate', function () {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') app.quit();
});

/* "args" is a stringified object of the following format:
{
    filePaths: [],
    halfTimeSet: "",
    gasCombinations: [
        ['O2', 'N2', 'He', 100],
    ],
    outputFilePath: "C:\Documents\Files\DiveResearch\my_result.csv",
    gfToggle: true,
    cpToggle: false
}
*/
ipcMain.on('asynchronous-message', (event, args) => {
    console.log("Called async ipc");
    // Event emitter for sending asynchronous messages.
    let python_process;
    console.log("ENV: " + process.env.RUN_DEV)
    if (process.env.RUN_DEV === "true") {
        // Dev paths:
        let pyPath = path.join(__dirname, '..', 'py', 'main', 'Main.py');
        python_process = spawn("python", [pyPath, args]);
    } else {
        // Prod/Dist paths:
        let pyExePath = path.join(__dirname, '..', '..', 'dist', 'Main', 'Main.exe');
        python_process = execFile(pyExePath, [args])
    }
    console.log(python_process.pid);

    python_process.stdout.on('data', (data) => {
        console.log('Result: ' + data.toString());
        event.sender.send('asynchronous-reply', data.toString());
    })

    python_process.stderr.on('data', (data) => {
        console.log(data.toString());
    })
})


ipcMain.on('writeDisplaySettings', (event, args) => {
    fs.mkdir('./settings', { recursive: true }, (err) => {
        if (err) throw err;
    });

    fs.writeFile(DISPLAY_SETTINGS_PATH, args, (err) => {
        if (err) {
            console.log("Couldn't write to settings file.");
            console.log(err);
        }
    });
})

ipcMain.on('readDisplaySettings', (event, args) => {
    fs.readFile(DISPLAY_SETTINGS_PATH, (err, jsonString) => {
        if (err) {
            console.log("File doesn't exist");
        } else {
            event.sender.send('receiveDisplaySettings', jsonString.toString());
        }
    })
})

ipcMain.on('readLanguageFile', (event, args) => {
    fs.readFile(LANGUAGE_FILE_PATH, (err, jsonString) => {
        if (err) {
            console.log("Language File doesn't exist");
        } else {
            event.sender.send('receiveLanguageFile', jsonString.toString());
        }
    })
})




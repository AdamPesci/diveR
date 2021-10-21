const { ipcRenderer } = require('electron');
const dialog = require('electron').remote.dialog;
const runButton = document.getElementById("run-btn");
const halfTimeSetSelect = document.getElementById("half-time-label");
const saveAsButton = document.getElementById("save-as-btn");
const addGasButton = document.getElementById("add-gas-btn");
const resultTable = document.getElementById("results-table");
const spinner = document.getElementById("spinner");
const rightSideContainer = document.getElementById("right-side-container");
const customGasSettingsPopup = document.getElementById("custom-gas-popup");
const progressBar = document.getElementById("progress-bar");
const progressBarContainer = document.getElementById("calculation-progress");
const gfToggle = document.getElementById("gf-btn");
const gfLabel = document.getElementById("gf-label");
const cpToggle = document.getElementById("additional-cp-values-btn");
const cpLabel = document.getElementById("additional-cp-values-label");

let errorMessages = {
    noUpload : "Error loading files - please check that correct files were uploaded.",
    noOutput : "No output file selected.",
    startTime : "Start time must be equal to or greater than 0.",
    fillAllGases : "Please fill in all 3 gases.",
    gasTotal : "Gases must add up to 1.0.",
    oxygenNonZero : "Oxygen must be a non-zero value.",
};

// Settings structure
// {
//     filePaths: [],
//     halfTimeSet: "",
//     gasCombinations: [
//         ['O2', 'N2', 'He', 100],
//         ['O2', 'N2', 'He', 20]
//     ],
//     outputFilePath: "C:\Documents\Files\DiveResearch\dive_in_honolulu_3242",
// } 

// Example for the input that will be received from the backend - placeholder for our calculations.
// const EXAMPLE_JSON = {
//     "headers": [ "MaxIns", "MaxBub", "MaxCP"], //One for each array in "results"
//     "dives": [
//         {
//             "profile": "dive_series1",
//             "model": "Buhlmann",
//             "results": [
//                 [1.7361208417147393,
//                     1.7319965520024265,
//                     1.7239482251073908], //maxIns
//                 [1.5215008417147395,
//                     1.5173765520024267,
//                     1.5076482251073908], //maxBub
//                 [ 
//                     2.5435008417147396,
//                     2.5393765520024267,
//                     2.537648225107391,
//                 ] // maxCP
//             ]
//         },
//         {
//             "profile": "dive_series2",
//             "model": "Buhlmann",
//             "results": [
//                 [1.7361208417147393,
//                     1.7319965520024265,
//                     1.7239482251073908], //maxIns
//                 [1.5215008417147395,
//                     1.5173765520024267,
//                     1.5076482251073908], //maxBub
//                 [ 
//                     2.5435008417147396,
//                     2.5393765520024267,
//                     2.537648225107391,
//                 ] // maxCP
//             ]
//         }
//     ]
// }

let settings = {
    filePathsDirectory: "",
    filePaths: [],
    halfTimeSet: "",
    gasCombinations: [],
    outputFilePath: "",
    gfToggle: true,
    cpToggle: false,
}

let gasOptions = {
    selectedGases: [],
    isAirSelected: true,
}

let loadingBarExists = false;

function sendData() {
    updateSettings();
    if (settings.outputFilePath !== "" && settings.filePaths.length !== 0) {
        runButton.disabled = true;
        ipcRenderer.send('asynchronous-message', JSON.stringify(settings));
        resultTable.innerHTML = "";
        //Remove loading bar if one already exists.
        if (progressBarContainer.hidden == false){
            progressBarContainer.hidden = true;
            clearInterval(interval)
        }
        updateProgressBar();

        setTimeout(() => {
            runButton.disabled = false;
        }, 30000);
    } else if (settings.filePaths.length === 0) {
        swal(errorMessages.noUpload);
    } else {
        swal(errorMessages.noOutput);
    }
}

function updateSettings() {
    updateFilePaths();
    settings.halfTimeSet = getHalfTimeSet();

    if (gasOptions.isAirSelected) {
        settings.gasCombinations = [];
    } else {
        settings.gasCombinations = gasOptions.selectedGases;
    }
}

function updateFilePaths() {
    let newFiles = fileInput.files;

    if (settings.filePaths.length !== 0 && newFiles.length === 0) {
        return;
    } else if (newFiles.length > 1300) {
        swal("Please limit file upload to 1300 files.")
        return;
    }

    settings.filePaths = []
    for (const file of newFiles) {
        // Splits the file path into an array of strings, where each dir is an element.
        foldersAndFile = file.path.split("\\");
        // All of the paths except for the last are part of the folder path (not)
        // the file path, so combine them all.
        folders = foldersAndFile.slice(0,foldersAndFile.length-1);
        folderPath = folders.join("/") + "/";
        // The final element of the foldersAndFile array is the file name itself.
        newFilePath = foldersAndFile[foldersAndFile.length - 1];

        settings.filePaths.push(newFilePath);
        settings.filePathsDirectory = folderPath;
    }
    
}

function getHalfTimeSet() {
    return halfTimeSetSelect.value;
}

function getOutputDirectory() {
    dialog.showSaveDialog(options = {
        title: "Select a save location for the output file.",
    }).then((result) => {
        if (!result.canceled) {
            settings.outputFilePath = result.filePath;
        }
    })
}

// Will iterate through entire JSON response and update the table accordingly.
function updateTableData(results) {
    resultTable.innerHTML = "";

    if (results.dives.length === 0) {
        swal(errorMessages.noUpload);
        return;
    }

    let isZHL16 = false;
    let isWorkman = false;
    if (results.dives[0].model === "ZH-L16A"
        || results.dives[0].model == "ZH-L16B"
        || results.dives[0].model == "ZH-L16C") {
        isZHL16 = true;
    }
    if(results.dives[0].model === "Workman65"){
        isWorkman = true
    }

    let numResults = results.dives[0].results[0].length;

    fillHeaders(results.headers, results.special, numResults, isZHL16, isWorkman);
    fillData(results.dives);
}

function fillHeaders(headers, specials, numResults, isZHL16, isWorkman) {
    let headerRow = document.createElement("tr");
    let filler = document.createElement("th");
    filler.innerHTML = "";
    headerRow.appendChild(filler);

    headers.forEach((headerString) => {
        for (let i = 0; i < numResults; i++) {
            let headerCol = document.createElement("th");
            if (isZHL16) {
                if (i == 0)
                    headerCol.innerHTML = `${headerString}1`;
                else if (i == 1) {
                    headerCol.innerHTML = `${headerString}1b`;
                }
                else {
                    headerCol.innerHTML = `${headerString}${i}`;
                }
            } else {
                headerCol.innerHTML = `${headerString}${i + 1}`;
            }

            headerRow.appendChild(headerCol);
            // Start displaying the first 3 of the "specials" headers.
            if (isZHL16 && headerString === "GFLowMax" && i === 16) {
                for (let j = 0; j < 3; j++) {
                    let headerCol = document.createElement("th");
                    let specialHeader = specials[j];
                    headerCol.innerHTML = specialHeader;
                    headerRow.appendChild(headerCol);
                }
            }

            if (isWorkman && headerString === "GFLowMax" && i === 8) {
                for (let j = 0; j < 3; j++) {
                    let headerCol = document.createElement("th");
                    let specialHeader = specials[j];
                    headerCol.innerHTML = specialHeader;
                    headerRow.appendChild(headerCol);
                }
            }
        }
            
    });

    resultTable.appendChild(headerRow);
    fillRemainingSpecial(specials, headerRow, isZHL16, isWorkman);
}

gfToggle.addEventListener("click", function (e) {
    if (gfLabel.innerText.match(": ON")) {
        settings.gfToggle = false
    }
    else {
        settings.gfToggle = true
    }
});

cpToggle.addEventListener("click", function (e) {
    if (cpToggle.innerText.match(": ON")) {
        settings.cpToggle = false
    }
    else {
        settings.cpToggle = true
    }
});

function fillRemainingSpecial(specials, headerRow, isZHL16, isWorkman) {
    if (!isZHL16 && !isWorkman) {
        specials.forEach(special => {
            let headerCol = document.createElement("th");
            headerCol.innerHTML = special;
            headerRow.appendChild(headerCol);
        });
    } else {
        //if model is zhl16 and gf toggle is off
        if (specials.length === 2) {
            specials.forEach(special => {
                let headerCol = document.createElement("th");
                headerCol.innerHTML = special;
                headerRow.appendChild(headerCol);
            });
        }
        else {
            for (let j = 3; j < specials.length; j++) {
                let headerCol = document.createElement("th");
                let specialHeader = specials[j];
                headerCol.innerHTML = specialHeader;
                headerRow.appendChild(headerCol);
            }
        }
    }
}

function fillData(results) {
    results.forEach(diveResult => {
        let resultRow = document.createElement("tr");
        let fileCol = document.createElement("th");
        fileCol.innerHTML = diveResult.profile;
        resultRow.appendChild(fileCol);

        diveResult.results.forEach((result, i) => {
            if (result instanceof Array) {
                result.forEach(num => {
                    let numTrunc = parseFloat(num).toFixed(2);
                    let resultCol = document.createElement("td");
                    resultCol.innerHTML = numTrunc;
                    resultRow.appendChild(resultCol);
                });
            } else {
                let numTrunc = parseFloat(result).toFixed(2);
                let resultCol = document.createElement("td");
                resultCol.innerHTML = numTrunc;
                resultRow.appendChild(resultCol);
            }

        });
        resultTable.appendChild(resultRow);
    });
}


/** Test cases:
 *  1) Less than 3 numbers are filled (add to 1.0)
 *  2) Less than 3 numbers are filled (add to < 1.0)
 *  3) Less than 3 numbers are filled (add to > 1.0)
 *  4) 3 Numbers filled, add to 1.0;
 *  5) 3 Numbers filled, add to < 1.0;
 *  6) 3 Numbers filled, add to > 1.0;
 * 
 */
function addCustomGas() {
    let O2 = parseFloat(document.getElementById("o2-input").value);
    let N2 = parseFloat(document.getElementById("n2-input").value);
    let He = parseFloat(document.getElementById("he-input").value);
    let startTime = parseFloat(document.getElementById("start-time-input").value);

    let nanCount = 0;
    let gases = [O2, He, N2];
    gases.forEach((gas, i) => {
        if (isNaN(gas)) {
            nanCount++;
            gases[i] = 0.0;
        }
    });

    let gasSum = gases.reduce((a, b) => a + b, 0);
    // NOTE: Alerts break the custom gas input - need an alternative (using swal instead at the moment).
    if (nanCount > 0) {
        swal(errorMessages.fillAllGases);
    } else if (startTime < 0 || isNaN(startTime)) {
        swal(errorMessages.startTime);
    } else if (gasSum > 1.0) {
        swal(errorMessages.gasTotal);
    } else if (gases[0] <= 0.0) {
        swal(errorMessages.oxygenNonZero);
    } else {
        removeIfTimeExists(startTime);
        gases.push(startTime);
        settings.gasCombinations.push(gases);
        settings.gasCombinations.sort((a, b) => {
            return a[3] - b[3];
        })
        gasOptions.selectedGases = settings.gasCombinations;
        updateGasDisplay();
    }
}

function removeIfTimeExists(time) {
    settings.gasCombinations.forEach((combination, index) => {
        if (combination[3] === time) {
            settings.gasCombinations.splice(index, 1);
            return;
        }
    }) 
}

function updateGasDisplay() {
    let gasTable = null;
    if (settings.gasCombinations.length === 0) {
        document.querySelector("#gas-table-container").remove();
        return;
    }
    if (document.querySelector("#gas-table-container") === null) {
        let tableContainer = document.createElement("div");
        gasTable = document.createElement("table");
        tableContainer.id = "gas-table-container";
        tableContainer.classList.add("shadow");
        tableContainer.appendChild(gasTable);
        gasTable.id = "gas-table";
        rightSideContainer.appendChild(tableContainer);
    }
    else {
        gasTable = document.querySelector("#gas-table");
        gasTable.innerHTML = '';
    }

    let headerRow = document.createElement("tr");
    let filler = document.createElement("th");
    filler.innerHTML = " ";
    headerRow.appendChild(filler);
    ['O2', 'He', 'N2', 'Start Time'].forEach(val => {
        let header = document.createElement("th");
        header.innerHTML = val;
        headerRow.appendChild(header)
    });
    gasTable.appendChild(headerRow);

    settings.gasCombinations.forEach(gasRow => {
        // First loop through the gases and fill in the table row.
        let newRow = document.createElement("tr");

        // Now add button & functionality for removing a gas combination from the table/list.
        let td = document.createElement("td");
        let button = document.createElement("button");

        button.innerHTML = "X";
        button.classList.add("gas-input");
        button.addEventListener("click", () => {
            let index = newRow.rowIndex - 1;
            settings.gasCombinations.splice(index, 1);
            updateGasDisplay();
        });
        button.classList.add("btn-secondary");

        td.appendChild(button);
        newRow.appendChild(td);
        gasRow.forEach(gas => {
            let gasData = document.createElement("td");
            gasData.innerHTML = gas;
            newRow.appendChild(gasData);
        });
        gasTable.appendChild(newRow);

    });
}

let interval;
function updateProgressBar() {
    progressBarContainer.hidden = false;
    setProgressBarValue(0);
    let progressDuration = 650; //Default file time.

    //Increase Duration if gradient factor is toggled on.
    if (settings.gfToggle == true)
    {
        progressDuration += 385;
        //Decrease duration if half time = ZH A-C
        if (settings.halfTimeSet == "ZH-L16A" || settings.halfTimeSet == "ZH-L16B" || settings.halfTimeSet == "ZH-L16C")
        {
            progressDuration += 2000;
        }
    }

    // Increase smoothing for smaller increments on loading bar
    smoothing = 50;

    const numFiles = parseFloat(settings.filePaths.length);

    const timeEstimatePerFile = progressDuration / smoothing;
    const stepSize = parseFloat((100 / numFiles) / smoothing).toFixed(1);

    let width = 0;
    update();
    interval = setInterval(update, timeEstimatePerFile)

    function update() {
        if (resultTable.innerHTML !== "" ) {
            setTimeout(() => {
                progressBarContainer.hidden = true;
            }, 100)
            clearInterval(interval);
            return;
        }

        if (width >= 100) {
            width = 100;
        } else {
            width += parseFloat(stepSize);
        }
        setProgressBarValue(width.toFixed(1));
    }
}

function setProgressBarValue(val) {
    progressBar.style.width = val + "%";
    progressBar.innerHTML = "";
    // progressBar.innerHTML = val + "%";
}

// ---- Event handling ----- //
runButton.addEventListener("click", () => {
    sendData();
});

saveAsButton.addEventListener("click", getOutputDirectory);
addGasButton.addEventListener("click", addCustomGas);

// Async message handler.
ipcRenderer.on('asynchronous-reply', (event, diveData) => {
    runButton.disabled = false;
    setProgressBarValue(100);
    updateTableData(JSON.parse(diveData));
})

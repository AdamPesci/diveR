const { SSL_OP_EPHEMERAL_RSA } = require("constants");
const { ipcRenderer } = require("electron");

const runBtnLabel = document.getElementById("run-btn-label");
const uploadBtnLabel = document.getElementById("upload-btn-label");
const saveBtnLabel = document.getElementById("save-as-label");
const gasBreathedSelect = document.getElementById("gas-breathed");
const inputGasButton = document.getElementById("custom-gas-button");
const folderLabel = document.getElementById("folder-label");
const addGasButton = document.getElementById("add-gas-btn");
const addGasButtonLabel = document.getElementById("add-gas-btn-label");
const advancedSettingsButton = document.getElementById("advanced-settings-btn");
const halfTimeSets = document.getElementById("half-time-sets");
const halfTimeLabel = document.getElementById("half-time-label");
const selectedHalfTime = document.getElementById("selected-half-time-set");
const gasLabel = document.getElementById("gas-label");
const airLabel = document.getElementById("air-label");
const customLabel = document.getElementById("custom-label");
const startTimeLabel = document.getElementById("start-time-label");
const gasCombination = document.getElementById("gas-combinations");
const customGasInput = document.getElementById("gas-input-fields");
const popoverBody = document.querySelector("popover-body");
const gfLabel = document.getElementById("gf-label");
const root = document.querySelector("root");
let switchInput = document.querySelector("form-switch-lg");


const English = {
    language: "English",
    run: "Run",
    upload_files: "Upload Files",
    no_files_uploaded: "No Files Uploaded",
    save_as: "Save As",
    half_time_sets: "Half-Time Sets",
    gradient_factor: "Gradient Factor",
    additional_cp_value: "Additional CP Values",
    gas_combinations: "Gas Combinations",
    air: "Air",
    custom: "Custom",
    start_time: "Start Time",
    add_gas: "Add Gas",
    settings: "Settings",
    light_mode: "Light Mode",
    language: "English",
    language_button: "Language",
    error_message_1: "Error loading files - please check that correct files were uploaded.",
    error_message_2: "No output file selected.",
    error_message_3: "Start time must be equal to or greater than 0.",
    error_message_4: "Please fill in all 3 gases.",
    error_message_5: "Gases must add up to 1.0.",
    error_message_6: "Oxygen amount must be greater than 0."
};

let languageList = null
let currentLanguage = English;
let selectedLanguage;
loadLanguages();

let displaySettings = {
    lightMode: false,
    language: "English",
}
loadDisplaySettings();

var popover = new bootstrap.Popover(advancedSettingsButton, {
    placement: 'bottom',
    html: true,
    sanitize: false,
    content: `<div class="form-check form-switch form-switch-lg">
    <input class="form-check-input" type="checkbox" id="flexSwitchCheckDefault">
    <label class="form-check-label" id="light-mode-label" for="flexSwitchCheckDefault">Light Mode</label>
  </div>
  <button class="mdc-button mdc-button--raised mdc-button--leading dropdown-toggle language" id="language-btn" data-bs-toggle="dropdown">
  <span class="mdc-button__ripple" id="upload_btn_ripple"></span>
  <i class="material-icons mdc-button__icon" aria-hidden="true"></i>
  <span class="mdc-button__label text-alignment" id="language-choice-label" value="English">Language</span>
  </button>
  <ul class="dropdown-menu dropdown-menu-end dropdown-menu-dark" aria-labelledby="dropdownMenuButton2" id="language-choice">
  </ul>`
});


halfTimeLabel.value ="Haldane" //Default Value for half time set.
gasLabel.value ="Air" //Default Value for gas.

//Initally disable all elements in the gas input div.
var nodes = customGasInput.getElementsByClassName('gas-input');
for(var i = 0; i < nodes.length; i++){
    nodes[i].disabled = true;
};

advancedSettingsButton.addEventListener("click", function(e) {
    const lightModeLabel = document.getElementById("light-mode-label");
    switchInput = document.getElementById("flexSwitchCheckDefault");
    switchInput.checked = displaySettings.lightMode;
    switchInput.addEventListener("click", function(e) {
        displaySettings.lightMode = !displaySettings.lightMode;
        changeTheme();
        writeDisplaySettings();
    });
    let languageChoice = document.getElementById("language-choice");
    let languageChoiceLabel = document.getElementById("language-choice-label");
    mdc.ripple.MDCRipple.attachTo(document.getElementById("language-btn"));
    
    languageChoiceLabel.innerHTML = selectedLanguage.language_button;
    lightModeLabel.innerHTML = selectedLanguage.light_mode;

    //Populate language list
    if (languageChoice.childNodes.length == 1)  //If the list is empty
    {
        Object.values(languageList).forEach(val => {
            let languageEntryLi = document.createElement("li");
            let languageEntryA = document.createElement("a");
            languageEntryA.innerHTML = val.language;
            languageEntryA.classList.add("dropdown-item");
            languageEntryLi.appendChild(languageEntryA);
            languageChoice.appendChild(languageEntryLi);
        });
    }

    languageChoice.addEventListener("click", function(e) {
        if(e.target && e.target.nodeName == "A") {
            languageChoiceLabel.innerHTML = (e.target.innerHTML);
            displaySettings.language = (e.target.innerHTML);
            currentLanguage = (e.target.innerHTML);
            changeGUILanguage();
            lightModeLabel.innerHTML = selectedLanguage.light_mode;
            writeDisplaySettings();
        }
    });
});


function changeTheme()
{
    if(displaySettings.lightMode){
        //Change to light mode.
        document.documentElement.style
        .setProperty('--primary-color', '#f0f0f0');
        document.documentElement.style
        .setProperty('--secondary-color', 'white');
        document.documentElement.style
        .setProperty('--file-viewer-color', 'white');
        document.documentElement.style
        .setProperty('--primary-text-color', 'black');
        document.documentElement.style
        .setProperty('--border-colour', '#f0f0f0');
        document.documentElement.style
        .setProperty('--primary-button-color', '#f0f0f0');
        document.documentElement.style
        .setProperty('--scroll-bar-color', 'grey');
        document.documentElement.style
        .setProperty('--primary-loader-color', '#f0f0f0');
        document.documentElement.style
        .setProperty('--secondary-loader-color', 'grey');
        document.documentElement.style
        .setProperty('--gas-input-color', '#d3d3d3');
        halfTimeSets.classList.remove("dropdown-menu-dark");
        gasCombination.classList.remove("dropdown-menu-dark");
        if (document.querySelector("#language-choice")) {
            document.querySelector("#language-choice").classList.remove("dropdown-menu-dark");
        }
    }
    else{
        //Change to dark mode.
        document.documentElement.style
        .setProperty('--primary-color', '#36393F');
        document.documentElement.style
        .setProperty('--secondary-color', '#40444B');
        document.documentElement.style
        .setProperty('--file-viewer-color', '#40444B');
        document.documentElement.style
        .setProperty('--primary-text-color', 'white');
        document.documentElement.style
        .setProperty('--border-colour', '#2c2f33');
        document.documentElement.style
        .setProperty('--primary-button-color', '#2F3136');
        document.documentElement.style
        .setProperty('--scroll-bar-color', '#2F3136');
        document.documentElement.style
        .setProperty('--primary-loader-color', 'rgba(255, 255, 255, 0.2)');
        document.documentElement.style
        .setProperty('--secondary-loader-color', '#ffffff');
        document.documentElement.style
        .setProperty('--gas-input-color', '#ffffff');
        halfTimeSets.classList.add("dropdown-menu-dark");
        gasCombination.classList.add("dropdown-menu-dark");
        if (document.querySelector("#language-choice")) {
            document.querySelector("#language-choice").classList.add("dropdown-menu-dark");
        }
    }
}

halfTimeSets.addEventListener("click", function(e) {
    if(e.target && e.target.nodeName == "A") {
        halfTimeLabel.innerHTML = e.target.innerHTML;
        halfTimeLabel.value = e.target.innerHTML;
    }
});

gasCombination.addEventListener("click", function(e) {
    if(e.target && e.target.nodeName == "A") {
        gasLabel.innerHTML = e.target.innerHTML;
        gasLabel.value = e.target.innerHTML;

        if (gasLabel.innerHTML == selectedLanguage.custom)
        {
            showCustomGasSettings();
        }
        else
        {
            hideCustomGasSettings();
        }
    }
});

function showCustomGasSettings() {
    gasOptions.isAirSelected = false;
    //Display the custom gas input settings.
    customGasInput.style.opacity = '1'
    //Enable all elements in the gas input div.
    var nodes = document.getElementsByClassName('gas-input');
    for(var i = 0; i < nodes.length; i++){
        nodes[i].disabled = false;
    }
    if (document.querySelector("#gas-table-container") != null)
    {
        document.querySelector("#gas-table").style.opacity = '1'
    }
}

function hideCustomGasSettings() {
    gasOptions.isAirSelected = true;
    //Hide the custom gas input settings.
    customGasInput.style.opacity = '0.2'

    //Disable all elements in the gas input div.
    var nodes = document.getElementsByClassName('gas-input');
    for(var i = 0; i < nodes.length; i++){
        nodes[i].disabled = true;
    }
    if (document.querySelector("#gas-table-container") != null)
    {
        document.querySelector("#gas-table").style.opacity = '0.2'
    }
}


function loadDisplaySettings() {
    ipcRenderer.send('readDisplaySettings');
}

function writeDisplaySettings() {
    ipcRenderer.send('writeDisplaySettings', JSON.stringify(displaySettings));
}

ipcRenderer.on('receiveDisplaySettings', (event, settings) => {
    displaySettings = JSON.parse(settings);
    currentLanguage = displaySettings.language; 
    changeTheme();
    setTimeout(changeGUILanguage, 50);
});

ipcRenderer.on('receiveLanguageFile', (event, languages) => {
    languageList = (JSON.parse(languages));
});

function loadLanguages()
{  
    ipcRenderer.send('readLanguageFile');
}

function changeGUILanguage()
{    
    //Change all labels on the frontend.
    if(languageList != null && languageList != null && languageList.hasOwnProperty(currentLanguage))
    {
        selectedLanguage = languageList[currentLanguage];
    }
    else{
        selectedLanguage = English;
    }
    runBtnLabel.innerHTML = selectedLanguage.run;
    uploadBtnLabel.innerHTML = selectedLanguage.upload_files;

    if (fileInput.files.length == 0) {
        folderLabel.innerHTML = selectedLanguage.no_files_uploaded;
    }
    saveBtnLabel.innerHTML = selectedLanguage.save_as;
    advancedSettingsButton.title = selectedLanguage.settings;
    toggleGradientFactorLabel();
    toggleAdditionalCPValuesLabel();
    gasLabel.innerHTML = selectedLanguage.gas_combinations;
    customLabel.innerHTML = selectedLanguage.custom;
    airLabel.innerHTML = selectedLanguage.air;
    addGasButtonLabel.innerHTML = selectedLanguage.add_gas;
    startTimeLabel.innerHTML = selectedLanguage.start_time;
    halfTimeLabel.innerHTML = selectedLanguage.half_time_sets;
    updateErrorMessages();
    
}

gfToggle.addEventListener("click", function (e) {
    if (gfLabel.innerText.match(": ON")) {
        gfLabel.innerText =  selectedLanguage.gradient_factor + ": OFF";
    }
    else {
        gfLabel.innerText = selectedLanguage.gradient_factor + ": ON";
    }
});

function toggleGradientFactorLabel()
{
    if (gfLabel.innerText.match(": ON")) {
        gfLabel.innerText = selectedLanguage.gradient_factor + ": ON";
    }
    else {
        gfLabel.innerText = selectedLanguage.gradient_factor + ": OFF";
    }
}

cpToggle.addEventListener("click", function (e) {
    if (cpLabel.innerText.match(": ON")) {
        cpLabel.innerText = selectedLanguage.additional_cp_value + ": OFF";
    }
    else {
        cpLabel.innerText = selectedLanguage.additional_cp_value + ": ON";
    }
});

function toggleAdditionalCPValuesLabel()
{
    if (cpLabel.innerText.match(": ON")) {
        cpLabel.innerText = selectedLanguage.additional_cp_value + ": ON";
    }
    else {
        cpLabel.innerText = selectedLanguage.additional_cp_value + ": OFF";
    }
}

function updateErrorMessages()
{
    errorMessages.noUpload = selectedLanguage.error_message_1;
    errorMessages.noOutput = selectedLanguage.error_message_2;
    errorMessages.startTime = selectedLanguage.error_message_3;
    errorMessages.fillAllGases = selectedLanguage.error_message_4;
    errorMessages.gasTotal = selectedLanguage.error_message_5;
    errorMessages.oxygenNonZero = selectedLanguage.error_message_6;
}
const fileInput = document.getElementById("input-file");
const uploadBtn = document.getElementById("upload-btn");
const filePath = document.getElementById("file-viewer-text");
const fileViwerList = document.getElementById("file-viewer-list");
const fileViewFolderName = document.getElementById("folder-label");
mdc.ripple.MDCRipple.attachTo(document.getElementById("run-btn"));
mdc.ripple.MDCRipple.attachTo(document.getElementById("advanced-settings-btn"));
mdc.ripple.MDCRipple.attachTo(document.getElementById("upload-btn"));
mdc.ripple.MDCRipple.attachTo(document.getElementById("save-as-btn"));
mdc.ripple.MDCRipple.attachTo(document.getElementById("half-time-btn"));
mdc.ripple.MDCRipple.attachTo(document.getElementById("gas-btn"));
mdc.ripple.MDCRipple.attachTo(document.getElementById("add-gas-btn"));
mdc.ripple.MDCRipple.attachTo(document.getElementById("gf-btn"));
mdc.ripple.MDCRipple.attachTo(
    document.getElementById("additional-cp-values-btn")
);

uploadBtn.addEventListener("click", () => {
    uploadFile();
});

fileInput.addEventListener("change", () => {
    try {
        displayFilePath();
    } catch (error) {
        swal("There was an error uploading files. You may need to restart the application.");
        console.log(error)
    }
});

function uploadFile() {
    fileInput.click();
}

function displayFilePath() {
    if (fileInput) {
        updateFilePaths();

        if (fileInput.files.length === 0){
            return;
        } else if (fileInput.files.length > 1300) {
            return;
        }
        //First clear the list.
        while (fileViwerList.firstChild) {
            fileViwerList.removeChild(fileViwerList.firstChild);
        }

        //Set the folder name.
        var directory = fileInput.files[0].path;
        var pathElements = directory.replace(/\/$/, "").split("\\");
        var lastFolder = pathElements[pathElements.length - 2];
        fileViewFolderName.textContent = lastFolder;

        //Populate the list with file names.
        for (file of fileInput.files) {
            let newPath = document.createElement("li");
            newPath.innerHTML = file.path.match(/[\/\\]([\w\d\s\.\-\(\)]+)$/)[1]; //fileInput.value.match(/[\/\\]([\w\d\s\.\-\(\)]+)$/);
            fileViwerList.appendChild(newPath);
        }
        console.log("File Path: ", fileInput.files[0].path);
    } else {
        filePath.innerHTML = "No file chosen";
    }
}

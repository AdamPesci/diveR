---
# diveR 
---
# Authors
1. Alex Bugajewski
1. Adam Camer-Pesci
1. Augustine Italiano
1. Ryan Forster
1. Ryan Poli

# Development Initial Setup

## Prerequisites:
1. Python installed on machine.
1. Node/NPM installed on machine.
1. R installed on machine.
1. Git installed on machine.

#### Python
https://www.python.org/downloads/

*Note: Python must not be added through the microsoft store.*  
#### Node
https://nodejs.org/en/
#### R for Windows 
https://cran.r-project.org/bin/windows/base/
#### R for MacOS
https://cran.r-project.org/bin/macosx/
#### Git
https://git-scm.com/downloads

## Setup:
1. Download / Clone repository
2. Create and activate your python virtual environment described below.

### Windows
**Minimum requirements:**
1. Must have `python 3.9` correctly installed.
1. Must have `R 4.1.0` correctly installed.
1. Must have `git` correctly installed.
1. must have `node` correctly installed.

#### Installation
1. Click the `install.bat` file - this will set up the python virtual environment and install the node modules.
1. Click the `build.bat` file - this will compile the executable.
*Note: These files will be blocked on first use, click more info and run anyway.*

#### Exectution
1. Open the terminal and run `npm run start-dev` - this will run the app in development mode using the source code and not the built executable.
1. Open the terminal and run `npm run start` - this will run the app using the built executable.

#### Uninstallation
1. Click the `clean.bat` file - this will delete all directories and files made by the previous commands.

#### Errors
1. Please see troubleshooting section if you encounter any errors.

### MacOS/Linux Terminal
1. In the terminal, navigate to the base directory of this repo, then run: 
		python3 -m venv /path/to/env

        E.g. To create "env" in the current working directory: `python3 -m venv ./env`

1. Activate the Virtual Environment (note - this should be done each session): 
		$ source <venv>/bin/activate

1. Install Python/Pip Packages from requirements.txt (*NOTE* Ensure the virtual envronment is active)
		pip install -r requirements.txt
	*You may have issues here with rpy2 filepaths. More mentioned at end of this section.*

1. Install Node modules with NPM: 
   In the directory containing package-lock.json run: 
		npm install
   
1. Launch the software:
    With the venv active Run:
		npm start

## Troubleshooting

### General

#### Finding Errors

1. for OSError connot load library, the issue is likely python not being installed correctly (*see below*).
1. If the program asks you to use a personal library instead, try running the program in adminstrative mode.

#### Windows

##### Issues will likely arise if the user has not done the following
1. Installed python 3.9 correctly - *this must not be done through the microsoft store*.
1. Installed R 4.1.0 correctly.

##### Known problems / solutions
1. In the event that everything is installed correctly, the issue is likely to do with rpy2 not being able to save the scuba library.  
Open `cmd` in administrator mode and navigate to the directory containing the project.  
Ensure that the `install.bat` file has been used and in cmd type `npm start-dev`. This should allow rpy2 to save the scuba library. 

1. In the even that python has not been installed properly, uninstall python from your system through the control panel.  
Upon re-installation ensure that the PATH variable is set. (there should be a checkbox upon opening the python 3.9 installer).  
In the event that there is not a checkbox, the user will have to do a custom install and check the box allowing the PATH variable to be updated.

##### Rpy2 Installation
You may experience an issue regarding R not being on the path. The fix that worked for me (Alex) is setting an environment variable R_HOME, which should be the path to your R home directory.  
For me (on MacOS), this was `/Library/Frameworks/R.framework/Resources`.  
To find the correct filepath for you, open R/R-Studio and run the command `R.home()`. Then set the R_HOME variable to this filepath.   
To set environment variable on MacOS/Linux: `export R_HOME='/My/File/Path'`
---
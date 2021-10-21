const fs = require('fs')
const path = require('path')
const iconPath = path.join(__dirname, "src", "electronJS", "Resources", "icons", "win", "win_icon.ico");

module.exports = {
    "packagerConfig": {
        "icon": iconPath
    },
        "makers": [
          {
            "name": "@electron-forge/maker-squirrel",
            "config": {
                "setupIcon": iconPath,
                "name": "diveR",
            }
          },
          {
            "name": "@electron-forge/maker-zip",
            "platforms": [
              "darwin"
            ]
          },
          {
            "name": "@electron-forge/maker-deb",
            "config": {}
          },
          {
            "name": "@electron-forge/maker-rpm",
            "config": {}
          }
        ]
  }

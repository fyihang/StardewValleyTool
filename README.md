# Stardew Valley Save Manager

[简体中文](README.zh-CN.md)

A Windows desktop tool for safely reading and editing selected Stardew Valley save information.

## Safety model

- Uses `%appdata%\StardewValley\Saves`; no user-specific path is embedded in the program.
- A save is valid only when its directory contains both `SaveGameInfo` and the same-named main save file.
- Farmer name, farm name, favorite thing, and an existing horse name are updated in both XML files.
- Animal names are changed only in their existing main-save `FarmAnimal` records.
- Before every save, the tool copies both files to `.svt-backups/<UTC timestamp>/` inside the selected save directory.
- It validates temporary XML files before replacement, reads the result back afterward, and restores both originals if an error occurs.

Close Stardew Valley before editing a save. Test changes on a copied save first.

## Run from source

Python 3.11 or later is required. From PowerShell at the repository root:

```powershell
$env:PYTHONPATH = "src"
python -m stardew_save_manager
```

The language selector switches the running interface between English and Simplified Chinese.

## Release policy

Automated tests, the PyInstaller build script, build directories, and the `.exe` remain local during development. A release artifact will be published only after user testing has been completed successfully.

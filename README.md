# Stardew Valley Save Manager

[简体中文](README.zh-CN.md)

A Windows desktop application for viewing and safely editing selected Stardew Valley save details.

## Download

Download `StardewValleySaveManager.exe` from the latest [GitHub Release](https://github.com/fyihang/StardewValleyTool/releases). No Python installation is required for the release executable.

## What it can edit

- Farmer name
- Farm name
- Favorite thing
- Horse name, when the save contains one
- Names of existing farm animals

The interface is available in English and Simplified Chinese.

## Safe save handling

The application automatically searches the standard Windows directory:

```text
%appdata%\StardewValley\Saves
```

It recognises a save only when its folder contains both `SaveGameInfo` and the same-named main save file. Shared farmer information is updated in both files; animal names are changed only in the relevant main-save animal record.

Before writing, the application copies both files to `.svt-backups/<UTC timestamp>/` inside that save folder. It validates temporary XML files before replacement and checks the saved result afterward. If an error occurs during the transaction, it restores both original files from the backup.

## How to use

1. Close Stardew Valley completely.
2. Start `StardewValleySaveManager.exe`.
3. Select a save from the left-hand list.
4. Edit the desired fields or double-click an animal name to rename it.
5. Select **Save changes** and confirm that the game is closed.

For the first use, make an independent copy of a save folder and test changes there. Keep the generated `.svt-backups` directory until you have verified the edited save in game.

## Source code

To run from source, install Python 3.11 or later and execute:

```powershell
$env:PYTHONPATH = "src"
python src\__main__.py
```

## License

Distributed under the [MIT License](LICENSE).

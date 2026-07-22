# Stardew Valley Tool

[简体中文](README.zh.md) | [Português](README.pt.md) | [Español](README.es.md) | [日本語](README.jp.md)

A Windows desktop application for inspecting and safely editing selected Stardew Valley save details. It works with the standard Windows save location and does not require Python when using the release executable.

## Download

Download `StardewValleySaveManager.exe` from the latest [GitHub Release](https://github.com/fyihang/StardewValleyTool/releases). No Python installation is required for the release executable.

## What it can edit

- Farmer name
- Farm name
- Favorite thing
- Names of existing animals, including the horse when present
- Existing farmhand names and favourite things through a selector (farm name remains an owner-only setting)

The interface is available in English, Simplified Chinese, Portuguese, Spanish, and Japanese. Animal types are translated in the selected interface language, while unknown modded animal types remain visible as their original in-game values.

Use **About** in the lower-left corner to view the author, repository, and installed version, or to open their corresponding GitHub pages.

## Safe save handling

The application starts by searching the standard Windows directory:

```text
%appdata%\StardewValley\Saves
```

Use **Choose save directory** to select a different save root for the current session. The choice is not saved and the next launch starts from the standard directory again.

It recognises a save only when its folder contains both `SaveGameInfo` and the same-named main save file. Owner information shared by the two files is updated in both of them. Farmhands and animals are edited only in the main save, where those records are stored.

Before writing, the application copies both files to `.svt-backups/<UTC timestamp>/` inside that save folder. It validates temporary XML files before replacement and checks the saved result afterward. If an error occurs during the transaction, it restores both original files from the backup.

## How to use

1. Close Stardew Valley completely.
2. Start `StardewValleySaveManager.exe`.
3. Select a save from the left-hand list.
4. Edit the owner fields, choose a farmhand when available, or double-click an animal name to rename it.
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

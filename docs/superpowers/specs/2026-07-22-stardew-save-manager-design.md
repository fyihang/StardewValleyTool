# Stardew Valley Save Manager Design

## Purpose

Build a Windows desktop application that reads and safely edits selected Stardew Valley save information. The application targets the standard Windows save root `%appdata%\\StardewValley\\Saves` and operates on one save-directory at a time.

## Scope

The first release shall display and edit these values:

- Farmer name (`name`)
- Farm name (`farmName`)
- Favorite thing (`favoriteThing`)
- Horse name (`horseName`), when present
- Animal names found in the main save file

The program shall list every direct child directory of the save root as a candidate save. A candidate is valid only when it contains both `SaveGameInfo` and a main save file whose name equals the directory name.

## Architecture

The application uses Python 3.11+ and Tkinter. Its source code is separated into a save-domain service, an XML text-patching service, an i18n service, and a thin Tkinter user interface. Domain services are independent of the GUI so that automated tests can exercise them with temporary fixture directories.

The save-domain service reads the summary file `SaveGameInfo` and the same-named main save file. Shared farmer fields are read from both files and presented only when their values agree. Animal data is read only from the main save, because it belongs to the farm/world state.

## Safe Write Transaction

1. The user must confirm that Stardew Valley is closed. The interface provides a warning but does not attempt to terminate the game.
2. Before changing a file, the program copies `SaveGameInfo` and the main save file into `<save directory>\\.svt-backups\\<UTC timestamp>\\`.
3. The application parses both files as XML and checks that the requested XML element exists in every file that must be changed. Optional missing fields, including a missing horse name, are reported and are never created automatically.
4. The program changes only text values of the selected XML elements. It preserves the remainder of each file by replacing the exact XML text span rather than serializing a new XML tree.
5. Updated content is written to temporary files in the same directory. Each temporary file is parsed again and its requested fields are checked.
6. Only after all temporary files validate are they atomically replaced into their original paths. A failed replacement restores every original from the backup and reports the failure.
7. The program re-reads both saved files and verifies that synchronized values are identical and equal to the requested values.

No operation edits a file outside the selected save directory. No operation changes unknown XML fields, XML element ordering, comments, encoding declaration, or unrelated whitespace.

## Animal Editing

The application identifies animal records in the main save by their object structure and presents each existing animal by species and name. Renaming an animal changes only the `name` element within that selected animal record. Duplicate names remain separate records and are addressed by their stable ordinal position in the loaded list. The program does not add, remove, transfer, or otherwise alter animals.

## User Interface

The UI contains:

- A save list with a refresh control and an indication for invalid/incomplete save directories.
- A details pane containing editable text fields for the farmer, farm, favorite thing, and optional horse.
- An animal table with an editable name column.
- A language selection control.
- A save button, backup path/status display, error dialogs, and a final success dialog listing the verified fields.

The UI prevents saving without a selected valid save or when no field has changed. It presents parse errors and synchronization mismatches as actionable errors rather than guessing a value.

## Internationalization

All visible strings are translation keys resolved by an i18n service. `i18n/default.json` is the authoritative English resource. `i18n/zh.json` contains the equivalent Simplified Chinese translations with the same keys. The user can change language while the application is running; then all static controls and messages refresh without changing loaded save data.

## Repository and Delivery Policy

The public GitHub repository is `fyihang/StardewValleyTool` under the MIT License. Source code, i18n resources, documentation, and `.gitignore` are committed and pushed at meaningful implementation boundaries. The final `README.md` describes installation, safe-edit behavior, language selection, and recovery from a backup.

Automated tests, PyInstaller build scripts, build artifacts, and the generated single-file `.exe` remain local during development and are excluded by `.gitignore`. After the user tests the executable successfully, the user may authorize publishing those selected artifacts to a GitHub Release.

## Testing and Acceptance Criteria

Tests use temporary representative XML files and verify:

- Save-directory discovery and valid-pair detection.
- Reading the requested fields from both files and detection of disagreement.
- Exact replacement of requested text while unrelated XML text remains unchanged.
- Synchronized update of shared farmer fields in both files.
- Main-file-only update of a selected animal name.
- Backup creation, post-write XML validation, and restoration after a simulated failure.
- English and Chinese translation resources have exactly matching keys.

Acceptance requires a successful local test run, a successful PyInstaller build, and a manual executable check against a copied save before the executable is uploaded to a GitHub Release.

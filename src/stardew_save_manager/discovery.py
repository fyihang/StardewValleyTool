import os
from pathlib import Path

from .models import SavePaths


def default_save_root(appdata: str | None = None) -> Path:
    return Path(appdata if appdata is not None else os.environ["APPDATA"]) / "StardewValley" / "Saves"


def discover_saves(root: Path) -> tuple[SavePaths, ...]:
    if not root.is_dir():
        return ()
    found = []
    for directory in sorted((item for item in root.iterdir() if item.is_dir()), key=lambda item: item.name.casefold()):
        info, main = directory / "SaveGameInfo", directory / directory.name
        if info.is_file() and main.is_file():
            found.append(SavePaths(directory, info, main))
    return tuple(found)

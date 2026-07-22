from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Animal:
    index: int
    species: str
    name: str


@dataclass(frozen=True)
class SaveData:
    farmer_name: str
    farm_name: str
    favorite_thing: str
    horse_name: str | None
    animals: tuple[Animal, ...]


@dataclass(frozen=True)
class SavePaths:
    directory: Path
    info_file: Path
    main_file: Path

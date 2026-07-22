from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Animal:
    index: int
    species: str
    name: str
    record_id: str | None = None
    kind: str = "animal"


@dataclass(frozen=True)
class Farmhand:
    index: int
    farmer_name: str
    farm_name: str
    favorite_thing: str


@dataclass(frozen=True)
class SaveData:
    farmer_name: str
    farm_name: str
    favorite_thing: str
    horse_name: str | None
    animals: tuple[Animal, ...]
    farmhands: tuple[Farmhand, ...] = ()


@dataclass(frozen=True)
class SavePaths:
    directory: Path
    info_file: Path
    main_file: Path

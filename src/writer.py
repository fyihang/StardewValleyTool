import shutil
import tempfile
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET

from models import SaveData, SavePaths
from reader import load_save
from xml_patch import replace_element_text


class SaveWriteError(RuntimeError):
    pass


def _patch_farmer(xml: str, updated: SaveData) -> str:
    for element, value in (("name", updated.farmer_name), ("farmName", updated.farm_name), ("favoriteThing", updated.favorite_thing)):
        xml = replace_element_text(xml, element, value)
    if updated.horse_name is not None:
        xml = replace_element_text(xml, "horseName", updated.horse_name)
    return xml


def _patch_animals(xml: str, original: SaveData, updated: SaveData) -> str:
    for old, new in zip(original.animals, updated.animals, strict=True):
        if old.name == new.name or old.kind == "horse":
            continue
        starts: list[int] = []
        search_at = 0
        while (start := xml.find("<FarmAnimal", search_at)) >= 0:
            starts.append(start); search_at = start + 1
        targets = starts if old.record_id is not None else [starts[old.index]]
        offset = 0
        for start in targets:
            start += offset; end = xml.find("</FarmAnimal>", start)
            if end < 0:
                raise SaveWriteError("Malformed animal record")
            section = xml[start:end + len("</FarmAnimal>")]
            if old.record_id is not None and f"<myID>{old.record_id}</myID>" not in section:
                continue
            replacement = replace_element_text(section, "name", new.name)
            xml = xml[:start] + replacement + xml[end + len("</FarmAnimal>"):]
            offset += len(replacement) - len(section)
    return xml


def _patch_farmhands(xml: str, original: SaveData, updated: SaveData) -> str:
    for old, new in zip(original.farmhands, updated.farmhands, strict=True):
        if old == new:
            continue
        start = -1; search_at = 0
        for _ in range(old.index + 1):
            start = xml.find("<Farmer", search_at)
            if start < 0:
                raise SaveWriteError("Farmhand record no longer exists")
            search_at = start + 1
        end = xml.find("</Farmer>", start)
        if end < 0:
            raise SaveWriteError("Malformed farmhand record")
        section = xml[start:end + len("</Farmer>")]
        for element, value in (("name", new.farmer_name), ("farmName", new.farm_name), ("favoriteThing", new.favorite_thing)):
            section = replace_element_text(section, element, value)
        xml = xml[:start] + section + xml[end + len("</Farmer>"):]
    return xml


def save_changes(paths: SavePaths, original: SaveData, updated: SaveData) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup = paths.directory / ".svt-backups" / stamp
    backup.mkdir(parents=True)
    for file in (paths.info_file, paths.main_file):
        shutil.copy2(file, backup / file.name)
    try:
        info = _patch_farmer(paths.info_file.read_text(encoding="utf-8"), updated)
        main = _patch_farmhands(_patch_animals(_patch_farmer(paths.main_file.read_text(encoding="utf-8"), updated), original, updated), original, updated)
        temporary = []
        for target, content in ((paths.info_file, info), (paths.main_file, main)):
            handle = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, dir=target.parent, suffix=".tmp")
            with handle:
                handle.write(content)
            candidate = Path(handle.name)
            ET.parse(candidate)
            temporary.append((target, candidate))
        for target, candidate in temporary:
            candidate.replace(target)
        if load_save(paths) != updated:
            raise SaveWriteError("Post-write validation failed")
        return backup
    except Exception as error:
        for file in (paths.info_file, paths.main_file):
            source = backup / file.name
            if source.exists():
                shutil.copy2(source, file)
        raise SaveWriteError(str(error)) from error

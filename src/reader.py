import xml.etree.ElementTree as ET

from models import Animal, SaveData, SavePaths


class SaveConsistencyError(ValueError):
    pass


def _text(parent: ET.Element, field: str, optional: bool = False) -> str | None:
    node = parent.find(field)
    if node is None:
        if optional:
            return None
        raise SaveConsistencyError(f"Missing required field: {field}")
    return node.text or ""


def _farmer(root: ET.Element) -> ET.Element:
    player = root.find("player")
    return player if player is not None else root


def load_save(paths: SavePaths) -> SaveData:
    info_root, main_root = ET.parse(paths.info_file).getroot(), ET.parse(paths.main_file).getroot()
    info_farmer, main_farmer = _farmer(info_root), _farmer(main_root)
    shared = {}
    for field in ("name", "farmName", "favoriteThing"):
        left, right = _text(info_farmer, field), _text(main_farmer, field)
        if left != right:
            raise SaveConsistencyError(f"Mismatched field: {field}")
        shared[field] = left
    left_horse, right_horse = _text(info_farmer, "horseName", True), _text(main_farmer, "horseName", True)
    if left_horse != right_horse:
        raise SaveConsistencyError("Mismatched field: horseName")
    animals = tuple(Animal(index, _text(node, "type") or "Unknown", _text(node, "name") or "") for index, node in enumerate(main_root.iter("FarmAnimal")))
    return SaveData(shared["name"], shared["farmName"], shared["favoriteThing"], left_horse, animals)

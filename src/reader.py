import xml.etree.ElementTree as ET

from models import Animal, Farmhand, SaveData, SavePaths


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
    animals: list[Animal] = []
    seen_ids: set[str] = set()
    for index, node in enumerate(main_root.iter("FarmAnimal")):
        record_id = _text(node, "myID", True)
        dedupe_key = record_id or f"occurrence:{index}"
        if dedupe_key in seen_ids:
            continue
        seen_ids.add(dedupe_key)
        animals.append(Animal(index, _text(node, "type") or "Unknown", _text(node, "name") or "", record_id))
    if left_horse is not None:
        animals.append(Animal(-1, "Horse", left_horse, kind="horse"))
    farmhand_root = main_root.find("farmhands")
    farmhand_nodes = () if farmhand_root is None else tuple(farmhand_root.findall("Farmer"))
    farmhands = []
    for index, node in enumerate(farmhand_nodes):
        name = _text(node, "name", True) or ""
        if not name:
            continue
        farmhands.append(Farmhand(index, name, _text(node, "farmName", True) or shared["farmName"], _text(node, "favoriteThing", True) or ""))
    return SaveData(shared["name"], shared["farmName"], shared["favoriteThing"], left_horse, tuple(animals), tuple(farmhands))

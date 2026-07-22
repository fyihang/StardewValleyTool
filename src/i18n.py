import json
from pathlib import Path

LANGUAGES = (
    ("en", "English"),
    ("zh", "中文"),
    ("pt", "Português"),
    ("es", "Español"),
    ("jp", "日本語"),
)


class Translator:
    def __init__(self, resource_dir: Path, language: str = "en"):
        self.resource_dir = resource_dir
        self.default = self._load("default")
        self.current = self.default
        self.set_language(language)

    def _load(self, language: str) -> dict[str, str]:
        with (self.resource_dir / f"{language}.json").open(encoding="utf-8") as source:
            return json.load(source)

    def set_language(self, language: str) -> None:
        if language == "en":
            self.current = self.default
            return
        candidate = self._load(language)
        if set(candidate) != set(self.default):
            raise ValueError("Translation keys do not match default.json")
        self.current = candidate

    def text(self, key: str, **values: str) -> str:
        try:
            return self.current[key].format(**values)
        except KeyError as error:
            raise KeyError(f"Unknown translation key: {key}") from error

    def animal_type(self, type_name: str) -> str:
        return self.current.get(f"animal.type.{type_name}", type_name)

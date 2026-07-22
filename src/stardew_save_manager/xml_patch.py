import re
from xml.sax.saxutils import escape


def replace_element_text(xml: str, element: str, replacement: str, occurrence: int = 0) -> str:
    pattern = re.compile(rf"(<{re.escape(element)}(?:\s[^>]*)?>)(.*?)(</{re.escape(element)}>)", re.DOTALL)
    matches = list(pattern.finditer(xml))
    if occurrence < 0 or occurrence >= len(matches):
        raise ValueError(f"Element occurrence not found: {element}[{occurrence}]")
    match = matches[occurrence]
    return xml[:match.start(2)] + escape(replacement) + xml[match.end(2):]

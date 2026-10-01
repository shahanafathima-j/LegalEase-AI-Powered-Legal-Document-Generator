import re


def sanitize_text(text: str) -> str:
    """Normalize AI output for document-generation libraries."""
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2022": "-",
        "\u00a0": " ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_sections(text: str):
    """Return non-empty paragraphs/sections for export formatting."""
    clean = sanitize_text(text)
    return [part.strip() for part in re.split(r"\n\s*\n", clean) if part.strip()]

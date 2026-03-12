from pathlib import Path

from pypdf import PdfReader


# read transcript text from a pdf file
def read_pdf(file_path: Path) -> str:
    reader = PdfReader(str(file_path))
    parts: list[str] = []

    for page in reader.pages:
        text = page.extract_text() or ""
        text = text.strip()

        if text:
            parts.append(text)

    return "\n".join(parts)
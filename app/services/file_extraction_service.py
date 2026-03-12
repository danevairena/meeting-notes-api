from pathlib import Path

from app.utils.docx_reader import read_docx
from app.utils.pdf_reader import read_pdf


# extract transcript text from a supported uploaded file
def extract_transcript(file_path: Path) -> str:
    suffix = file_path.suffix.lower()

    if suffix == ".docx":
        return read_docx(file_path)

    if suffix == ".pdf":
        return read_pdf(file_path)

    raise ValueError(f"unsupported file type: {suffix}")
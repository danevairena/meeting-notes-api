import pytest

from app.utils.google_docs import extract_google_doc_id


def test_extract_google_doc_id_from_valid_url():
    # extract the id from a standard google docs edit url
    url = "https://docs.google.com/document/d/abc123_DEF-456/edit"
    result = extract_google_doc_id(url)

    assert result == "abc123_DEF-456"


def test_extract_google_doc_id_from_url_without_edit_suffix():
    # support urls that end right after the document id
    url = "https://docs.google.com/document/d/abc123_DEF-456"
    result = extract_google_doc_id(url)

    assert result == "abc123_DEF-456"


def test_extract_google_doc_id_raises_for_invalid_url():
    # reject non google docs document urls
    url = "https://docs.google.com/spreadsheets/d/abc123_DEF-456/edit"

    with pytest.raises(ValueError, match="invalid google docs url"):
        extract_google_doc_id(url)
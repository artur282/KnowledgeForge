"""Tests for document parsers."""

from knowledgeforge.ingestion.parsers import DocumentType, compute_hash, detect_type, parse_document


def test_detect_pdf():
    assert detect_type("report.pdf") == DocumentType.PDF


def test_detect_markdown():
    assert detect_type("notes.md") == DocumentType.MARKDOWN
    assert detect_type("notes.markdown") == DocumentType.MARKDOWN


def test_detect_html():
    assert detect_type("page.html") == DocumentType.HTML
    assert detect_type("page.htm") == DocumentType.HTML


def test_detect_text():
    assert detect_type("notes.txt") == DocumentType.TEXT
    assert detect_type("unknown.xyz") == DocumentType.TEXT


def test_compute_hash():
    h1 = compute_hash(b"hello")
    h2 = compute_hash(b"hello")
    h3 = compute_hash(b"world")
    assert h1 == h2
    assert h1 != h3
    assert len(h1) == 64


def test_parse_text():
    content = b"Plain text content"
    result = parse_document(content, "notes.txt")
    assert result == "Plain text content"


def test_parse_markdown():
    content = b"# Heading\n\nSome **bold** text"
    result = parse_document(content, "notes.md")
    assert result == "# Heading\n\nSome **bold** text"

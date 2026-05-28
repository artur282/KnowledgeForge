"""Document parsers for PDF, Markdown, and HTML files."""

import hashlib
import os
import tempfile
from enum import Enum

from langchain_community.document_loaders import PyPDFLoader, UnstructuredHTMLLoader


class DocumentType(Enum):
    """Supported document types."""

    PDF = "pdf"
    MARKDOWN = "md"
    HTML = "html"
    TEXT = "txt"


def detect_type(filename: str) -> DocumentType:
    """Detect document type from filename extension."""
    ext = filename.rsplit(".", 1)[-1].lower()
    mapping = {
        "pdf": DocumentType.PDF,
        "md": DocumentType.MARKDOWN,
        "markdown": DocumentType.MARKDOWN,
        "html": DocumentType.HTML,
        "htm": DocumentType.HTML,
        "txt": DocumentType.TEXT,
    }
    return mapping.get(ext, DocumentType.TEXT)


def compute_hash(content: bytes) -> str:
    """Compute SHA-256 hash for deduplication."""
    return hashlib.sha256(content).hexdigest()


def parse_document(file_bytes: bytes, filename: str) -> str:
    """Parse a document and return its text content."""
    doc_type = detect_type(filename)

    if doc_type == DocumentType.PDF:
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                f.write(file_bytes)
                tmp_path = f.name
            docs = PyPDFLoader(tmp_path).load()
            return "\n\n".join(doc.page_content for doc in docs)
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)

    if doc_type == DocumentType.HTML:
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="wb") as f:
                f.write(file_bytes)
                tmp_path = f.name
            docs = UnstructuredHTMLLoader(tmp_path).load()
            return "\n\n".join(doc.page_content for doc in docs)
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)

    text = file_bytes.decode("utf-8")
    return text

"""Tests for hybrid search service."""

from uuid import uuid4

from knowledgeforge.search.services import RRF_K, HybridSearchService


def test_rrf_fusion_basic():
    """RRF fusion combines results from both sources."""
    service = HybridSearchService(None, None)

    doc_id = uuid4()
    bm25 = [
        {
            "doc_id": doc_id,
            "chunk_index": 0,
            "content": "BM25 result",
            "score": 0.9,
            "filename": "test.pdf",
            "metadata": {},
        },
    ]
    semantic = [
        {
            "doc_id": doc_id,
            "chunk_index": 0,
            "content": "Semantic result",
            "score": 0.85,
            "filename": "test.pdf",
            "metadata": {},
        },
    ]

    results = service._rrf_fusion(bm25, semantic)
    assert len(results) == 1
    assert results[0].doc_id == doc_id
    expected_score = round(1.0 / (RRF_K + 1) + 1.0 / (RRF_K + 1), 6)
    assert results[0].score == expected_score


def test_rrf_fusion_different_results():
    """RRF fusion handles non-overlapping results."""
    service = HybridSearchService(None, None)

    doc1 = uuid4()
    doc2 = uuid4()
    bm25 = [
        {
            "doc_id": doc1,
            "chunk_index": 0,
            "content": "BM25 only",
            "score": 0.9,
            "filename": "test.pdf",
            "metadata": {},
        },
    ]
    semantic = [
        {
            "doc_id": doc2,
            "chunk_index": 0,
            "content": "Semantic only",
            "score": 0.85,
            "filename": "test.pdf",
            "metadata": {},
        },
    ]

    results = service._rrf_fusion(bm25, semantic)
    assert len(results) == 2
    assert results[0].doc_id == doc1
    assert results[1].doc_id == doc2


def test_rrf_fusion_empty_lists():
    """RRF fusion handles empty input."""
    service = HybridSearchService(None, None)
    results = service._rrf_fusion([], [])
    assert results == []


def test_rrf_fusion_preserves_content():
    """RRF fusion preserves result content."""
    service = HybridSearchService(None, None)

    doc_id = uuid4()
    bm25 = [
        {
            "doc_id": doc_id,
            "chunk_index": 0,
            "content": "Test content",
            "score": 0.9,
            "filename": "test.pdf",
            "metadata": {"page": 1},
        },
    ]

    results = service._rrf_fusion(bm25, [])
    assert len(results) == 1
    assert results[0].content == "Test content"
    assert results[0].filename == "test.pdf"
    assert results[0].metadata == {"page": 1}

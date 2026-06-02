import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from scripts.search import ArxivSearcher, Paper, search_papers


@pytest.fixture
def sample_strategy():
    return {
        "topic": "transformer attention mechanism",
        "keywords": ["attention", "transformer", "self-attention"],
        "exclude": ["survey"],
        "max_results": 10
    }


@pytest.fixture
def sample_arxiv_response():
    return """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2401.00001v1</id>
    <title>Attention Is All You Need</title>
    <author><name>John Doe</name></author>
    <author><name>Jane Smith</name></author>
    <summary>We propose a new attention mechanism...</summary>
    <published>2024-01-01T00:00:00Z</published>
    <link href="http://arxiv.org/abs/2401.00001v1" rel="alternate"/>
    <link href="http://arxiv.org/pdf/2401.00001v1" rel="related" type="application/pdf"/>
  </entry>
</feed>"""


@pytest.mark.asyncio
async def test_arxiv_searcher_parse_response(sample_strategy, sample_arxiv_response):
    """Test parsing ArXiv XML response."""
    searcher = ArxivSearcher()
    papers = searcher._parse_response(sample_arxiv_response)

    assert len(papers) == 1
    assert papers[0].id == "arxiv:2401.00001v1"
    assert papers[0].title == "Attention Is All You Need"
    assert papers[0].authors == ["John Doe", "Jane Smith"]
    assert papers[0].source == "arxiv"
    assert papers[0].date == "2024-01-01"


@pytest.mark.asyncio
async def test_arxiv_searcher_build_query(sample_strategy):
    """Test building ArXiv search query."""
    searcher = ArxivSearcher()
    query = searcher._build_query(sample_strategy)

    assert "attention" in query
    assert "transformer" in query


@pytest.fixture
def sample_semantic_scholar_response():
    return {
        "data": [
            {
                "paperId": "abc123def456",
                "title": "Efficient Transformers: A Survey",
                "authors": [{"name": "Alice Johnson"}, {"name": "Bob Wilson"}],
                "abstract": "This paper surveys efficient transformer architectures...",
                "url": "https://www.semanticscholar.org/paper/abc123def456",
                "year": 2024,
                "citationCount": 150,
                "externalIds": {"ArXiv": "2401.00002"}
            }
        ],
        "total": 1,
        "offset": 0
    }


@pytest.mark.asyncio
async def test_semantic_scholar_parse_response(sample_semantic_scholar_response):
    """Test parsing Semantic Scholar JSON response."""
    from scripts.search import SemanticScholarSearcher

    searcher = SemanticScholarSearcher()
    papers = searcher._parse_response(sample_semantic_scholar_response)

    assert len(papers) == 1
    assert papers[0].id == "semantic_scholar:abc123def456"
    assert papers[0].title == "Efficient Transformers: A Survey"
    assert papers[0].authors == ["Alice Johnson", "Bob Wilson"]
    assert papers[0].source == "semantic_scholar"
    assert papers[0].citation_count == 150
    assert papers[0].date == "2024"


@pytest.fixture
def sample_google_scholar_response():
    return {
        "organic_results": [
            {
                "result_id": "xyz789",
                "title": "BERT: Pre-training of Deep Bidirectional Transformers",
                "link": "https://arxiv.org/abs/1810.04805",
                "snippet": "We introduce a new language representation model called BERT...",
                "publication_info": {
                    "authors": [{"name": "Jacob Devlin"}, {"name": "Ming-Wei Chang"}],
                    "summary": "Published 2019"
                },
                "inline_links": {
                    "serpapi_cite_link": "https://scholar.google.com/citations?xyz789"
                }
            }
        ]
    }


@pytest.mark.asyncio
async def test_google_scholar_parse_response(sample_google_scholar_response):
    """Test parsing Google Scholar response."""
    from scripts.search import GoogleScholarSearcher

    searcher = GoogleScholarSearcher()
    papers = searcher._parse_response(sample_google_scholar_response)

    assert len(papers) == 1
    assert papers[0].id == "google_scholar:xyz789"
    assert papers[0].title == "BERT: Pre-training of Deep Bidirectional Transformers"
    assert papers[0].source == "google_scholar"
    assert "Jacob Devlin" in papers[0].authors

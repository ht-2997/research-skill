import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from scripts.screen import ScreenResult, classify_paper, score_papers


@pytest.fixture
def sample_paper():
    return {
        "id": "arxiv:2401.00001v1",
        "title": "Attention Is All You Need",
        "authors": ["John Doe"],
        "abstract": "We propose a new attention mechanism...",
        "source": "arxiv",
        "url": "http://arxiv.org/abs/2401.00001v1",
        "date": "2024-01-01"
    }


@pytest.fixture
def sample_strategy():
    return {
        "topic": "transformer attention",
        "keywords": ["attention", "transformer"],
        "exclude": ["survey"]
    }


@pytest.fixture
def sample_config():
    class MockModel:
        base_url = "https://integrate.api.nvidia.com/v1"
        api_key = "test-key"
        model_name = "test-model"

    class MockConfig:
        model = MockModel()
        dimensions = [
            {"name": "relevance", "description": "与搜索策略的相关程度"},
            {"name": "novelty", "description": "方法或视角的新颖性"}
        ]

    return MockConfig()


@pytest.mark.asyncio
async def test_classify_paper_returns_label(sample_paper, sample_strategy, sample_config):
    """Test that classify_paper returns a valid label."""
    mock_response = {
        "choices": [{
            "message": {
                "content": "relevant\n\nThis paper directly addresses attention mechanisms."
            }
        }]
    }

    with patch("scripts.screen.call_llm", new_callable=AsyncMock, return_value=mock_response):
        result = await classify_paper(sample_paper, sample_strategy, sample_config)

    assert result.label in ["relevant", "possibly_relevant", "irrelevant"]
    assert result.reasoning != ""


@pytest.mark.asyncio
async def test_classify_paper_handles_irrelevant(sample_paper, sample_strategy, sample_config):
    """Test classification of irrelevant paper."""
    mock_response = {
        "choices": [{
            "message": {
                "content": "irrelevant\n\nThis paper is about computer vision, not attention mechanisms."
            }
        }]
    }

    with patch("scripts.screen.call_llm", new_callable=AsyncMock, return_value=mock_response):
        result = await classify_paper(sample_paper, sample_strategy, sample_config)

    assert result.label == "irrelevant"


@pytest.mark.asyncio
async def test_score_papers_returns_scores(sample_paper, sample_strategy, sample_config):
    """Test that score_papers returns scores for each dimension."""
    mock_response = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "scores": {"relevance": 8, "novelty": 7},
                    "overall": 7.5,
                    "summary": "This paper proposes a novel attention mechanism."
                })
            }
        }]
    }

    papers = [sample_paper]
    classify_results = [
        ScreenResult(paper_id=sample_paper["id"], label="relevant", reasoning="Directly relevant")
    ]

    with patch("scripts.screen.call_llm", new_callable=AsyncMock, return_value=mock_response):
        results = await score_papers(papers, classify_results, sample_strategy, sample_config)

    assert len(results) == 1
    assert results[0].scores["relevance"] == 8
    assert results[0].scores["novelty"] == 7
    assert results[0].overall == 7.5
    assert results[0].summary != ""


@pytest.mark.asyncio
async def test_score_papers_skips_irrelevant(sample_paper, sample_strategy, sample_config):
    """Test that scoring skips irrelevant papers."""
    papers = [sample_paper]
    classify_results = [
        ScreenResult(paper_id=sample_paper["id"], label="irrelevant", reasoning="Not relevant")
    ]

    results = await score_papers(papers, classify_results, sample_strategy, sample_config)

    assert len(results) == 0

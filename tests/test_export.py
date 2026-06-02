import pytest
import json
from scripts.export import export_papers, import_papers


@pytest.fixture
def sample_papers():
    return [
        {
            "id": "arxiv:2401.00001v1",
            "title": "Attention Is All You Need",
            "authors": ["John Doe"],
            "abstract": "We propose...",
            "source": "arxiv",
            "url": "http://arxiv.org/abs/2401.00001v1",
            "date": "2024-01-01",
            "label": "relevant",
            "scores": {"relevance": 9},
            "overall": 9.0,
            "summary": "Novel attention"
        }
    ]


def test_export_papers(sample_papers, tmp_path):
    """Test exporting papers to JSON file."""
    output_file = tmp_path / "export.json"
    export_papers(sample_papers, str(output_file))

    assert output_file.exists()

    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    assert "papers" in data
    assert "metadata" in data
    assert len(data["papers"]) == 1
    assert data["papers"][0]["id"] == "arxiv:2401.00001v1"
    assert "exported_at" in data["metadata"]


def test_import_papers(sample_papers, tmp_path):
    """Test importing papers from JSON file."""
    # First export
    output_file = tmp_path / "export.json"
    export_papers(sample_papers, str(output_file))

    # Then import
    imported = import_papers(str(output_file))

    assert len(imported) == 1
    assert imported[0]["id"] == "arxiv:2401.00001v1"
    assert imported[0]["title"] == "Attention Is All You Need"


def test_import_papers_invalid_file(tmp_path):
    """Test importing from non-existent file."""
    with pytest.raises(FileNotFoundError):
        import_papers(str(tmp_path / "nonexistent.json"))

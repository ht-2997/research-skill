import pytest
from scripts.report import format_terminal_table, generate_report


@pytest.fixture
def sample_screened_papers():
    return [
        {
            "id": "arxiv:2401.00001v1",
            "title": "Attention Is All You Need",
            "authors": ["John Doe", "Jane Smith"],
            "abstract": "We propose a new attention mechanism...",
            "source": "arxiv",
            "url": "http://arxiv.org/abs/2401.00001v1",
            "date": "2024-01-01",
            "label": "relevant",
            "scores": {"relevance": 9, "novelty": 8},
            "overall": 8.5,
            "summary": "Novel attention mechanism"
        },
        {
            "id": "semantic_scholar:abc123",
            "title": "Efficient Transformers Survey",
            "authors": ["Alice Johnson"],
            "abstract": "This paper surveys...",
            "source": "semantic_scholar",
            "url": "https://www.semanticscholar.org/paper/abc123",
            "date": "2024-06",
            "label": "possibly_relevant",
            "scores": {"relevance": 7, "novelty": 5},
            "overall": 6.0,
            "summary": "Comprehensive survey"
        }
    ]


def test_format_terminal_table(sample_screened_papers):
    """Test terminal table formatting."""
    output = format_terminal_table(sample_screened_papers, total_found=10)

    assert "10" in output  # Total found
    assert "2" in output  # Filtered count
    assert "Attention Is All You Need" in output
    assert "Efficient Transformers Survey" in output
    assert "8.5" in output
    assert "6.0" in output


def test_format_terminal_table_empty():
    """Test terminal table with empty results."""
    output = format_terminal_table([], total_found=0)

    assert "0" in output


def test_generate_report_markdown(sample_screened_papers):
    """Test Markdown report generation."""
    strategy = {
        "topic": "transformer attention",
        "keywords": ["attention", "transformer"],
        "exclude": ["survey"]
    }

    report = generate_report(sample_screened_papers, strategy, total_found=10)

    assert "# 论文搜索报告" in report
    assert "transformer attention" in report
    assert "attention" in report
    assert "## 搜索策略" in report
    assert "## 结果摘要" in report
    assert "## 论文列表" in report
    assert "Attention Is All You Need" in report
    assert "Efficient Transformers Survey" in report
    assert "8.5" in report
    assert "6.0" in report
    assert "✅ 相关" in report
    assert "❓ 待确认" in report


def test_save_report_to_file(sample_screened_papers, tmp_path):
    """Test saving report to file."""
    from scripts.report import save_report

    strategy = {
        "topic": "transformer attention",
        "keywords": ["attention", "transformer"],
        "exclude": ["survey"]
    }

    output_file = tmp_path / "report.md"
    save_report(sample_screened_papers, strategy, total_found=10, output_path=str(output_file))

    assert output_file.exists()
    content = output_file.read_text(encoding='utf-8')
    assert "# 论文搜索报告" in content
    assert "Attention Is All You Need" in content

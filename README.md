# Paper Search Skills

Claude Code skills for paper search with AI screening, supporting arXiv, Semantic Scholar, and Google Scholar.

## Features

- **Dialogue-based strategy:** Refine research ideas through conversation
- **Multi-source search:** arXiv, Semantic Scholar, Google Scholar
- **AI screening:** Classification + scoring with configurable models
- **Report generation:** Terminal table + Markdown report
- **Export/Import:** JSON format for sharing results

## Quick Start

### 1. Requirements

- Python 3.10+
- Claude Code (installed and configured)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure

Copy and edit the config template:

```bash
cp config.example.yaml config.yaml
```

Edit `config.yaml`:

```yaml
# External screening model (OpenAI-compatible API)
model:
  base_url: "https://integrate.api.nvidia.com/v1"  # API endpoint
  api_key: "nvapi-xxxx"                             # API key
  model_name: "meta/llama-3.1-8b-instruct"          # Model name

# Paper sources
sources:
  arxiv:
    enabled: true
  semantic_scholar:
    enabled: true
    api_key: ""  # Optional, higher rate limit with key
  google_scholar:
    enabled: false
    serpapi_key: ""  # Required for Google Scholar

# Screening dimensions (customize as needed)
dimensions:
  - name: "relevance"
    description: "与搜索策略的相关程度"
  - name: "novelty"
    description: "方法或视角的新颖性"
  - name: "reproducibility"
    description: "实验可复现的难易程度"

# Search parameters
search:
  max_results_per_source: 30
  date_range_years: 3
  concurrent_requests: 5
  dedup_threshold: 0.85
```

### 4. Usage

In Claude Code:

```
/paper-strategy    # Dialogue to generate search strategy
/paper-search      # Execute search + screening + report
```

## Data Sources

| Source | API Key Required | Notes |
|--------|-----------------|-------|
| arXiv | ❌ | Free public API, CS/Physics/Math |
| Semantic Scholar | Optional | Free without key, higher rate with key |
| Google Scholar | ✅ SerpAPI | Requires paid proxy |

## External Model Compatibility

Screening model must support OpenAI-compatible API format:

- **NVIDIA NIM:** `https://integrate.api.nvidia.com/v1`
- **Local Ollama:** `http://localhost:11434/v1`
- **OpenAI:** `https://api.openai.com/v1`
- **Other:** Any service implementing `/v1/chat/completions`

## Project Structure

```
paper-search/
├── skills/
│   ├── paper-strategy/    # Strategy generation skill
│   └── paper-search/      # Search orchestration skill
├── scripts/
│   ├── config.py          # Configuration loading
│   ├── search.py          # Paper search (arXiv, Semantic Scholar, Google Scholar)
│   ├── screen.py          # AI screening (classification + scoring)
│   ├── report.py          # Report generation (terminal + markdown)
│   └── export.py          # Export/import JSON
├── tests/                 # Unit tests
├── config.yaml            # Your configuration
├── config.example.yaml    # Configuration template
└── requirements.txt       # Python dependencies
```

## Development

### Run Tests

```bash
pytest tests/ -v
```

### Manual Testing

```bash
# Create a test strategy
echo '{"topic": "attention", "keywords": ["attention", "transformer"], "exclude": [], "max_results": 5}' > test_strategy.json

# Search
python scripts/search.py --strategy test_strategy.json --output papers.json

# Screen
python scripts/screen.py --papers papers.json --strategy test_strategy.json --output screened.json

# Report
python scripts/report.py --papers screened.json --strategy test_strategy.json --output report.md --total-found 5
```

## License

MIT

# Research Skill - Paper Search & AI Screening

Claude Code skills for academic paper search with AI-powered screening. Supports multiple data sources including ArXiv, DBLP, CrossRef, CORE, and Semantic Scholar.

## Features

- **Dialogue-based strategy:** Refine research ideas through conversation
- **Multi-source search:** ArXiv, DBLP, CrossRef, CORE, Semantic Scholar
- **AI screening:** Classification + scoring with configurable LLM models
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
  base_url: "https://integrate.api.nvidia.com/v1"
  api_key: ""  # Or set NVIDIA_API_KEY environment variable
  model_name: "openai/gpt-oss-120b"

# Paper sources
sources:
  arxiv:
    enabled: true
  dblp:
    enabled: true           # DBLP Computer Science Bibliography, free
  crossref:
    enabled: true           # CrossRef, free
    mailto: ""              # Optional: email for Polite Pool
  semantic_scholar:
    enabled: false          # Temporarily disabled (rate limited)
    api_key: ""
  core:
    enabled: false          # Requires API key
    api_key: ""             # Or set CORE_API_KEY environment variable
  google_scholar:
    enabled: false
    serpapi_key: ""

# Screening dimensions (customize as needed)
dimensions:
  - name: "relevance"
    description: "Relevance to the search strategy"
  - name: "novelty"
    description: "Novelty of method or perspective"
  - name: "reproducibility"
    description: "Ease of reproducing experiments"

# Search parameters
search:
  max_results_per_source: 30
  date_range_years: 3
  concurrent_requests: 5
  dedup_threshold: 0.85
```

### 4. Install Skills

Copy the skills to your Claude Code skills directory:

```bash
# Option A: Install to project directory
mkdir -p /path/to/your/project/.claude/skills
cp -r .claude/skills/* /path/to/your/project/.claude/skills/

# Option B: Install to user directory (global)
mkdir -p ~/.claude/skills
cp -r .claude/skills/* ~/.claude/skills/
```

### 5. Usage

In Claude Code:

```
/paper-strategy    # Dialogue to generate search strategy
/paper-search      # Execute search + screening + report
```

## Data Sources

| Source | API Key Required | Coverage | Notes |
|--------|-----------------|----------|-------|
| ArXiv | ❌ | CS, Physics, Math | Free public API |
| DBLP | ❌ | Computer Science | Free, no registration |
| CrossRef | ❌ | All disciplines | Free, email recommended for rate limits |
| CORE | ✅ | All disciplines (Open Access) | Free API key at core.ac.uk |
| Semantic Scholar | Optional | All disciplines | Free without key, higher rate with key |
| Google Scholar | ✅ SerpAPI | All disciplines | Requires paid proxy |

## Environment Variables

API keys can be set via environment variables:

```bash
# Linux/Mac
export NVIDIA_API_KEY="nvapi-xxxx"
export CORE_API_KEY="your-core-key"

# Windows CMD
set NVIDIA_API_KEY=nvapi-xxxx
set CORE_API_KEY=your-core-key

# PowerShell
$env:NVIDIA_API_KEY="nvapi-xxxx"
$env:CORE_API_KEY="your-core-key"
```

## External Model Compatibility

Screening model must support OpenAI-compatible API format:

- **NVIDIA NIM:** `https://integrate.api.nvidia.com/v1`
- **Local Ollama:** `http://localhost:11434/v1`
- **OpenAI:** `https://api.openai.com/v1`
- **Other:** Any service implementing `/v1/chat/completions`

## Project Structure

```
research-skill/
├── .claude/
│   └── skills/
│       ├── paper-strategy/    # Strategy generation skill
│       │   └── skill.md
│       └── paper-search/      # Search orchestration skill
│           └── skill.md
├── scripts/
│   ├── config.py          # Configuration loading
│   ├── search.py          # Paper search (ArXiv, DBLP, CrossRef, CORE, etc.)
│   ├── screen.py          # AI screening (classification + scoring)
│   ├── report.py          # Report generation (terminal + markdown)
│   └── export.py          # Export/import JSON
├── tests/                 # Unit tests
├── test_apis.py           # API connectivity test
├── list_models.py         # List available NVIDIA models
├── config.yaml            # Your configuration
├── config.example.yaml    # Configuration template
└── requirements.txt       # Python dependencies
```

## Development

### Test API Connectivity

```bash
python test_apis.py
```

### List Available Models

```bash
python list_models.py
```

### Run Tests

```bash
pytest tests/ -v
```

### Manual Testing

```bash
# Create a test strategy
echo '{"topic": "attention", "keywords": ["attention", "transformer"], "exclude": [], "max_results": 5}' > test_strategy.json

# Search
python scripts/search.py --strategy test_strategy.json --config config.yaml --output papers.json

# Screen
python scripts/screen.py --papers papers.json --strategy test_strategy.json --config config.yaml --output screened.json

# Report
python scripts/report.py --papers screened.json --strategy test_strategy.json --output report.md --total-found 5
```

## License

MIT

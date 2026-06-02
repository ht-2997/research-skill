# Research Skill - Paper Search & AI Screening

Claude Code skills for academic paper search with AI-powered screening. Supports multiple data sources including ArXiv, DBLP, CrossRef, CORE, and Semantic Scholar.

## Usage Mode

This is a **project-level skill**. You need to run Claude Code from this project directory to use the skills.

```bash
# Clone the repository
git clone https://github.com/ht-2997/research-skill.git
cd research-skill

# Install dependencies and configure
pip install -r requirements.txt
cp config.example.yaml config.yaml
# Edit config.yaml with your API keys

# Start Claude Code from this directory
claude

# Then use the skills
/paper-research    # Generate search strategy through dialogue
/paper-search      # Execute search + screening + report
```

## Skills Usage Guide

### `/paper-research` — Generate Search Strategy

**When to use:**
- You have a research idea but haven't formed search keywords yet
- You don't know what to search or how to search
- You need to refine your research direction through dialogue

**When NOT to use:**
- You already have a strategy file → use `/paper-search` directly
- You know exactly what keywords to search → skip to `/paper-search`
- You want to search for non-academic content (blog posts, news, etc.) → this skill is for academic papers only

### `/paper-search` — Execute Search & Screening

**When to use:**
- You have a strategy file ready (in `output/<topic>_<date>/strategy.json`)
- You have already defined keywords, exclusions, and search parameters
- You want to execute search, screening, and generate report

**When NOT to use:**
- You don't have a strategy file yet → use `/paper-research` first
- You are still unsure about research direction → use `/paper-research` first
- You want to search non-academic content → this skill is for academic papers only

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
  base_url: "https://openrouter.ai/api/v1"
  api_key: ""  # Or set OPENROUTER_API_KEY environment variable
  model_name: "openai/gpt-oss-120b:free"  # Free model on OpenRouter

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

### 4. Usage

In Claude Code (run from this project directory):

```
/paper-research    # Dialogue to generate search strategy
/paper-search      # Execute search + screening + report
```

## Data Sources

| Source | Free | Coverage | Notes |
|--------|------|----------|-------|
| ArXiv | ✅ | CS, Physics, Math | Free public API |
| DBLP | ✅ | Computer Science | Free, no registration |
| CrossRef | ✅ | All disciplines | Free, email recommended for rate limits |
| CORE | ✅ | All disciplines (Open Access | Free API key at core.ac.uk |
| Semantic Scholar | ✅ | All disciplines | Free without key, higher rate with key |
| Google Scholar | ❌ | All disciplines | Requires paid SerpAPI proxy |

## Environment Variables

API keys can be set via environment variables:

```bash
# Linux/Mac
export OPENROUTER_API_KEY="sk-or-xxxx"
export CORE_API_KEY="your-core-key"

# Windows CMD
set OPENROUTER_API_KEY=sk-or-xxxx
set CORE_API_KEY=your-core-key

# PowerShell
$env:OPENROUTER_API_KEY="sk-or-xxxx"
$env:CORE_API_KEY="your-core-key"
```

## External Model Compatibility

Screening model must support OpenAI-compatible API format:

- **OpenRouter (default):** `https://openrouter.ai/api/v1` — Free models available (e.g. `openai/gpt-oss-120b:free`)
- **Local Ollama:** `http://localhost:11434/v1`
- **OpenAI:** `https://api.openai.com/v1`
- **Other:** Any service implementing `/v1/chat/completions`

## Project Structure

```
research-skill/
├── .claude/
│   └── skills/
│       ├── paper-research/    # Strategy generation skill
│       │   └── skill.md
│       └── paper-search/      # Search orchestration skill
│           └── skill.md
├── scripts/
│   ├── config.py          # Configuration loading
│   ├── search.py          # Paper search (ArXiv, DBLP, CrossRef, CORE, etc.)
│   ├── screen.py          # AI screening (classification + scoring)
│   ├── report.py          # Report generation (terminal + markdown)
│   └── export.py          # Export/import JSON
├── output/                # Output files (auto-generated)
│   └── <topic>_<date>/    # One folder per research topic
│       ├── strategy.json
│       ├── papers_raw.json
│       ├── papers_screened.json
│       └── report.md
├── config.yaml            # Your configuration
├── config.example.yaml    # Configuration template
└── requirements.txt       # Python dependencies
```

## Development

### Manual Testing

```bash
# Create output folder
mkdir -p output/test-search_20260602

# Create a test strategy
echo '{"topic": "attention", "keywords": ["attention", "transformer"], "exclude": [], "max_results": 5}' > output/test-search_20260602/strategy.json

# Search
python scripts/search.py --strategy output/test-search_20260602/strategy.json --config config.yaml --output output/test-search_20260602/papers_raw.json

# Screen
python scripts/screen.py --papers output/test-search_20260602/papers_raw.json --strategy output/test-search_20260602/strategy.json --config config.yaml --output output/test-search_20260602/papers_screened.json

# Report
python scripts/report.py --papers output/test-search_20260602/papers_screened.json --strategy output/test-search_20260602/strategy.json --output output/test-search_20260602/report.md --total-found 5
```

## License

MIT

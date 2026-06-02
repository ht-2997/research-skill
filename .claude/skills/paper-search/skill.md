# Paper Search Skill

Execute paper search based on a strategy, screen results with AI, and generate reports.

## Prerequisites

- Python 3.10+
- Dependencies installed: `pip install -r requirements.txt`
- Config file created: `cp config.example.yaml config.yaml`
- API keys configured in `config.yaml` or environment variables

## Process

1. **Load strategy:** Read from file or accept inline
2. **Confirm with user:** Show strategy summary and get approval
3. **Search:** Run `scripts/search.py` to find papers
4. **Screen:** Run `scripts/screen.py` to classify and score papers
5. **Report:** Run `scripts/report.py` to generate terminal + Markdown output
6. **Export (optional):** Run `scripts/export.py` if user wants to save

## Commands

```bash
# Search papers
python scripts/search.py --strategy <strategy.json> --config config.yaml --output papers_raw.json

# Screen papers
python scripts/screen.py --papers papers_raw.json --strategy <strategy.json> --config config.yaml --output papers_screened.json

# Generate report
python scripts/report.py --papers papers_screened.json --strategy <strategy.json> --output report.md --total-found <N>

# Export results
python scripts/export.py --papers papers_screened.json --output search_YYYYMMDD.json
```

## Data Sources

| Source | API Key Required | Notes |
|--------|-----------------|-------|
| ArXiv | No | Free public API |
| DBLP | No | Computer Science |
| CrossRef | No | All disciplines |
| CORE | Yes | Open Access papers |
| Semantic Scholar | Optional | Higher rate with key |

## Environment Variables

```bash
export NVIDIA_API_KEY="nvapi-xxxx"    # For screening model
export CORE_API_KEY="your-core-key"   # For CORE search
```

## User Interaction Points

- **Before search:** Confirm strategy
- **After search:** Show raw count
- **After screening:** Show filtered count and top papers
- **After report:** Ask if user wants to export or adjust

## Example Usage

User: "Search for papers using my strategy file"

Assistant: "I'll search for papers based on your strategy.

**Strategy summary:**
- Topic: Model compression
- Keywords: model compression, knowledge distillation, pruning
- Exclude: survey
- Max results: 50

Starting search..."

[Run search.py]

"Found 45 papers. Now screening with AI..."

[Run screen.py]

"Screened to 12 relevant papers. Generating report..."

[Run report.py]

"📊 Results:
#  Title                                    Source      Score   Date
1  Efficient Knowledge Distillation         arxiv       9.2    2024-01
2  Pruning Strategies for LLMs              sem.sch     8.7    2024-03
...

Report saved to `report.md`.

Would you like to:
1. Export results to JSON
2. Adjust screening dimensions
3. Search with different keywords?"

# Paper Search Skill

Execute paper search based on a strategy, screen results with AI, and generate reports.

## When to Use

- User has a strategy file ready (in `output/<topic>_<date>/strategy.json`)
- User has already defined keywords, exclusions, and search parameters
- User wants to execute search, screening, and generate report

## When NOT to Use

- User doesn't have a strategy file yet → use `/paper-research` first
- User is still unsure about research direction → use `/paper-research` first
- User wants to search non-academic content → this skill is for academic papers only

## Prerequisites

- Python 3.10+
- Dependencies installed: `pip install -r requirements.txt`
- Config file created: `cp config.example.yaml config.yaml`
- API keys configured in `config.yaml` or environment variables

## Process

1. **Load strategy:** Read from `output/<topic>_<date>/strategy.json`
2. **Confirm with user:** Show strategy summary and get approval
3. **Search:** Run `scripts/search.py` to find papers
4. **Screen:** Run `scripts/screen.py` to classify and score papers
5. **Report:** Run `scripts/report.py` to generate terminal + Markdown output
6. **Final output:** All files saved to the same `output/<topic>_<date>/` folder

## Commands

```bash
# Set output directory (replace with your actual folder name)
OUTPUT_DIR="output/<topic-name>_<YYYYMMDD>"

# Search papers
python scripts/search.py --strategy $OUTPUT_DIR/strategy.json --config config.yaml --output $OUTPUT_DIR/papers_raw.json

# Screen papers
python scripts/screen.py --papers $OUTPUT_DIR/papers_raw.json --strategy $OUTPUT_DIR/strategy.json --config config.yaml --output $OUTPUT_DIR/papers_screened.json

# Generate report
python scripts/report.py --papers $OUTPUT_DIR/papers_screened.json --strategy $OUTPUT_DIR/strategy.json --output $OUTPUT_DIR/report.md --total-found <N>
```

## Output Folder Structure

```
output/
└── <topic-name>_<YYYYMMDD>/
    ├── strategy.json          # Search strategy
    ├── papers_raw.json        # Raw search results
    ├── papers_screened.json   # AI-screened results
    └── report.md              # Final report
```

## Data Sources

| Source | Free | Notes |
|--------|------|-------|
| ArXiv | ✅ | Free public API |
| DBLP | ✅ | Computer Science |
| CrossRef | ✅ | All disciplines |
| CORE | ✅ | Open Access papers, free API key |
| Semantic Scholar | ✅ | Free without key, higher rate with key |

## Environment Variables

```bash
export OPENROUTER_API_KEY="sk-or-xxxx"  # For screening model
export CORE_API_KEY="your-core-key"      # For CORE search
```

## User Interaction Points

- **Before search:** Confirm strategy
- **After search:** Show raw count
- **After screening:** Show filtered count and top papers
- **After report:** Ask if user wants to adjust

## Example Usage

User: "Search for papers using my strategy file"

Assistant: "I'll search for papers based on your strategy.

**Strategy summary:**
- Topic: VLM SAM bbox correction
- Keywords: VLM, SAM, bbox, prompt refinement
- Exclude: point prompt
- Max results: 50

Starting search..."

[Run search.py → output/vlm-sam-bbox-correction_20260602/papers_raw.json]

"Found 45 papers. Now screening with AI..."

[Run screen.py → output/vlm-sam-bbox-correction_20260602/papers_screened.json]

"Screened to 12 relevant papers. Generating report..."

[Run report.py → output/vlm-sam-bbox-correction_20260602/report.md]

"📊 Results:
#  Title                                    Source      Score   Date
1  Efficient Knowledge Distillation         arxiv       9.2    2024-01
2  Pruning Strategies for LLMs              sem.sch     8.7    2024-03
...

All files saved to `output/vlm-sam-bbox-correction_20260602/`.

Would you like to:
1. Adjust screening dimensions
2. Search with different keywords?"

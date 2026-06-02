import json
from datetime import datetime
from typing import List, Dict, Any


def export_papers(papers: List[Dict[str, Any]], output_path: str) -> None:
    """Export papers to JSON file."""
    export_data = {
        "metadata": {
            "exported_at": datetime.now().isoformat(),
            "total_papers": len(papers)
        },
        "papers": papers
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)


def import_papers(input_path: str) -> List[Dict[str, Any]]:
    """Import papers from JSON file."""
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if "papers" not in data:
        raise ValueError("Invalid export file: missing 'papers' key")

    return data["papers"]


import argparse


def main():
    parser = argparse.ArgumentParser(description="Export/Import paper search results")
    parser.add_argument("--papers", help="Path to papers JSON file (for export)")
    parser.add_argument("--input", help="Path to import file")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--show", action="store_true", help="Show imported papers")

    args = parser.parse_args()

    if args.papers and args.output:
        # Export mode
        with open(args.papers, 'r', encoding='utf-8') as f:
            papers = json.load(f)
        export_papers(papers, args.output)
        print(f"Exported {len(papers)} papers to {args.output}")

    elif args.input:
        # Import mode
        papers = import_papers(args.input)
        print(f"Imported {len(papers)} papers")

        if args.show:
            for i, paper in enumerate(papers, 1):
                print(f"{i}. {paper.get('title', '')} ({paper.get('overall', 0):.1f})")

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(papers, f, ensure_ascii=False, indent=2)
            print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()

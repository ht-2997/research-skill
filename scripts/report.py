from datetime import datetime
from typing import List, Dict, Any


def format_terminal_table(papers: List[Dict[str, Any]], total_found: int) -> str:
    """Format papers as a terminal table."""
    if not papers:
        return f"搜索结果：共 {total_found} 篇，筛选后 0 篇相关"

    # Header
    lines = [f"搜索结果：共 {total_found} 篇，筛选后 {len(papers)} 篇相关\n"]

    # Table header
    lines.append(f"{'#':<4} {'标题':<45} {'来源':<15} {'评分':<8} {'状态':<12} {'日期':<10}")
    lines.append("-" * 94)

    # Table rows
    for i, paper in enumerate(papers, 1):
        title = paper.get("title", "")
        if len(title) > 42:
            title = title[:42] + "..."

        source = paper.get("source", "")
        source_short = {
            "arxiv": "arxiv",
            "semantic_scholar": "sem.scholar",
            "google_scholar": "g.scholar"
        }.get(source, source)

        overall = paper.get("overall", 0.0)
        label = paper.get("label", "")
        status_icon = {
            "relevant": "Y",
            "possibly_relevant": "?",
            "irrelevant": "N"
        }.get(label, "")

        date = paper.get("date", "")

        lines.append(f"{i:<4} {title:<45} {source_short:<15} {overall:<8.1f} {status_icon:<12} {date:<10}")

    return "\n".join(lines)


def generate_report(papers: List[Dict[str, Any]], strategy: Dict[str, Any], total_found: int) -> str:
    """Generate Markdown report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# 论文搜索报告 - {now}",
        "",
        "## 搜索策略",
        f"- 主题: {strategy.get('topic', '')}",
        f"- 关键词: {', '.join(strategy.get('keywords', []))}",
        f"- 排除: {', '.join(strategy.get('exclude', []))}",
        "",
        "## 结果摘要",
        f"- 总计: {total_found}",
        f"- 相关: {len(papers)}",
    ]

    if papers:
        avg_score = sum(p.get("overall", 0) for p in papers) / len(papers)
        lines.append(f"- 平均分: {avg_score:.1f}")

    lines.append("")
    lines.append("## 论文列表")

    for i, paper in enumerate(papers, 1):
        overall = paper.get("overall", 0.0)
        title = paper.get("title", "")
        source = paper.get("source", "")
        date = paper.get("date", "")
        url = paper.get("url", "")
        summary = paper.get("summary", "")
        abstract = paper.get("abstract", "")

        scores = paper.get("scores", {})
        scores_str = " | ".join([f"{k} {v}" for k, v in scores.items()])

        label = paper.get("label", "")
        status = {
            "relevant": "✅ 相关",
            "possibly_relevant": "❓ 待确认",
            "irrelevant": "❌ 不相关"
        }.get(label, "")

        lines.extend([
            f"### {i}. {title} ({overall:.1f}) {status}",
            f"- 来源: {source} | 日期: {date}",
            f"- 评分: {scores_str}",
            f"- 摘要: {summary}",
            f"- 摘要详情: {abstract[:200]}{'...' if len(abstract) > 200 else ''}",
            f"- 链接: {url}",
            ""
        ])

    return "\n".join(lines)


def save_report(papers: List[Dict[str, Any]], strategy: Dict[str, Any], total_found: int, output_path: str) -> None:
    """Save report to Markdown file."""
    report_content = generate_report(papers, strategy, total_found)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)


import argparse
import json


def main():
    parser = argparse.ArgumentParser(description="Generate paper search report")
    parser.add_argument("--papers", required=True, help="Path to screened papers JSON file")
    parser.add_argument("--strategy", required=True, help="Path to strategy JSON file")
    parser.add_argument("--output", required=True, help="Output Markdown file path")
    parser.add_argument("--total-found", type=int, default=0, help="Total papers found before screening")

    args = parser.parse_args()

    # Load papers
    with open(args.papers, 'r', encoding='utf-8') as f:
        papers = json.load(f)

    # Load strategy
    with open(args.strategy, 'r', encoding='utf-8') as f:
        strategy = json.load(f)

    # Print terminal table
    print(format_terminal_table(papers, args.total_found))
    print()

    # Save Markdown report
    save_report(papers, strategy, args.total_found, args.output)
    print(f"Report saved to {args.output}")


if __name__ == "__main__":
    main()

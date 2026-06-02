import json
import asyncio
import sys
import io
import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import httpx

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def _get_system_proxy() -> Optional[str]:
    """Detect system proxy on Windows. Returns proxy URL or None."""
    if sys.platform == 'win32':
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Internet Settings'
            )
            proxy_enable, _ = winreg.QueryValueEx(key, 'ProxyEnable')
            if proxy_enable:
                proxy_server, _ = winreg.QueryValueEx(key, 'ProxyServer')
                winreg.CloseKey(key)
                if proxy_server:
                    if not proxy_server.startswith(('http://', 'https://', 'socks5://')):
                        proxy_server = f'http://{proxy_server}'
                    return proxy_server
            winreg.CloseKey(key)
        except Exception:
            pass
    return os.environ.get('HTTP_PROXY') or os.environ.get('HTTPS_PROXY') or os.environ.get('http_proxy') or os.environ.get('https_proxy')


SYSTEM_PROXY = _get_system_proxy()


@dataclass
class ScreenResult:
    paper_id: str = ""
    label: str = ""  # relevant, possibly_relevant, irrelevant
    reasoning: str = ""
    scores: Dict[str, float] = field(default_factory=dict)
    overall: float = 0.0
    summary: str = ""


async def call_llm(base_url: str, api_key: str, model_name: str, messages: List[Dict[str, str]], max_retries: int = 3) -> Dict[str, Any]:
    """Call OpenAI-compatible LLM API with retry logic."""
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.1
    }

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(proxy=SYSTEM_PROXY) as client:
                response = await client.post(url, json=data, headers=headers, timeout=120.0)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # 指数退避
                continue
            raise


def build_classify_prompt(paper: dict, strategy: dict) -> List[Dict[str, str]]:
    """Build classification prompt."""
    system_prompt = """你是一个论文筛选助手。根据搜索策略，判断论文是否相关。

请回答以下三个类别之一：
- relevant：高度相关
- possibly_relevant：可能相关，需要进一步确认
- irrelevant：不相关

回答格式：
<label>
<reasoning>"""

    user_prompt = f"""搜索策略：
- 主题：{strategy.get('topic', '')}
- 关键词：{', '.join(strategy.get('keywords', []))}
- 排除：{', '.join(strategy.get('exclude', []))}

论文信息：
- 标题：{paper.get('title', '')}
- 摘要：{paper.get('abstract', '')}"""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]


async def classify_paper(paper: dict, strategy: dict, config) -> ScreenResult:
    """Classify a single paper."""
    messages = build_classify_prompt(paper, strategy)

    response = await call_llm(
        config.model.base_url,
        config.model.api_key,
        config.model.model_name,
        messages
    )

    content = response["choices"][0]["message"]["content"]

    # Parse response - match label on the first line only
    label = "irrelevant"
    reasoning = content

    lines = content.strip().split("\n")
    first_line = lines[0].strip().lower()

    # Check in order from most specific to least to avoid substring matches
    for valid_label in ["possibly_relevant", "relevant", "irrelevant"]:
        if first_line == valid_label:
            label = valid_label
            reasoning = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
            break

    return ScreenResult(
        paper_id=paper.get("id", ""),
        label=label,
        reasoning=reasoning
    )


def build_score_prompt(paper: dict, strategy: dict, dimensions: List) -> List[Dict[str, str]]:
    """Build scoring prompt."""
    dimensions_text = "\n".join([f"- {d.name}: {d.description}" for d in dimensions])

    system_prompt = f"""你是一个论文评审助手。请对论文进行评分。

请按以下维度打分（1-10）：
{dimensions_text}

输出严格的JSON格式：
{{
  "scores": {{"dimension_name": score, ...}},
  "overall": average_score,
  "summary": "一句话总结这篇论文为什么有价值"
}}"""

    user_prompt = f"""搜索策略：
- 主题：{strategy.get('topic', '')}
- 关键词：{', '.join(strategy.get('keywords', []))}

论文信息：
- 标题：{paper.get('title', '')}
- 摘要：{paper.get('abstract', '')}"""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]


async def score_papers(papers: List[dict], classify_results: List[ScreenResult], strategy: dict, config) -> List[ScreenResult]:
    """Score papers that passed classification with concurrency."""
    # Filter to only relevant and possibly_relevant papers
    relevant_ids = {r.paper_id for r in classify_results if r.label in ["relevant", "possibly_relevant"]}
    papers_to_score = [p for p in papers if p["id"] in relevant_ids]

    sem = asyncio.Semaphore(5)

    async def score_one(paper):
        async with sem:
            messages = build_score_prompt(paper, strategy, config.dimensions)
            try:
                response = await call_llm(
                    config.model.base_url,
                    config.model.api_key,
                    config.model.model_name,
                    messages
                )

                content = response["choices"][0]["message"]["content"]
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                score_data = json.loads(content.strip())

                return ScreenResult(
                    paper_id=paper["id"],
                    label=next((r.label for r in classify_results if r.paper_id == paper["id"]), ""),
                    reasoning=next((r.reasoning for r in classify_results if r.paper_id == paper["id"]), ""),
                    scores=score_data.get("scores", {}),
                    overall=score_data.get("overall", 0.0),
                    summary=score_data.get("summary", "")
                )
            except Exception as e:
                return ScreenResult(
                    paper_id=paper["id"],
                    label=next((r.label for r in classify_results if r.paper_id == paper["id"]), ""),
                    reasoning=f"Scoring failed: {str(e)}",
                    scores={d.name: 5 for d in config.dimensions},
                    overall=5.0,
                    summary="Scoring failed"
                )

    results = await asyncio.gather(*[score_one(p) for p in papers_to_score])

    # Sort by overall score descending
    results.sort(key=lambda x: x.overall, reverse=True)
    return results


import argparse


async def main():
    parser = argparse.ArgumentParser(description="Screen papers using AI")
    parser.add_argument("--papers", required=True, help="Path to papers JSON file")
    parser.add_argument("--strategy", required=True, help="Path to strategy JSON file")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    parser.add_argument("--output", required=True, help="Output JSON file path")

    args = parser.parse_args()

    # Load papers
    with open(args.papers, 'r', encoding='utf-8') as f:
        papers = json.load(f)

    # Load strategy
    with open(args.strategy, 'r', encoding='utf-8') as f:
        strategy = json.load(f)

    # Load config
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scripts.config import load_config
    config = load_config(args.config)

    # Classify papers with concurrency
    sem = asyncio.Semaphore(5)  # Limit to 5 concurrent requests

    async def classify_with_limit(i, paper):
        async with sem:
            try:
                result = await classify_paper(paper, strategy, config)
                safe_title = paper['title'][:50].encode('utf-8', errors='replace').decode('utf-8')
                print(f"[{i+1}/{len(papers)}] Classified: {safe_title}... -> {result.label}")
                return result
            except Exception as e:
                safe_title = paper['title'][:50].encode('utf-8', errors='replace').decode('utf-8')
                print(f"[{i+1}/{len(papers)}] Failed: {safe_title}... Error: {e}")
                return ScreenResult(
                    paper_id=paper.get("id", ""),
                    label="irrelevant",
                    reasoning=f"Classification failed: {str(e)}"
                )

    classify_results = await asyncio.gather(*[classify_with_limit(i, p) for i, p in enumerate(papers)])

    # Score papers
    score_results = await score_papers(papers, classify_results, strategy, config)

    # Merge results into papers
    screened_papers = []
    for paper in papers:
        classify_result = next((r for r in classify_results if r.paper_id == paper["id"]), None)
        score_result = next((r for r in score_results if r.paper_id == paper["id"]), None)

        if classify_result and classify_result.label != "irrelevant":
            screened_paper = {
                **paper,
                "label": classify_result.label,
                "reasoning": classify_result.reasoning,
                "scores": score_result.scores if score_result else {},
                "overall": score_result.overall if score_result else 0.0,
                "summary": score_result.summary if score_result else ""
            }
            screened_papers.append(screened_paper)

    # Sort by overall score
    screened_papers.sort(key=lambda x: x.get("overall", 0), reverse=True)

    # Save results
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(screened_papers, f, ensure_ascii=False, indent=2)

    print(f"Screened {len(papers)} papers -> {len(screened_papers)} relevant")


if __name__ == "__main__":
    asyncio.run(main())

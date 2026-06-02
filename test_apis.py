"""Test all paper search APIs."""
import asyncio
import httpx
import json


async def test_dblp():
    """Test DBLP API."""
    print("\n🔍 测试 DBLP API...")
    url = "https://dblp.org/search/publ/api"
    params = {
        "q": "visual language model segmentation",
        "format": "json",
        "h": 3
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            hits = data.get("result", {}).get("hits", {}).get("hit", [])
            print(f"  ✅ DBLP 成功! 返回 {len(hits)} 条结果")
            if hits:
                print(f"  📄 示例: {hits[0].get('info', {}).get('title', 'N/A')[:60]}...")
            return True
    except Exception as e:
        print(f"  ❌ DBLP 失败: {e}")
        return False


async def test_crossref():
    """Test CrossRef API."""
    print("\n🔍 测试 CrossRef API...")
    url = "https://api.crossref.org/works"
    params = {
        "query": "visual language model SAM segmentation",
        "rows": 3,
        "sort": "relevance"
    }
    headers = {"Mailto": "test@example.com"}  # Polite Pool
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            items = data.get("message", {}).get("items", [])
            print(f"  ✅ CrossRef 成功! 返回 {len(items)} 条结果")
            if items:
                title = items[0].get("title", ["N/A"])[0] if items[0].get("title") else "N/A"
                print(f"  📄 示例: {title[:60]}...")
            return True
    except Exception as e:
        print(f"  ❌ CrossRef 失败: {e}")
        return False


async def test_core():
    """Test CORE API (without key, expect auth error)."""
    print("\n🔍 测试 CORE API...")
    url = "https://api.core.ac.uk/v3/search/works/"  # 注意末尾的斜杠
    params = {"q": "visual language model", "limit": 1}
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, params=params, timeout=30.0)
            if response.status_code == 401:
                print("  ⚠️ CORE 需要 API Key (401 Unauthorized)")
                print("  📝 请从 https://core.ac.uk/services/api 申请 key")
                return False
            response.raise_for_status()
            data = response.json()
            print(f"  ✅ CORE 成功!")
            return True
    except Exception as e:
        print(f"  ❌ CORE 失败: {e}")
        return False


async def test_arxiv():
    """Test ArXiv API."""
    print("\n🔍 测试 ArXiv API...")
    url = "https://export.arxiv.org/api/query"  # 使用 HTTPS
    params = {
        "search_query": 'all:"visual language model" AND all:"SAM"',
        "max_results": 3,
        "sortBy": "relevance"
    }
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            # Parse XML
            from xml.etree import ElementTree as ET
            root = ET.fromstring(response.text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entries = root.findall("atom:entry", ns)
            print(f"  ✅ ArXiv 成功! 返回 {len(entries)} 条结果")
            if entries:
                title = entries[0].find("atom:title", ns).text.strip()[:60]
                print(f"  📄 示例: {title}...")
            return True
    except Exception as e:
        print(f"  ❌ ArXiv 失败: {e}")
        return False


async def test_semantic_scholar():
    """Test Semantic Scholar API."""
    print("\n🔍 测试 Semantic Scholar API...")
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": "visual language model SAM segmentation prompt",
        "limit": 3,
        "fields": "title,abstract,year"
    }
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, params=params, timeout=30.0)
            if response.status_code == 429:
                print("  ⚠️ Semantic Scholar 速率限制，稍后重试...")
                await asyncio.sleep(2)
                response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            papers = data.get("data", [])
            print(f"  ✅ Semantic Scholar 成功! 返回 {len(papers)} 条结果")
            if papers:
                print(f"  📄 示例: {papers[0].get('title', 'N/A')[:60]}...")
            return True
    except Exception as e:
        print(f"  ❌ Semantic Scholar 失败: {e}")
        return False


async def main():
    print("=" * 60)
    print("🚀 开始测试所有学术搜索 API")
    print("=" * 60)

    results = await asyncio.gather(
        test_arxiv(),
        test_semantic_scholar(),
        test_dblp(),
        test_crossref(),
        test_core()
    )

    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    print("=" * 60)
    apis = ["ArXiv", "Semantic Scholar", "DBLP", "CrossRef", "CORE"]
    for api, result in zip(apis, results):
        status = "✅ 可用" if result else "❌ 不可用"
        print(f"  {api}: {status}")

    available = sum(results)
    print(f"\n总计: {available}/{len(apis)} 个 API 可用")


if __name__ == "__main__":
    asyncio.run(main())

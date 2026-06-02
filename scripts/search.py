import re
import json
from dataclasses import dataclass, field
from typing import List, Optional
from xml.etree import ElementTree as ET
import httpx


@dataclass
class Paper:
    id: str = ""
    title: str = ""
    authors: List[str] = field(default_factory=list)
    abstract: str = ""
    source: str = ""
    url: str = ""
    date: str = ""
    citation_count: Optional[int] = None
    pdf_url: Optional[str] = None


class ArxivSearcher:
    BASE_URL = "https://export.arxiv.org/api/query"  # 使用 HTTPS

    def _build_query(self, strategy: dict) -> str:
        """Build ArXiv search query from strategy."""
        keywords = strategy.get("keywords", [])
        exclude = strategy.get("exclude", [])

        # Build OR query for keywords
        keyword_query = " OR ".join([f'all:"{kw}"' for kw in keywords])

        # Build exclude query
        if exclude:
            exclude_query = " AND ".join([f'NOT all:"{ex}"' for ex in exclude])
            return f"({keyword_query}) AND {exclude_query}"

        return keyword_query

    def _parse_response(self, xml_text: str) -> List[Paper]:
        """Parse ArXiv XML response to Paper list."""
        papers = []
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        root = ET.fromstring(xml_text)
        for entry in root.findall("atom:entry", ns):
            arxiv_id = entry.find("atom:id", ns).text
            paper_id = f"arxiv:{arxiv_id.split('/abs/')[-1]}"

            title = entry.find("atom:title", ns).text.strip()
            title = re.sub(r'\s+', ' ', title)

            authors = [
                author.find("atom:name", ns).text
                for author in entry.findall("atom:author", ns)
            ]

            summary = entry.find("atom:summary", ns).text.strip()
            published = entry.find("atom:published", ns).text[:10]

            # Get links
            url = ""
            pdf_url = None
            for link in entry.findall("atom:link", ns):
                if link.get("rel") == "alternate":
                    url = link.get("href", "")
                elif link.get("type") == "application/pdf":
                    pdf_url = link.get("href", "")

            papers.append(Paper(
                id=paper_id,
                title=title,
                authors=authors,
                abstract=summary,
                source="arxiv",
                url=url,
                date=published,
                pdf_url=pdf_url
            ))

        return papers

    async def search(self, strategy: dict, max_results: int = 30) -> List[Paper]:
        """Search ArXiv for papers."""
        query = self._build_query(strategy)
        params = {
            "search_query": query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }

        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(self.BASE_URL, params=params, timeout=60.0)
                response.raise_for_status()
            return self._parse_response(response.text)
        except Exception as e:
            print(f"ArXiv search failed: {e}")
            return []


class SemanticScholarSearcher:
    BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

    def _build_query(self, strategy: dict) -> str:
        """Build search query from strategy."""
        keywords = strategy.get("keywords", [])
        return " ".join(keywords)

    def _parse_response(self, data: dict) -> List[Paper]:
        """Parse Semantic Scholar JSON response to Paper list."""
        papers = []

        for item in data.get("data", []):
            paper_id = f"semantic_scholar:{item['paperId']}"

            authors = [a["name"] for a in item.get("authors", [])]

            # Get ArXiv ID if available
            external_ids = item.get("externalIds", {})
            arxiv_id = external_ids.get("ArXiv")

            date = str(item.get("year", ""))

            papers.append(Paper(
                id=paper_id,
                title=item.get("title", ""),
                authors=authors,
                abstract=item.get("abstract", ""),
                source="semantic_scholar",
                url=item.get("url", ""),
                date=date,
                citation_count=item.get("citationCount"),
                pdf_url=None
            ))

        return papers

    async def search(self, strategy: dict, max_results: int = 30, api_key: str = "") -> List[Paper]:
        """Search Semantic Scholar for papers."""
        query = self._build_query(strategy)
        params = {
            "query": query,
            "limit": max_results,
            "fields": "paperId,title,authors,abstract,url,year,citationCount,externalIds"
        }

        headers = {}
        if api_key:
            headers["x-api-key"] = api_key

        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(self.BASE_URL, params=params, headers=headers, timeout=60.0)
                if response.status_code == 429:
                    await asyncio.sleep(3)
                    response = await client.get(self.BASE_URL, params=params, headers=headers, timeout=60.0)
                response.raise_for_status()
            return self._parse_response(response.json())
        except Exception as e:
            print(f"Semantic Scholar search failed: {e}")
            return []


class GoogleScholarSearcher:
    BASE_URL = "https://serpapi.com/search"

    def _build_query(self, strategy: dict) -> str:
        """Build search query from strategy."""
        keywords = strategy.get("keywords", [])
        exclude = strategy.get("exclude", [])

        query = " ".join(keywords)
        if exclude:
            exclude_terms = " ".join([f"-{ex}" for ex in exclude])
            query = f"{query} {exclude_terms}"

        return query

    def _parse_response(self, data: dict) -> List[Paper]:
        """Parse Google Scholar response to Paper list."""
        papers = []

        for item in data.get("organic_results", []):
            paper_id = f"google_scholar:{item.get('result_id', '')}"

            # Extract authors from publication_info
            pub_info = item.get("publication_info", {})
            authors = [a["name"] for a in pub_info.get("authors", [])]

            # Extract date from summary
            summary = pub_info.get("summary", "")
            date_match = re.search(r'\b(19|20)\d{2}\b', summary)
            date = date_match.group(0) if date_match else ""

            papers.append(Paper(
                id=paper_id,
                title=item.get("title", ""),
                authors=authors,
                abstract=item.get("snippet", ""),
                source="google_scholar",
                url=item.get("link", ""),
                date=date,
                citation_count=None,
                pdf_url=None
            ))

        return papers

    async def search(self, strategy: dict, max_results: int = 30, serpapi_key: str = "") -> List[Paper]:
        """Search Google Scholar via SerpAPI."""
        if not serpapi_key:
            raise ValueError("SerpAPI key required for Google Scholar search")

        query = self._build_query(strategy)
        params = {
            "q": query,
            "num": max_results,
            "api_key": serpapi_key,
            "engine": "google_scholar"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.BASE_URL, params=params)
            response.raise_for_status()

        return self._parse_response(response.json())


class DBLPSearcher:
    """DBLP Computer Science Bibliography searcher."""
    BASE_URL = "https://dblp.org/search/publ/api"

    def _build_query(self, strategy: dict) -> str:
        """Build DBLP search query from strategy."""
        keywords = strategy.get("keywords", [])
        return " ".join(keywords)

    def _parse_response(self, data: dict) -> List[Paper]:
        """Parse DBLP JSON response to Paper list."""
        papers = []
        hits = data.get("result", {}).get("hits", {}).get("hit", [])

        for item in hits:
            info = item.get("info", {})
            paper_id = f"dblp:{item.get('@id', '')}"

            # Extract authors - can be single author or list
            authors_data = info.get("authors", {}).get("author", [])
            if isinstance(authors_data, dict):
                authors = [authors_data.get("text", "")]
            elif isinstance(authors_data, list):
                authors = [a.get("text", "") if isinstance(a, dict) else str(a) for a in authors_data]
            else:
                authors = []

            # Extract year
            year = info.get("year", "")

            papers.append(Paper(
                id=paper_id,
                title=info.get("title", ""),
                authors=authors,
                abstract="",  # DBLP doesn't provide abstracts
                source="dblp",
                url=info.get("url", ""),
                date=str(year),
                citation_count=None,
                pdf_url=info.get("ee", None)  # Electronic edition URL
            ))

        return papers

    async def search(self, strategy: dict, max_results: int = 30) -> List[Paper]:
        """Search DBLP for papers."""
        query = self._build_query(strategy)
        params = {
            "q": query,
            "format": "json",
            "h": max_results
        }

        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(self.BASE_URL, params=params, timeout=60.0)
                response.raise_for_status()
            return self._parse_response(response.json())
        except Exception as e:
            print(f"DBLP search failed: {e}")
            return []


class CrossRefSearcher:
    """CrossRef API searcher for scholarly works."""
    BASE_URL = "https://api.crossref.org/works"

    def _build_query(self, strategy: dict) -> str:
        """Build CrossRef search query from strategy."""
        keywords = strategy.get("keywords", [])
        return " ".join(keywords)

    def _parse_response(self, data: dict) -> List[Paper]:
        """Parse CrossRef JSON response to Paper list."""
        papers = []
        items = data.get("message", {}).get("items", [])

        for item in items:
            paper_id = f"crossref:{item.get('DOI', '')}"

            # Extract authors
            authors = []
            for author in item.get("author", []):
                name_parts = []
                if author.get("given"):
                    name_parts.append(author["given"])
                if author.get("family"):
                    name_parts.append(author["family"])
                if name_parts:
                    authors.append(" ".join(name_parts))

            # Extract date
            date_parts = item.get("published-print", {}).get("date-parts", [[]])
            date = str(date_parts[0][0]) if date_parts and date_parts[0] else ""

            # Extract abstract (may contain HTML tags)
            abstract = item.get("abstract", "")
            if abstract:
                # Simple HTML tag removal
                abstract = re.sub(r'<[^>]+>', '', abstract)

            papers.append(Paper(
                id=paper_id,
                title=item.get("title", [""])[0] if item.get("title") else "",
                authors=authors,
                abstract=abstract,
                source="crossref",
                url=item.get("URL", ""),
                date=date,
                citation_count=item.get("is-referenced-by-count"),
                pdf_url=None
            ))

        return papers

    async def search(self, strategy: dict, max_results: int = 30, mailto: str = "") -> List[Paper]:
        """Search CrossRef for papers."""
        query = self._build_query(strategy)
        params = {
            "query": query,
            "rows": max_results,
            "sort": "relevance",
            "order": "desc"
        }

        headers = {}
        if mailto:
            headers["Mailto"] = mailto  # Enables Polite Pool for better rate limits

        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(self.BASE_URL, params=params, headers=headers, timeout=60.0)
                response.raise_for_status()
            return self._parse_response(response.json())
        except Exception as e:
            print(f"CrossRef search failed: {e}")
            return []


class CORESearcher:
    """CORE open access papers searcher."""
    BASE_URL = "https://api.core.ac.uk/v3/search/works/"  # 末尾需要斜杠

    def _build_query(self, strategy: dict) -> str:
        """Build CORE search query from strategy."""
        keywords = strategy.get("keywords", [])
        return " ".join(keywords)

    def _parse_response(self, data: dict) -> List[Paper]:
        """Parse CORE JSON response to Paper list."""
        papers = []

        for item in data.get("results", []):
            paper_id = f"core:{item.get('id', '')}"

            # Extract authors
            authors = [a.get("name", "") for a in item.get("authors", [])]

            # Extract date
            date = item.get("publishedDate", "")[:10] if item.get("publishedDate") else ""

            # Get PDF URL
            pdf_url = None
            for link in item.get("links", []):
                if link.get("type") == "download":
                    pdf_url = link.get("url")
                    break

            papers.append(Paper(
                id=paper_id,
                title=item.get("title", ""),
                authors=authors,
                abstract=item.get("abstract", ""),
                source="core",
                url=item.get("downloadUrl", "") or item.get("sourceFulltextUrls", [""])[0] if item.get("sourceFulltextUrls") else "",
                date=date,
                citation_count=None,
                pdf_url=pdf_url
            ))

        return papers

    async def search(self, strategy: dict, max_results: int = 30, api_key: str = "") -> List[Paper]:
        """Search CORE for open access papers."""
        if not api_key:
            print("CORE search skipped: no API key provided")
            return []

        query = self._build_query(strategy)
        params = {
            "q": query,
            "limit": max_results
        }

        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(self.BASE_URL, params=params, headers=headers, timeout=60.0)
                response.raise_for_status()
            return self._parse_response(response.json())
        except Exception as e:
            print(f"CORE search failed: {e}")
            return []


async def search_papers(strategy: dict, config) -> List[Paper]:
    """Search papers from all enabled sources."""
    all_papers = []

    if config.sources.arxiv.enabled:
        searcher = ArxivSearcher()
        papers = await searcher.search(
            strategy,
            max_results=config.search.max_results_per_source
        )
        all_papers.extend(papers)

    if config.sources.semantic_scholar.enabled:
        searcher = SemanticScholarSearcher()
        papers = await searcher.search(
            strategy,
            max_results=config.search.max_results_per_source,
            api_key=config.sources.semantic_scholar.api_key
        )
        all_papers.extend(papers)

    if config.sources.google_scholar.enabled:
        searcher = GoogleScholarSearcher()
        papers = await searcher.search(
            strategy,
            max_results=config.search.max_results_per_source,
            serpapi_key=config.sources.google_scholar.serpapi_key
        )
        all_papers.extend(papers)

    if config.sources.dblp.enabled:
        searcher = DBLPSearcher()
        papers = await searcher.search(
            strategy,
            max_results=config.search.max_results_per_source
        )
        all_papers.extend(papers)

    if config.sources.crossref.enabled:
        searcher = CrossRefSearcher()
        papers = await searcher.search(
            strategy,
            max_results=config.search.max_results_per_source,
            mailto=config.sources.crossref.mailto
        )
        all_papers.extend(papers)

    if config.sources.core.enabled:
        searcher = CORESearcher()
        papers = await searcher.search(
            strategy,
            max_results=config.search.max_results_per_source,
            api_key=config.sources.core.api_key
        )
        all_papers.extend(papers)

    return all_papers


import argparse
import asyncio


async def main():
    parser = argparse.ArgumentParser(description="Search papers from multiple sources")
    parser.add_argument("--strategy", required=True, help="Path to strategy JSON file")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    parser.add_argument("--output", required=True, help="Output JSON file path")

    args = parser.parse_args()

    # Load strategy
    with open(args.strategy, 'r', encoding='utf-8') as f:
        strategy = json.load(f)

    # Load config
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scripts.config import load_config
    config = load_config(args.config)

    # Search papers
    papers = await search_papers(strategy, config)

    # Convert to dict for JSON serialization
    papers_dict = [
        {
            "id": p.id,
            "title": p.title,
            "authors": p.authors,
            "abstract": p.abstract,
            "source": p.source,
            "url": p.url,
            "date": p.date,
            "citation_count": p.citation_count,
            "pdf_url": p.pdf_url
        }
        for p in papers
    ]

    # Save results
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(papers_dict, f, ensure_ascii=False, indent=2)

    print(f"Found {len(papers)} papers, saved to {args.output}")


if __name__ == "__main__":
    asyncio.run(main())

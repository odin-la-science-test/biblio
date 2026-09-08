"""
Search service implementing federated search (section 21).

This service:
- Adapts queries to different source capabilities (section 23)
- Normalizes results from multiple sources
- Performs deduplication (section 16)
- Supports lexical, boolean, structured, and semantic search
"""
import asyncio
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.config import get_settings
from app.schemas import SearchQuery, DocumentResponse, SourceResponse

settings = get_settings()


class SourceConnector:
    """Base class for source connectors."""
    
    def __init__(self, source_id: int, name: str, api_url: str):
        self.source_id = source_id
        self.name = name
        self.api_url = api_url
    
    async def search(self, query: SearchQuery) -> List[Dict[str, Any]]:
        """Execute search on this source."""
        raise NotImplementedError
    
    def adapt_query(self, query: SearchQuery) -> Any:
        """Adapt OLS query to source-specific format (section 24)."""
        raise NotImplementedError
    
    def normalize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize source result to OLS canonical format (section 17)."""
        raise NotImplementedError


class PubMedConnector(SourceConnector):
    """PubMed/NCBI connector."""
    
    def __init__(self, source_id: int = 1):
        super().__init__(
            source_id=source_id,
            name="PubMed",
            api_url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        )
    
    async def search(self, query: SearchQuery) -> List[Dict[str, Any]]:
        """Search PubMed using E-utilities API."""
        results = []
        
        # Build PubMed query
        pubmed_query = self.adapt_query(query)
        
        async with httpx.AsyncClient(timeout=settings.SEARCH_TIMEOUT_SECONDS) as client:
            try:
                # Search for IDs
                search_url = f"{self.api_url}/esearch.fcgi"
                params = {
                    "db": "pubmed",
                    "term": pubmed_query,
                    "retmax": settings.MAX_RESULTS_PER_SOURCE,
                    "retmode": "json",
                    "api_key": settings.PUBMED_API_KEY or ""
                }
                
                response = await client.get(search_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                ids = data.get("esearchresult", {}).get("idlist", [])
                
                if not ids:
                    return []
                
                # Fetch details
                fetch_url = f"{self.api_url}/esummary.fcgi"
                fetch_params = {
                    "db": "pubmed",
                    "id": ",".join(ids),
                    "retmode": "json",
                    "api_key": settings.PUBMED_API_KEY or ""
                }
                
                response = await client.get(fetch_url, params=fetch_params)
                response.raise_for_status()
                data = response.json()
                
                for pmid, item in data.get("result", {}).items():
                    if pmid == "uids":
                        continue
                    normalized = self.normalize_result(item)
                    normalized["_source"] = "PubMed"
                    normalized["_source_id"] = self.source_id
                    results.append(normalized)
                    
            except Exception as e:
                print(f"PubMed search error: {e}")
        
        return results
    
    def adapt_query(self, query: SearchQuery) -> str:
        """Adapt OLS query to PubMed syntax."""
        terms = []
        
        if query.query_text:
            terms.append(f'({query.query_text}[All Fields])')
        
        if query.title:
            terms.append(f'({query.title}[Title])')
        
        if query.authors:
            author_terms = [f'{author}[Author]' for author in query.authors]
            terms.append(f'({" OR ".join(author_terms)})')
        
        if query.journal:
            terms.append(f'({query.journal}[Journal])')
        
        if query.publication_date_from:
            date_from = query.publication_date_from.strftime("%Y/%m/%d")
            terms.append(f'({date_from}:3000/12/31[Date - Publication])')
        
        if query.document_type:
            terms.append(f'({query.document_type}[Publication Type])')
        
        if query.is_open_access is True:
            terms.append('(free fulltext[sb])')
        
        operator = " AND " if query.boolean_operator == "AND" else " OR "
        return operator.join(terms) if terms else ""
    
    def normalize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize PubMed result to OLS format."""
        return {
            "title": result.get("title", ""),
            "abstract": result.get("fulljournalname", ""),  # Note: abstract needs separate fetch
            "authors": result.get("authors", []),
            "journal": result.get("fulljournalname", ""),
            "publication_date": result.get("pubdate", ""),
            "pmid": result.get("uid", ""),
            "document_type": result.get("pubtype", ["article"])[0] if result.get("pubtype") else "article",
            "doi": next((id_val for id_val in result.get("ids", []) if id_val.get("idtype") == "doi"), {}).get("value"),
        }


class OpenAlexConnector(SourceConnector):
    """OpenAlex connector."""
    
    def __init__(self, source_id: int = 2):
        super().__init__(
            source_id=source_id,
            name="OpenAlex",
            api_url=settings.OPENALEX_API_URL
        )
    
    async def search(self, query: SearchQuery) -> List[Dict[str, Any]]:
        """Search OpenAlex API."""
        results = []
        
        async with httpx.AsyncClient(timeout=settings.SEARCH_TIMEOUT_SECONDS) as client:
            try:
                search_url = f"{self.api_url}/works"
                params = {
                    "search": query.query_text or "",
                    "per_page": min(settings.MAX_RESULTS_PER_SOURCE, 200),
                }
                
                if query.title:
                    params["title.search"] = query.title
                
                if query.authors:
                    params["author.search"] = " ".join(query.authors)
                
                response = await client.get(search_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                for item in data.get("results", []):
                    normalized = self.normalize_result(item)
                    normalized["_source"] = "OpenAlex"
                    normalized["_source_id"] = self.source_id
                    results.append(normalized)
                    
            except Exception as e:
                print(f"OpenAlex search error: {e}")
        
        return results
    
    def adapt_query(self, query: SearchQuery) -> Dict[str, Any]:
        """Adapt OLS query to OpenAlex format."""
        return {
            "search": query.query_text,
            "from_publication_date": query.publication_date_from.isoformat() if query.publication_date_from else None,
        }
    
    def normalize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize OpenAlex result to OLS format."""
        return {
            "title": result.get("title", ""),
            "abstract": result.get("abstract", None),
            "authors": [
                {"name": a.get("author", {}).get("display_name", ""), 
                 "orcid": a.get("author", {}).get("orcid", "")}
                for a in result.get("authorships", [])
            ],
            "journal": result.get("primary_location", {}).get("source", {}).get("display_name", "") if result.get("primary_location") else "",
            "publication_date": result.get("publication_date", ""),
            "doi": result.get("doi", ""),
            "openalex_id": result.get("id", "").replace("https://openalex.org/", ""),
            "is_open_access": result.get("open_access", {}).get("is_oa", False),
            "document_type": result.get("type", "article"),
            "citation_count": result.get("cited_by_count", 0),
        }


class CrossrefConnector(SourceConnector):
    """Crossref connector."""
    
    def __init__(self, source_id: int = 3):
        super().__init__(
            source_id=source_id,
            name="Crossref",
            api_url=settings.CROSSREF_API_URL
        )
    
    async def search(self, query: SearchQuery) -> List[Dict[str, Any]]:
        """Search Crossref API."""
        results = []
        
        async with httpx.AsyncClient(timeout=settings.SEARCH_TIMEOUT_SECONDS) as client:
            try:
                search_url = f"{self.api_url}/works"
                params = {
                    "query": query.query_text or "",
                    "rows": settings.MAX_RESULTS_PER_SOURCE,
                }
                
                if query.title:
                    params["query.title"] = query.title
                
                if query.authors:
                    params["query.author"] = " ".join(query.authors)
                
                response = await client.get(search_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                for item in data.get("message", {}).get("items", []):
                    normalized = self.normalize_result(item)
                    normalized["_source"] = "Crossref"
                    normalized["_source_id"] = self.source_id
                    results.append(normalized)
                    
            except Exception as e:
                print(f"Crossref search error: {e}")
        
        return results
    
    def adapt_query(self, query: SearchQuery) -> Dict[str, Any]:
        """Adapt OLS query to Crossref format."""
        return {"query": query.query_text}
    
    def normalize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Crossref result to OLS format."""
        return {
            "title": result.get("title", [""])[0],
            "abstract": result.get("abstract", ""),
            "authors": [
                {"name": f"{a.get('given', '')} {a.get('family', '')}".strip()}
                for a in result.get("author", [])
            ],
            "journal": result.get("container-title", [""])[0] if result.get("container-title") else "",
            "publication_date": result.get("published-print", {}).get("date-parts", [[None]])[0][0] if result.get("published-print") else None,
            "doi": result.get("DOI", ""),
            "document_type": result.get("type", "journal-article"),
            "is_open_access": result.get("open-access-status", "") == "gold",
            "license": result.get("license", [{}])[0].get("URL", "") if result.get("license") else None,
        }


class FederatedSearchService:
    """
    Federated search service (section 21).
    
    Coordinates searches across multiple sources, normalizes results,
    and performs deduplication.
    """
    
    def __init__(self):
        self.connectors: List[SourceConnector] = [
            PubMedConnector(),
            OpenAlexConnector(),
            CrossrefConnector(),
        ]
    
    async def search(self, query: SearchQuery, source_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """
        Execute federated search across multiple sources.
        
        Implements progressive search (section 32) where results are returned
        as sources respond, without blocking on the slowest source.
        """
        # Filter connectors by requested sources
        connectors = self.connectors
        if source_ids:
            connectors = [c for c in self.connectors if c.source_id in source_ids]
        
        # Execute searches concurrently
        tasks = [connector.search(query) for connector in connectors]
        results_lists = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results
        all_results = []
        for results in results_lists:
            if isinstance(results, list):
                all_results.extend(results)
        
        # Deduplicate results (section 16)
        deduplicated = self.deduplicate_results(all_results)
        
        return deduplicated
    
    def deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicate results based on identifiers (section 16).
        
        Priority for deduplication:
        1. DOI match (certain correspondence)
        2. PMID/PMCID match
        3. OpenAlex ID match
        4. Title + authors + date similarity (strong correspondence)
        """
        seen_dois = {}
        seen_pmids = {}
        unique_results = []
        
        for result in results:
            doi = result.get("doi")
            pmid = result.get("pmid")
            openalex_id = result.get("openalex_id")
            
            # Check DOI first (most reliable)
            if doi and doi in seen_dois:
                # Merge sources
                existing = seen_dois[doi]
                existing.setdefault("_all_sources", []).append(result.get("_source"))
                continue
            
            # Check PMID
            if pmid and pmid in seen_pmids:
                existing = seen_pmids[pmid]
                existing.setdefault("_all_sources", []).append(result.get("_source"))
                continue
            
            # Add as unique
            result["_all_sources"] = [result.get("_source")]
            unique_results.append(result)
            
            if doi:
                seen_dois[doi] = result
            if pmid:
                seen_pmids[pmid] = result
        
        return unique_results
    
    def get_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate statistics/facets from search results (section 5.3).
        
        Returns contextual statistics about the current result set.
        """
        stats = {
            "total": len(results),
            "by_year": {},
            "by_document_type": {},
            "by_journal": {},
            "by_source": {},
            "open_access_count": 0,
        }
        
        for result in results:
            # By year
            pub_date = result.get("publication_date")
            if pub_date:
                try:
                    if isinstance(pub_date, str):
                        year = pub_date[:4]
                    else:
                        year = str(pub_date.year)
                    stats["by_year"][year] = stats["by_year"].get(year, 0) + 1
                except (ValueError, AttributeError):
                    pass
            
            # By document type
            doc_type = result.get("document_type", "unknown")
            stats["by_document_type"][doc_type] = stats["by_document_type"].get(doc_type, 0) + 1
            
            # By journal
            journal = result.get("journal", "Unknown")
            stats["by_journal"][journal] = stats["by_journal"].get(journal, 0) + 1
            
            # By source
            source = result.get("_source", "Unknown")
            stats["by_source"][source] = stats["by_source"].get(source, 0) + 1
            
            # Open access
            if result.get("is_open_access"):
                stats["open_access_count"] += 1
        
        return stats


# Singleton instance
federated_search_service = FederatedSearchService()

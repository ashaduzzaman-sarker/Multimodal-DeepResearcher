import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

class DataSource:
    """Base class for data sources"""
    
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
    
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for information"""
        raise NotImplementedError

class GoogleSearchSource(DataSource):
    """Google Custom Search API source"""
    
    def __init__(self, session: aiohttp.ClientSession, api_key: str, cse_id: str):
        super().__init__(session)
        self.api_key = api_key
        self.cse_id = cse_id
        self.base_url = "https://customsearch.googleapis.com/customsearch/v1"
    
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search Google for information"""
        results = []
        
        try:
            params = {
                'key': self.api_key,
                'cx': self.cse_id,
                'q': query,
                'num': min(max_results, 10)
            }
            
            async with self.session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for item in data.get('items', []):
                        results.append({
                            'title': item.get('title', ''),
                            'url': item.get('link', ''),
                            'snippet': item.get('snippet', ''),
                            'source': 'google'
                        })
        
        except Exception as e:
            print(f"Google search error: {e}")
        
        return results

class ArxivSource(DataSource):
    """ArXiv academic papers source"""
    
    def __init__(self, session: aiohttp.ClientSession):
        super().__init__(session)
        self.base_url = "http://export.arxiv.org/api/query"
    
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search ArXiv for academic papers"""
        results = []
        
        try:
            params = {
                'search_query': f'all:{query}',
                'start': 0,
                'max_results': max_results,
                'sortBy': 'relevance',
                'sortOrder': 'descending'
            }
            
            async with self.session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    content = await response.text()
                    root = ET.fromstring(content)
                    
                    # Parse ArXiv XML response
                    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                        title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                        summary_elem = entry.find('{http://www.w3.org/2005/Atom}summary')
                        link_elem = entry.find('{http://www.w3.org/2005/Atom}id')
                        
                        if title_elem is not None and summary_elem is not None:
                            results.append({
                                'title': title_elem.text.strip(),
                                'url': link_elem.text if link_elem is not None else '',
                                'snippet': summary_elem.text.strip()[:300] + '...',
                                'source': 'arxiv'
                            })
        
        except Exception as e:
            print(f"ArXiv search error: {e}")
        
        return results

class WikipediaSource(DataSource):
    """Wikipedia source"""
    
    def __init__(self, session: aiohttp.ClientSession):
        super().__init__(session)
        self.base_url = "https://en.wikipedia.org/api/rest_v1/page/summary"
    
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search Wikipedia for information"""
        results = []
        
        try:
            # First, search for pages
            search_url = "https://en.wikipedia.org/w/api.php"
            search_params = {
                'action': 'opensearch',
                'search': query,
                'limit': max_results,
                'format': 'json'
            }
            
            async with self.session.get(search_url, params=search_params) as response:
                if response.status == 200:
                    search_data = await response.json()
                    titles = search_data[1] if len(search_data) > 1 else []
                    
                    # Get summary for each title
                    for title in titles[:max_results]:
                        summary_url = f"{self.base_url}/{quote_plus(title)}"
                        
                        try:
                            async with self.session.get(summary_url) as summary_response:
                                if summary_response.status == 200:
                                    summary_data = await summary_response.json()
                                    
                                    results.append({
                                        'title': summary_data.get('title', title),
                                        'url': summary_data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                                        'snippet': summary_data.get('extract', ''),
                                        'source': 'wikipedia'
                                    })
                        except:
                            continue
        
        except Exception as e:
            print(f"Wikipedia search error: {e}")
        
        return results
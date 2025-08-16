import asyncio
import os
from typing import List, Dict, Any
from ..data.sources import GoogleSearchSource, ArxivSource, WikipediaSource
from ..utils.cache import cache_result
from .base import BaseAgent
import aiohttp

class ResearchAgent(BaseAgent):
    """Agent responsible for researching topics"""
    
    def __init__(self, config):
        super().__init__(config)
        self.max_sources = config.research.max_sources_per_query
        self.concurrent_requests = config.research.concurrent_requests
    
    async def process(self, topic: str) -> Dict[str, Any]:
        """Research a given topic comprehensively"""
        
        # Generate search queries
        search_queries = await self._generate_search_queries(topic)
        
        # Search all sources concurrently
        all_results = []
        async with aiohttp.ClientSession() as session:
            # Initialize data sources
            sources = await self._initialize_sources(session)
            
            # Search with all queries and sources
            tasks = []
            for query in search_queries:
                for source in sources:
                    task = self._search_with_source(source, query)
                    tasks.append(task)
            
            # Limit concurrent requests
            semaphore = asyncio.Semaphore(self.concurrent_requests)
            async def bounded_search(task):
                async with semaphore:
                    return await task
            
            results = await asyncio.gather(*[bounded_search(task) for task in tasks])
            
            # Flatten results
            for result_list in results:
                all_results.extend(result_list)
        
        # Remove duplicates and rank results
        filtered_results = await self._filter_and_rank_results(all_results, topic)
        
        # Synthesize research findings
        synthesis = await self._synthesize_research(filtered_results, topic)
        
        return {
            'topic': topic,
            'search_queries': search_queries,
            'raw_results': filtered_results,
            'synthesis': synthesis,
            'source_count': len(filtered_results),
            'sources_breakdown': self._count_sources(filtered_results)
        }
    
    async def _generate_search_queries(self, topic: str) -> List[str]:
        """Generate multiple search queries for comprehensive research"""
        
        messages = [
            {
                "role": "system",
                "content": """You are an expert researcher. Generate 5-7 diverse search queries that will comprehensively research the given topic. 
                
Include queries that cover:
1. Basic definitions and overview
2. Recent developments and trends
3. Key statistics and data
4. Expert opinions and analysis
5. Practical applications or implications
6. Comparative analysis
7. Future outlook

Return only the queries, one per line, without numbering."""
            },
            {
                "role": "user",
                "content": f"Generate comprehensive search queries for researching: {topic}"
            }
        ]
        
        response = await self._make_llm_request(messages)
        queries = [q.strip() for q in response.split('\n') if q.strip()]
        
        # Ensure we have the original topic as a query too
        if topic not in queries:
            queries.insert(0, topic)
        
        return queries[:7]  # Limit to 7 queries max
    
    async def _initialize_sources(self, session: aiohttp.ClientSession) -> List:
        """Initialize all data sources"""
        sources = []
        
        # Google Search (if API keys available)
        google_api_key = os.getenv('GOOGLE_API_KEY')
        google_cse_id = os.getenv('GOOGLE_CSE_ID')
        if google_api_key and google_cse_id:
            sources.append(GoogleSearchSource(session, google_api_key, google_cse_id))
        
        # ArXiv (always available)
        sources.append(ArxivSource(session))
        
        # Wikipedia (always available)
        sources.append(WikipediaSource(session))
        
        return sources
    
    async def _search_with_source(self, source, query: str) -> List[Dict[str, Any]]:
        """Search with a specific source"""
        try:
            return await source.search(query, max_results=5)
        except Exception as e:
            print(f"Search error with {type(source).__name__}: {e}")
            return []
    
    async def _filter_and_rank_results(self, results: List[Dict[str, Any]], topic: str) -> List[Dict[str, Any]]:
        """Remove duplicates and rank results by relevance"""
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        # Rank results using LLM
        if len(unique_results) > 10:
            ranked_results = await self._rank_results_by_relevance(unique_results, topic)
            return ranked_results[:self.max_sources]
        
        return unique_results
    
    async def _rank_results_by_relevance(self, results: List[Dict[str, Any]], topic: str) -> List[Dict[str, Any]]:
        """Rank search results by relevance to topic"""
        
        # Create a summary of all results for ranking
        results_summary = "\n\n".join([
            f"Result {i+1}:\nTitle: {r.get('title', 'No title')}\nSnippet: {r.get('snippet', 'No snippet')[:200]}"
            for i, r in enumerate(results)
        ])
        
        messages = [
            {
                "role": "system", 
                "content": """You are evaluating search results for relevance to a research topic. 
                
Rate each result on a scale of 1-10 for relevance, considering:
- How directly related the content is to the topic
- Quality and credibility of the source
- Uniqueness of information provided

Return only a list of numbers (the rankings) separated by commas, in the same order as the results."""
            },
            {
                "role": "user",
                "content": f"Topic: {topic}\n\nResults to rank:\n{results_summary}\n\nProvide relevance scores (1-10) for each result:"
            }
        ]
        
        try:
            response = await self._make_llm_request(messages)
            scores = [float(x.strip()) for x in response.split(',') if x.strip()]
            
            # Pair results with scores and sort
            scored_results = list(zip(results, scores))
            scored_results.sort(key=lambda x: x[1], reverse=True)
            
            return [result for result, score in scored_results]
            
        except Exception as e:
            print(f"Ranking error: {e}")
            return results  # Return original order if ranking fails
    
    async def _synthesize_research(self, results: List[Dict[str, Any]], topic: str) -> str:
        """Synthesize research findings into a coherent summary"""
        
        # Create research summary
        research_content = "\n\n".join([
            f"Source: {r.get('source', 'unknown')}\nTitle: {r.get('title', 'No title')}\nContent: {r.get('snippet', 'No content')}"
            for r in results[:15]  # Limit to prevent token overflow
        ])
        
        messages = [
            {
                "role": "system",
                "content": """You are a research analyst synthesizing information from multiple sources. 

Create a comprehensive but concise synthesis that:
1. Identifies the main themes and findings
2. Notes areas of consensus and disagreement
3. Highlights the most important insights
4. Identifies gaps where more research might be needed
5. Maintains objectivity and cites the general types of sources used

Keep the synthesis focused and well-structured."""
            },
            {
                "role": "user", 
                "content": f"Synthesize this research on '{topic}':\n\n{research_content}"
            }
        ]
        
        return await self._make_llm_request(messages)
    
    def _count_sources(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count results by source type"""
        counts = {}
        for result in results:
            source = result.get('source', 'unknown')
            counts[source] = counts.get(source, 0) + 1
        return counts

import asyncio

class ResearchAgent:
    def __init__(self, config):
        self.config = config
        self.search_engines = ["google", "arxiv", "wikipedia"]

    async def research_topic(self, topic):
        """Find information about a topic"""
        results = []
        
        # Search multiple sources
        for engine in self.search_engines:
            search_results = await self.search(topic, engine)
            results.extend(search_results)
        
        # Remove duplicates and rank by quality
        filtered_results = self.filter_and_rank(results)
        
        return filtered_results

    async def search(self, topic, engine):
        """Mock search function that simulates an API call"""
        print(f"[{engine} Searching for: {topic}]")
        await asyncio.sleep(0.5)  # simulate network delay
        return [f"{engine} result 1 for {topic}", f"{engine} result 2 for {topic}"]

    def filter_and_rank(self, results):
        """Remove duplicates and sort alphabetically (as mock ranking)"""
        unique_results = list(set(results))  # remove duplicates
        unique_results.sort()  # mock 'ranking'
        return unique_results


# # -----------------
# # Running the agent
# # -----------------
# async def main():
#     agent = ResearchAgent(config={"language": "en"})
#     topic = "Quantum Computing"
#     final_results = await agent.research_topic(topic)
    
#     print("\n--- Final Results ---")
#     for r in final_results:
#         print(r)

# # Run the async program
# asyncio.run(main())

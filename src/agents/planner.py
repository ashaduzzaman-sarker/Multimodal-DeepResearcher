from typing import List, Dict, Any
from .base import BaseAgent
import json

class PlanningAgent(BaseAgent):
    """Agent responsible for planning report structure"""
    
    async def process(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive report plan"""
        
        topic = research_data['topic']
        synthesis = research_data['synthesis']
        
        # Create report outline
        outline = await self._create_outline(topic, synthesis)
        
        # Plan visualizations
        viz_plan = await self._plan_visualizations(topic, synthesis, outline)
        
        # Estimate content distribution
        content_plan = await self._plan_content_distribution(outline)
        
        return {
            'topic': topic,
            'outline': outline,
            'visualization_plan': viz_plan,
            'content_plan': content_plan,
            'estimated_sections': len(outline),
            'estimated_charts': len(viz_plan)
        }
    
    async def _create_outline(self, topic: str, synthesis: str) -> List[Dict[str, Any]]:
        """Create a detailed report outline"""
        
        messages = [
            {
                "role": "system",
                "content": """You are an expert technical writer creating report outlines. 

Create a detailed outline for a comprehensive research report based on the topic and research synthesis provided. 

Return a JSON array where each section has:
- "title": Section title
- "description": Brief description of what this section will cover
- "key_points": Array of 3-5 key points to address
- "estimated_words": Estimated word count for this section

The report should be well-structured, logical, and comprehensive. Include:
1. Introduction
2. 3-6 main content sections based on research themes
3. Conclusion
4. Optional: Methodology, Future Work, or Recommendations if relevant

Return only valid JSON."""
            },
            {
                "role": "user",
                "content": f"Topic: {topic}\n\nResearch Synthesis:\n{synthesis}\n\nCreate a detailed report outline:"
            }
        ]
        
        response = await self._make_llm_request(messages)
        
        try:
            outline = json.loads(response)
            return outline if isinstance(outline, list) else []
        except json.JSONDecodeError:
            # Fallback basic outline if JSON parsing fails
            return [
                {
                    "title": "Introduction",
                    "description": f"Overview of {topic}",
                    "key_points": ["Background", "Scope", "Objectives"],
                    "estimated_words": 300
                },
                {
                    "title": "Analysis",
                    "description": f"Detailed analysis of {topic}",
                    "key_points": ["Key findings", "Important trends", "Critical insights"],
                    "estimated_words": 500
                },
                {
                    "title": "Conclusion",
                    "description": "Summary and implications",
                    "key_points": ["Summary", "Implications", "Future outlook"],
                    "estimated_words": 250
                }
            ]
    
    async def _plan_visualizations(self, topic: str, synthesis: str, outline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Plan what visualizations would be most effective"""
        
        outline_text = "\n".join([f"{i+1}. {section['title']}: {section['description']}" for i, section in enumerate(outline)])
        
        messages = [
            {
                "role": "system",
                "content": """You are a data visualization expert planning charts for a research report.

Based on the topic, research synthesis, and report outline, suggest visualizations that would enhance the report.

For each suggested visualization, provide:
- "type": Chart type (bar, line, pie, scatter, heatmap, network, etc.)
- "title": Descriptive title for the chart
- "description": What the chart will show
- "section": Which report section it belongs in
- "data_requirements": What kind of data would be needed
- "priority": High, Medium, or Low

Focus on visualizations that:
1. Support key arguments in the report
2. Make complex information clearer
3. Are feasible to create from research data
4. Add genuine value to understanding

Return a JSON array of visualization suggestions. Aim for 3-6 high-quality suggestions."""
            },
            {
                "role": "user",
                "content": f"Topic: {topic}\n\nSynthesis: {synthesis[:1000]}...\n\nOutline:\n{outline_text}\n\nSuggest effective visualizations:"
            }
        ]
        
        response = await self._make_llm_request(messages)
        
        try:
            viz_plan = json.loads(response)
            return viz_plan if isinstance(viz_plan, list) else []
        except json.JSONDecodeError:
            return []
    
    async def _plan_content_distribution(self, outline: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Plan how content will be distributed across sections"""
        
        total_words = sum(section.get('estimated_words', 300) for section in outline)
        
        content_plan = {
            'total_estimated_words': total_words,
            'section_breakdown': {},
            'writing_priorities': []
        }
        
        for i, section in enumerate(outline):
            section_words = section.get('estimated_words', 300)
            content_plan['section_breakdown'][section['title']] = {
                'words': section_words,
                'percentage': round((section_words / total_words) * 100, 1),
                'priority': 'High' if i in [0, len(outline)-1] else 'Medium'
            }
        
        return content_plan
from typing import Dict, Any, List
from .base import BaseAgent
import json
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

class GenerationAgent(BaseAgent):
    async def process(self, research_data: Dict[str, Any], plan: Dict[str, Any], charts: Dict[str, Any]) -> Dict[str, Any]:
        topic = research_data['topic']
        outline = plan['outline']
        chart_list = charts.get('charts', [])
        
        sections = []
        for i, section_plan in enumerate(outline):
            section_content = await self._generate_section(
                section_plan, research_data, chart_list, i
            )
            sections.append(section_content)
        
        report = await self._assemble_report(topic, sections, chart_list)
        metadata = self._create_metadata(research_data, plan, charts, report)
        
        return {
            'report': report,
            'sections': sections,
            'metadata': metadata,
            'word_count': self._count_words(report),
            'chart_references': self._count_chart_references(report)
        }

    async def _generate_section(self, section_plan: Dict[str, Any], research_data: Dict[str, Any],
                              charts: List[Dict[str, Any]], section_index: int) -> Dict[str, Any]:
        title = section_plan['title']
        description = section_plan['description']
        key_points = section_plan.get('key_points', [])
        target_words = section_plan.get('estimated_words', 150)
        
        relevant_charts = self._find_relevant_charts(title, description, charts)
        content = await self._generate_section_content(
            title, description, key_points, research_data, relevant_charts, target_words
        )
        
        return {
            'title': title,
            'content': content,
            'charts': relevant_charts,
            'word_count': self._count_words(content),
            'section_index': section_index
        }

    async def _generate_section_content(self, title: str, description: str, key_points: List[str],
                                      research_data: Dict[str, Any], charts: List[Dict[str, Any]],
                                      target_words: int) -> str:
        research_context = research_data.get('synthesis', '')
        topic = research_data.get('topic', '')
        
        chart_context = ""
        if charts:
            chart_descriptions = []
            for chart in charts:
                chart_desc = f"Chart: {chart.get('title', 'Untitled')} - {chart.get('description', 'No description')}"
                chart_descriptions.append(chart_desc)
            chart_context = f"\n\nAvailable visualizations to reference:\n" + "\n".join(chart_descriptions)
        
        key_points_text = "\n".join([f"- {point}" for point in key_points])
        
        messages = [
            {
                "role": "system",
                "content": f"""You are an expert technical writer creating a section for a research report.
Write content that:
1. Is approximately {target_words} words long
2. Uses clear, professional language
3. References research findings accurately
4. Integrates chart references naturally ([See Chart: Chart Title])
5. Follows academic writing standards
6. Avoids lists unless appropriate
Structure with clear paragraphs and logical flow."""
            },
            {
                "role": "user",
                "content": f"""Section Title: {title}
Section Purpose: {description}
Key Points:
{key_points_text}
Research Context:
{research_context[:1500]}...
{chart_context}
Write the section content:"""
            }
        ]
        
        return await self._make_llm_request(messages)

    def _find_relevant_charts(self, section_title: str, section_description: str,
                            charts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        relevant_charts = []
        for chart in charts:
            chart_section = chart.get('section', '').lower()
            chart_title = chart.get('title', '').lower()
            chart_desc = chart.get('description', '').lower()
            section_keywords = section_title.lower().split() + section_description.lower().split()
            relevance_score = 0
            for keyword in section_keywords:
                if len(keyword) > 3:
                    if keyword in chart_title:
                        relevance_score += 3
                    elif keyword in chart_desc:
                        relevance_score += 2
                    elif keyword in chart_section:
                        relevance_score += 1
            if relevance_score > 0:
                chart['relevance_score'] = relevance_score
                relevant_charts.append(chart)
        relevant_charts.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        return relevant_charts[:2]

    async def _assemble_report(self, topic: str, sections: List[Dict[str, Any]],
                             charts: List[Dict[str, Any]]) -> str:
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('report_template.md')
        
        toc = []
        content = []
        for i, section in enumerate(sections):
            toc.append(f"{i+1}. [{section['title']}](#{section['title'].lower().replace(' ', '-')})")
            section_content = f"## {section['title']}\n\n{section['content']}\n\n"
            for chart in section.get('charts', []):
                if chart.get('file_path'):
                    section_content += f"![{chart['title']}]({chart['file_path']})\n\n"
                    section_content += f"*{chart.get('description', '')}*\n\n"
            content.append(section_content)
        
        unreferenced_charts = self._find_unreferenced_charts(charts, ''.join(content))
        if unreferenced_charts:
            appendix = "## Additional Visualizations\n\n"
            for chart in unreferenced_charts:
                if chart.get('file_path'):
                    appendix += f"### {chart['title']}\n\n"
                    appendix += f"![{chart['title']}]({chart['file_path']})\n\n"
                    appendix += f"{chart.get('description', '')}\n\n"
            content.append(appendix)
        
        return template.render(
            topic=topic,
            generation_date=pd.Timestamp.now().strftime('%B %d, %Y'),
            toc='\n'.join(toc),
            content='\n'.join(content)
        )

    def _find_unreferenced_charts(self, all_charts: List[Dict[str, Any]], report_content: str) -> List[Dict[str, Any]]:
        unreferenced = []
        for chart in all_charts:
            chart_title = chart.get('title', '')
            if chart_title and f"[See Chart: {chart_title}]" not in report_content:
                unreferenced.append(chart)
        return unreferenced

    def _create_metadata(self, research_data: Dict[str, Any], plan: Dict[str, Any],
                       charts: Dict[str, Any], report: str) -> Dict[str, Any]:
        return {
            'topic': research_data.get('topic'),
            'generation_date': pd.Timestamp.now().isoformat(),
            'word_count': self._count_words(report),
            'section_count': len(plan.get('outline', [])),
            'chart_count': len(charts.get('charts', [])),
            'source_count': research_data.get('source_count', 0),
            'research_sources': research_data.get('sources_breakdown', {}),
            'estimated_reading_time_minutes': max(1, self._count_words(report) // 200)
        }

    def _count_words(self, text: str) -> int:
        return len(text.split()) if text else 0

    def _count_chart_references(self, text: str) -> int:
        return text.count('[See Chart:') if text else 0
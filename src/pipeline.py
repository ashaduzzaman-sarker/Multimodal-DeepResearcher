import asyncio
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from .agents.researcher import ResearchAgent
from .agents.planner import PlanningAgent
from .agents.visualization_agent import VisualizationAgent
from .agents.generator import GenerationAgent
from .utils.logger import setup_logger
from .utils.config import SystemConfig
import markdown
import shutil
import json

class MultimodalReportPipeline:
    def __init__(self, config: SystemConfig):
        self.config = config
        self.logger = setup_logger("pipeline", config.system.get('log_level', 'INFO'))
        self.research_agent = ResearchAgent(config)
        self.planning_agent = PlanningAgent(config)
        self.visualization_agent = VisualizationAgent(config)
        self.generation_agent = GenerationAgent(config)

    async def generate_report(self, topic: str, style: str = "academic") -> Dict[str, Any]:
        self.logger.info(f"🚀 Starting report generation for: {topic} (style: {style})")
        start_time = datetime.now()
        
        try:
            self.config.visualization.style_template = style
            research_data = await self.research_agent.process(topic)
            self.logger.info(f"✅ Research complete: {research_data['source_count']} sources")
            
            plan = await self.planning_agent.process(research_data)
            self.logger.info(f"✅ Planning complete: {plan['estimated_sections']} sections")
            
            charts = await self.visualization_agent.process(research_data, plan)
            self.logger.info(f"✅ Visualization complete: {charts['chart_count']} charts")
            
            report_data = await self.generation_agent.process(research_data, plan, charts)
            self.logger.info(f"✅ Report complete: {report_data['word_count']} words")
            
            total_time = datetime.now() - start_time
            results = {
                'topic': topic,
                'style': style,
                'research_data': research_data,
                'plan': plan,
                'charts': charts,
                'report': report_data,
                'generation_time_seconds': total_time.total_seconds(),
                'timestamp': start_time.isoformat(),
                'success': True
            }
            self.logger.info(f"🎉 Report generation complete in {total_time.total_seconds():.1f}s")
            return results
        except Exception as e:
            self.logger.error(f"❌ Report generation failed: {e}")
            return {
                'topic': topic,
                'success': False,
                'error': str(e),
                'generation_time_seconds': (datetime.now() - start_time).total_seconds()
            }

    async def save_results(self, results: Dict[str, Any], output_dir: Optional[str] = None) -> str:
        if not results.get('success', False):
            self.logger.error("Cannot save failed generation results")
            return ""
        
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"outputs/report_{timestamp}"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        report_content = results['report']['report']
        with open(output_path / "final_report.md", 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        html_content = self._markdown_to_html(report_content)
        with open(output_path / "final_report.html", 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        with open(output_path / "research_data.json", 'w', encoding='utf-8') as f:
            json.dump(results['research_data'], f, indent=2, ensure_ascii=False)
        
        with open(output_path / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(results['report']['metadata'], f, indent=2, ensure_ascii=False)
        
        charts_dir = output_path / "charts"
        charts_dir.mkdir(exist_ok=True)
        for chart in results['charts'].get('charts', []):
            if chart.get('file_path'):
                chart_file = Path(chart['file_path'])
                if chart_file.exists():
                    new_path = charts_dir / chart_file.name
                    shutil.copy2(chart_file, new_path)
                    old_path = str(chart_file)
                    new_relative_path = f"charts/{chart_file.name}"
                    report_content = report_content.replace(old_path, new_relative_path)
        
        with open(output_path / "final_report.md", 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"✅ Results saved to {output_path}")
        return str(output_path)

    def _markdown_to_html(self, markdown_content: str) -> str:
        html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Report</title>
    <script src="https://cdn.jsdelivr.net/npm/plotly.js@2.27.0/dist/plotly.min.js"></script>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.7;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 30px;
            background-color: #f8f9fa;
        }
        .container {
            background-color: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        h1 {
            color: #1a3c6c;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }
        h2 {
            color: #2c5282;
            margin-top: 30px;
        }
        img, .plotly-chart {
            max-width: 100%;
            margin: 20px 0;
            border-radius: 5px;
        }
        .toc {
            background-color: #f1f5f9;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .toc a {
            color: #007bff;
            text-decoration: none;
        }
        .toc a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
{content}
    </div>
</body>
</html>"""
        html_content = markdown.markdown(markdown_content, extensions=['toc', 'tables', 'fenced_code'])
        return html_template.format(content=html_content)
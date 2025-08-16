import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import io
import base64
import plotly.io as pio
from jinja2 import Environment, FileSystemLoader

class ChartGenerator:
    def __init__(self, config):
        self.config = config
        self.resolution = tuple(config.visualization.chart_resolution)
        self.style = config.visualization.style_template
        self.color_palette = config.visualization.color_palette
        plt.style.use('default')
        if self.style == 'academic':
            sns.set_palette("viridis")
            pio.templates.default = "simple_white"
        elif self.style == 'business':
            sns.set_palette("Set2")
            pio.templates.default = "plotly"
        else:
            sns.set_palette("bright")
            pio.templates.default = "plotly_dark"

    async def generate_chart_from_spec(self, chart_spec: Dict[str, Any], data: Optional[Dict] = None) -> Dict[str, Any]:
        chart_type = chart_spec.get('type', 'bar')
        title = chart_spec.get('title', 'Chart')
        description = chart_spec.get('description', '')
        if data is None:
            chart_data = await self._generate_mock_data(chart_spec)
        else:
            chart_data = data
        
        if chart_type == 'bar':
            fig_data = self._create_bar_chart(chart_data, title)
        elif chart_type == 'line':
            fig_data = self._create_line_chart(chart_data, title)
        elif chart_type == 'pie':
            fig_data = self._create_pie_chart(chart_data, title)
        elif chart_type == 'scatter':
            fig_data = self._create_scatter_plot(chart_data, title)
        elif chart_type == 'heatmap':
            fig_data = self._create_heatmap(chart_data, title)
        elif chart_type == 'histogram':
            fig_data = self._create_histogram(chart_data, title)
        else:
            fig_data = self._create_bar_chart(chart_data, title)
        
        return {
            'type': chart_type,
            'title': title,
            'description': description,
            'data': chart_data,
            'chart_info': fig_data,
            'file_path': fig_data.get('file_path'),
            'data_summary': self._summarize_data(chart_data)
        }

    def _create_bar_chart(self, data: Dict[str, Any], title: str) -> Dict[str, Any]:
        categories = data.get('categories', ['A', 'B', 'C', 'D', 'E'])
        values = data.get('values', [10, 15, 12, 8, 20])
        
        fig = px.bar(
            x=categories, y=values,
            labels={'x': data.get('x_label', 'Categories'), 'y': data.get('y_label', 'Values')},
            title=title,
            color=values,
            color_continuous_scale=self.color_palette
        )
        fig.update_layout(
            font=dict(size=14),
            title=dict(x=0.5, xanchor='center'),
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        file_path = self._save_interactive_chart(fig, f"bar_chart_{hash(title)}")
        return {
            'file_path': file_path,
            'chart_type': 'bar',
            'data_points': len(categories)
        }

    def _create_line_chart(self, data: Dict[str, Any], title: str) -> Dict[str, Any]:
        x_values = data.get('x_values', list(range(2020, 2025)))
        y_values = data.get('y_values', [100, 120, 135, 140, 155])
        
        fig = px.line(
            x=x_values, y=y_values,
            labels={'x': data.get('x_label', 'Time'), 'y': data.get('y_label', 'Value')},
            title=title,
            markers=True
        )
        fig.update_traces(line=dict(width=3))
        fig.update_layout(
            font=dict(size=14),
            title=dict(x=0.5, xanchor='center'),
            margin=dict(l=50, r=50, t=80, b=50),
            showlegend=True
        )
        
        file_path = self._save_interactive_chart(fig, f"line_chart_{hash(title)}")
        return {
            'file_path': file_path,
            'chart_type': 'line',
            'data_points': len(x_values)
        }

    def _create_pie_chart(self, data: Dict[str, Any], title: str) -> Dict[str, Any]:
        labels = data.get('labels', ['Category A', 'Category B', 'Category C', 'Category D'])
        sizes = data.get('sizes', [30, 25, 20, 25])
        
        fig = px.pie(
            names=labels, values=sizes,
            title=title,
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            font=dict(size=14),
            title=dict(x=0.5, xanchor='center'),
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        file_path = self._save_interactive_chart(fig, f"pie_chart_{hash(title)}")
        return {
            'file_path': file_path,
            'chart_type': 'pie',
            'data_points': len(labels)
        }

    def _create_scatter_plot(self, data: Dict[str, Any], title: str) -> Dict[str, Any]:
        x_values = data.get('x_values', np.random.normal(50, 15, 50))
        y_values = data.get('y_values', np.random.normal(50, 15, 50))
        
        fig = px.scatter(
            x=x_values, y=y_values,
            labels={'x': data.get('x_label', 'X Values'), 'y': data.get('y_label', 'Y Values')},
            title=title,
            color=y_values,
            color_continuous_scale=self.color_palette
        )
        if data.get('show_correlation', True):
            z = np.polyfit(x_values, y_values, 1)
            p = np.poly1d(z)
            fig.add_scatter(x=x_values, y=p(x_values), mode='lines', name='Best Fit',
                          line=dict(dash='dash', color='red'))
            correlation = np.corrcoef(x_values, y_values)[0,1]
            fig.add_annotation(
                text=f'r = {correlation:.3f}',
                x=0.05, y=0.95, xref="paper", yref="paper",
                showarrow=False, bgcolor='wheat', opacity=0.8
            )
        
        file_path = self._save_interactive_chart(fig, f"scatter_plot_{hash(title)}")
        return {
            'file_path': file_path,
            'chart_type': 'scatter',
            'data_points': len(x_values)
        }

    def _create_heatmap(self, data: Dict[str, Any], title: str) -> Dict[str, Any]:
        matrix = np.array(data.get('matrix', np.random.rand(8, 8)))
        
        fig = px.imshow(
            matrix,
            labels=dict(x=data.get('x_label', 'X'), y=data.get('y_label', 'Y'), color='Value'),
            x=data.get('x_labels', None),
            y=data.get('y_labels', None),
            title=title,
            color_continuous_scale=self.color_palette
        )
        fig.update_layout(
            font=dict(size=14),
            title=dict(x=0.5, xanchor='center'),
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        file_path = self._save_interactive_chart(fig, f"heatmap_{hash(title)}")
        return {
            'file_path': file_path,
            'chart_type': 'heatmap',
            'data_points': matrix.size
        }

    def _create_histogram(self, data: Dict[str, Any], title: str) -> Dict[str, Any]:
        values = data.get('values', np.random.normal(50, 15, 1000))
        bins = data.get('bins', 30)
        
        fig = px.histogram(
            x=values,
            nbins=bins,
            labels={'x': data.get('x_label', 'Values'), 'y': data.get('y_label', 'Frequency')},
            title=title,
            color_discrete_sequence=[px.colors.sequential.Viridis[0]]
        )
        mean_val = np.mean(values)
        fig.add_vline(x=mean_val, line_dash="dash", line_color="red",
                     annotation_text=f'Mean: {mean_val:.2f}')
        fig.update_layout(
            font=dict(size=14),
            title=dict(x=0.5, xanchor='center'),
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        file_path = self._save_interactive_chart(fig, f"histogram_{hash(title)}")
        return {
            'file_path': file_path,
            'chart_type': 'histogram',
            'data_points': len(values)
        }

    async def _generate_mock_data(self, chart_spec: Dict[str, Any]) -> Dict[str, Any]:
        from ..agents.base import BaseAgent
        chart_type = chart_spec.get('type', 'bar')
        description = chart_spec.get('description', '')
        data_requirements = chart_spec.get('data_requirements', '')
        
        messages = [
            {
                "role": "system",
                "content": """You are a data generator creating realistic sample data for charts.
Based on the chart specification, generate appropriate sample data that would be realistic for the described visualization.
Return only a JSON object with the data structure needed for the chart type:
For bar charts: {"categories": [...], "values": [...], "x_label": "...", "y_label": "..."}
For line charts: {"x_values": [...], "y_values": [...], "x_label": "...", "y_label": "..."}
For pie charts: {"labels": [...], "sizes": [...]}
For scatter plots: {"x_values": [...], "y_values": [...], "x_label": "...", "y_label": "..."}
For heatmaps: {"matrix": [[...]], "x_labels": [...], "y_labels": [...]}
For histograms: {"values": [...], "bins": int, "x_label": "...", "y_label": "..."}
Make the data realistic and relevant to the description."""
            },
            {
                "role": "user",
                "content": f"Chart type: {chart_type}\nDescription: {description}\nData requirements: {data_requirements}\n\nGenerate realistic sample data:"
            }
        ]
        
        try:
            temp_agent = type('TempAgent', (BaseAgent,), {
                'process': lambda self: None
            })(self.config)
            response = await temp_agent._make_llm_request(messages)
            return json.loads(response)
        except:
            return self._get_default_data(chart_type)

    def _get_default_data(self, chart_type: str) -> Dict[str, Any]:
        defaults = {
            'bar': {
                'categories': ['Category A', 'Category B', 'Category C', 'Category D'],
                'values': [23, 45, 56, 78],
                'x_label': 'Categories',
                'y_label': 'Values'
            },
            'line': {
                'x_values': [2020, 2021, 2022, 2023, 2024],
                'y_values': [100, 120, 115, 140, 155],
                'x_label': 'Year',
                'y_label': 'Value'
            },
            'pie': {
                'labels': ['Section A', 'Section B', 'Section C', 'Section D'],
                'sizes': [30, 25, 25, 20]
            },
            'scatter': {
                'x_values': list(np.random.normal(50, 15, 30)),
                'y_values': list(np.random.normal(50, 15, 30)),
                'x_label': 'X Variable',
                'y_label': 'Y Variable'
            },
            'heatmap': {
                'matrix': np.random.rand(8, 8).tolist(),
                'x_labels': [f'X{i}' for i in range(8)],
                'y_labels': [f'Y{i}' for i in range(8)]
            },
            'histogram': {
                'values': list(np.random.normal(50, 15, 1000)),
                'bins': 30,
                'x_label': 'Values',
                'y_label': 'Frequency'
            }
        }
        return defaults.get(chart_type, defaults['bar'])

    def _save_interactive_chart(self, fig, filename: str) -> str:
        output_dir = Path("outputs/charts")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = output_dir / f"{filename}.html"
        pio.write_html(fig, file_path, include_plotlyjs='cdn', full_html=False)
        
        for format_type in self.config.visualization.supported_formats:
            if format_type == 'png':
                file_path_png = output_dir / f"{filename}.png"
                fig.write_image(file_path_png, width=self.resolution[0], height=self.resolution[1])
            elif format_type == 'svg':
                file_path_svg = output_dir / f"{filename}.svg"
                fig.write_image(file_path_svg, width=self.resolution[0], height=self.resolution[1])
            elif format_type == 'pdf':
                file_path_pdf = output_dir / f"{filename}.pdf"
                fig.write_image(file_path_pdf, width=self.resolution[0], height=self.resolution[1])
        
        return str(file_path)

    def _summarize_data(self, data: Dict[str, Any]) -> str:
        summary_parts = []
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0:
                if isinstance(value[0], (int, float)):
                    avg_val = sum(value) / len(value)
                    min_val = min(value)
                    max_val = max(value)
                    summary_parts.append(f"{key}: {len(value)} points, avg={avg_val:.2f}, range=[{min_val:.2f}, {max_val:.2f}]")
                elif isinstance(value, list) and isinstance(value[0], list):
                    matrix = np.array(value)
                    summary_parts.append(f"{key}: {matrix.shape[0]}x{matrix.shape[1]} matrix, avg={matrix.mean():.2f}")
                else:
                    summary_parts.append(f"{key}: {len(value)} items")
            elif isinstance(value, str):
                summary_parts.append(f"{key}: {value}")
        return "; ".join(summary_parts) if summary_parts else "No data summary available"
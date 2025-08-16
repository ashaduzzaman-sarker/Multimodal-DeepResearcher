import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json
import io
import base64

class ChartGenerator:
    """Generate various types of charts and visualizations"""
    
    def __init__(self, config):
        self.config = config
        self.resolution = tuple(config.visualization.chart_resolution)
        self.style = config.visualization.style_template
        self.color_palette = config.visualization.color_palette
        
        # Set up matplotlib style
        plt.style.use('default')
        if self.style == 'academic':
            sns.set_palette("viridis")
        elif self.style == 'business':
            sns.set_palette("Set2")
        else:  # casual
            sns.set_palette("bright")
    
    async def generate_chart_from_spec(self, chart_spec: Dict[str, Any], data: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate a chart based on specification"""
        
        chart_type = chart_spec.get('type', 'bar')
        title = chart_spec.get('title', 'Chart')
        description = chart_spec.get('description', '')
        
        # Generate or use provided data
        if data is None:
            chart_data = await self._generate_mock_data(chart_spec)
        else:
            chart_data = data
        
        # Create the chart
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
            # Default to bar chart
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
        """Create a bar chart"""
        
        # Extract data
        categories = data.get('categories', ['A', 'B', 'C', 'D', 'E'])
        values = data.get('values', [10, 15, 12, 8, 20])
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(self.resolution[0]/100, self.resolution[1]/100))
        
        bars = ax.bar(categories, values, color=sns.color_palette(n_colors=len(categories)))
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(data.get('x_label', 'Categories'), fontsize=12)
        ax.set_ylabel(data.get('y_label', 'Values'), fontsize=12)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{value}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        
        # Save figure
        file_path = self._save_figure(fig, f"bar_chart_{hash(title)}")
        plt.close(fig)
        
        return {
            'file_path': file_path,
            'chart_type': 'bar',
            'data_points': len(categories)
        }
    
    def _create_line_chart(self, data: Dict[str, Any], title: str) -> Dict[str, Any]:
        """Create a line chart"""
        
        x_values = data.get('x_values', list(range(2020, 2025)))
        y_values = data.get('y_values', [100, 120, 135, 140, 155])
        
        fig, ax = plt.subplots(figsize=(self.resolution[0]/100, self.resolution[1]/100))
        
        line = ax.plot(x_values, y_values, marker='o', linewidth=2, markersize=8)
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(data.get('x_label', 'Time'), fontsize=12)
        ax.set_ylabel(data.get('y_label', 'Value'), fontsize=12)
        
        # Add grid for better readability
        ax.grid(True, alpha=0.3)
        
        # Add trend line if requested
        if data.get('show_trend', False):
            z = np.polyfit(x_values, y_values, 1)
            p = np.poly1d(z)
            ax.plot(x_values, p(x_values), "--", alpha=0.8, color='red', label='Trend')
            ax.legend()
        
        plt.tight_layout()
        
        file_path = self._save_figure(fig, f"line_chart_{hash(title)}")
        plt.close(fig)
        
        return {
            'file_path': file_path,
            'chart_type': 'line',
            'data_points': len(x_values)
        }
    
    def _create_pie_chart(self, data: Dict[str, Any], title: str) -> Dict[str, Any]:
        """Create a pie chart"""
        
        labels = data.get('labels', ['Category A', 'Category B', 'Category C', 'Category D'])
        sizes = data.get('sizes', [30, 25, 20, 25])
        
        fig, ax = plt.subplots(figsize=(self.resolution[0]/100, self.resolution[1]/100))
        
        # Create pie chart with better styling
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                         startangle=90, colors=sns.color_palette(n_colors=len(labels)))
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Improve text readability
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.tight_layout()
        
        file_path = self._save_figure(fig, f"pie_chart_{hash(title)}")
        plt.close(fig)
        
        return {
            'file_path': file_path,
            'chart_type': 'pie',
            'data_points': len(labels)
        }
    
    def _create_scatter_plot(self, data: Dict[str, Any], title: str) -> Dict[str, Any]:
        """Create a scatter plot"""
        
        x_values = data.get('x_values', np.random.normal(50, 15, 50))
        y_values = data.get('y_values', np.random.normal(50, 15, 50))
        
        fig, ax = plt.subplots(figsize=(self.resolution[0]/100, self.resolution[1]/100))
        
        scatter = ax.scatter(x_values, y_values, alpha=0.7, s=60, 
                           c=range(len(x_values)), cmap='viridis')
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(data.get('x_label', 'X Values'), fontsize=12)
        ax.set_ylabel(data.get('y_label', 'Y Values'), fontsize=12)
        
        # Add correlation line if requested
        if data.get('show_correlation', True):
            z = np.polyfit(x_values, y_values, 1)
            p = np.poly1d(z)
            ax.plot(x_values, p(x_values), "r--", alpha=0.8, label='Best Fit')
            
            # Calculate and display correlation coefficient
            correlation = np.corrcoef(x_values, y_values)[0,1]
            ax.text(0.05, 0.95, f'r = {correlation:.3f}', transform=ax.transAxes, 
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        
        file_path = self._save_figure(fig, f"scatter_plot_{hash(title)}")
        plt.close(fig)
        
        return {
            'file_path': file_path,
            'chart_type': 'scatter',
            'data_points': len(x_values)
        }
    
    def _create_heatmap(self, data: Dict[str, Any], title: str) -> Dict[str, Any]:
        """Create a heatmap"""
        
        # Generate or use provided matrix data
        if 'matrix' in data:
            matrix = np.array(data['matrix'])
        else:
            matrix = np.random.rand(8, 8)
        
        fig, ax = plt.subplots(figsize=(self.resolution[0]/100, self.resolution[1]/100))
        
        heatmap = sns.heatmap(matrix, annot=True, cmap='viridis', 
                             xticklabels=data.get('x_labels', False),
                             yticklabels=data.get('y_labels', False),
                             ax=ax, fmt='.2f')
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        file_path = self._save_figure(fig, f"heatmap_{hash(title)}")
        plt.close(fig)
        
        return {
            'file_path': file_path,
            'chart_type': 'heatmap',
            'data_points': matrix.size
        }
    
    def _create_histogram(self, data: Dict[str, Any], title: str) -> Dict[str, Any]:
        """Create a histogram"""
        
        values = data.get('values', np.random.normal(50, 15, 1000))
        bins = data.get('bins', 30)
        
        fig, ax = plt.subplots(figsize=(self.resolution[0]/100, self.resolution[1]/100))
        
        n, bins, patches = ax.hist(values, bins=bins, alpha=0.7, color='skyblue', edgecolor='black')
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(data.get('x_label', 'Values'), fontsize=12)
        ax.set_ylabel(data.get('y_label', 'Frequency'), fontsize=12)
        
        # Add statistics
        mean_val = np.mean(values)
        std_val = np.std(values)
        ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.2f}')
        ax.legend()
        
        plt.tight_layout()
        
        file_path = self._save_figure(fig, f"histogram_{hash(title)}")
        plt.close(fig)
        
        return {
            'file_path': file_path,
            'chart_type': 'histogram',
            'data_points': len(values)
        }
    
    async def _generate_mock_data(self, chart_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate realistic mock data based on chart specification"""
        
        chart_type = chart_spec.get('type', 'bar')
        description = chart_spec.get('description', '')
        data_requirements = chart_spec.get('data_requirements', '')
        
        # Use LLM to generate contextually relevant data
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

Make the data realistic and relevant to the description."""
            },
            {
                "role": "user",
                "content": f"Chart type: {chart_type}\nDescription: {description}\nData requirements: {data_requirements}\n\nGenerate realistic sample data:"
            }
        ]
        
        try:
            from ..agents.base import BaseAgent
            # Create a temporary agent instance for this request
            temp_agent = type('TempAgent', (BaseAgent,), {
                'process': lambda self: None
            })(self.config)
            
            response = await temp_agent._make_llm_request(messages)
            data = json.loads(response)
            return data
        except:
            # Fallback to default data
            return self._get_default_data(chart_type)
    
    def _get_default_data(self, chart_type: str) -> Dict[str, Any]:
        """Get default data for different chart types"""
        
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
            }
        }
        
        return defaults.get(chart_type, defaults['bar'])
    
    def _save_figure(self, fig, filename: str) -> str:
        """Save figure to file and return path"""
        
        # Ensure output directory exists
        output_dir = Path("outputs/charts")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as PNG
        file_path = output_dir / f"{filename}.png"
        fig.savefig(file_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        
        return str(file_path)
    
    def _summarize_data(self, data: Dict[str, Any]) -> str:
        """Create a summary of the data used in the chart"""
        
        summary_parts = []
        
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0:
                if isinstance(value[0], (int, float)):
                    avg_val = sum(value) / len(value)
                    min_val = min(value)
                    max_val = max(value)
                    summary_parts.append(f"{key}: {len(value)} data points, avg={avg_val:.2f}, range=[{min_val:.2f}, {max_val:.2f}]")
                else:
                    summary_parts.append(f"{key}: {len(value)} items")
            elif isinstance(value, str):
                summary_parts.append(f"{key}: {value}")
        
        return "; ".join(summary_parts) if summary_parts else "No data summary available"

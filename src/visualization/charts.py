"""
Visualization module.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path
from typing import Optional

from src.models.config import Config
from src.utils.exceptions import VisualizationError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Visualizer:
    """
    Class for creating visualizations.
    
    Creates interactive charts using Plotly.
    """
    
    def __init__(self, config: Config, output_dir: str = "visualizations"):
        """
        Initialize visualizer.
        
        Args:
            config: Configuration object
            output_dir: Output directory for visualizations
        """
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.theme = config.visualization.theme
        logger.info(f"Visualizer initialized with output directory: {output_dir}")
    
    def create_index_ranking(self, indicators_df: pd.DataFrame, top_n: int = 20) -> go.Figure:
        """Tworzy wykres rankingu indeksu branż"""
        df_sorted = indicators_df.sort_values('final_index', ascending=True).tail(top_n)
        
        fig = go.Figure()
        
        colors = {
            'Bardzo dobra kondycja': '#2ecc71',
            'Dobra kondycja': '#3498db',
            'Średnia kondycja': '#f39c12',
            'Słaba kondycja': '#e67e22',
            'Bardzo słaba kondycja': '#e74c3c'
        }
        
        for category in df_sorted['category'].unique():
            df_cat = df_sorted[df_sorted['category'] == category]
            fig.add_trace(go.Bar(
                y=df_cat['pkd_code'],
                x=df_cat['final_index'],
                name=category,
                orientation='h',
                marker_color=colors.get(category, '#95a5a6')
            ))
        
        fig.update_layout(
            title='Ranking Indeksu Branż - Top 20',
            xaxis_title='Wartość indeksu',
            yaxis_title='Kod PKD',
            template=self.theme,
            height=800,
            showlegend=True
        )
        
        return fig
    
    def create_radar_chart(self, indicators_df: pd.DataFrame, pkd_code: str) -> go.Figure:
        """Tworzy wykres radarowy dla wybranej branży"""
        sector = indicators_df[indicators_df['pkd_code'] == pkd_code].iloc[0]
        
        categories = ['Wielkość', 'Rozwój', 'Rentowność', 'Zadłużenie', 'Ryzyko']
        values = [
            sector['size_score'],
            sector['growth_score'],
            sector['profitability_score'],
            sector['debt_score'],
            sector['risk_score']
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=pkd_code
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            title=f'Profil branży {pkd_code}'
        )
        
        return fig
    
    def create_growth_comparison(self, indicators_df: pd.DataFrame, top_n: int = 15) -> go.Figure:
        """Tworzy wykres porównania wzrostu branż"""
        df_sorted = indicators_df.nlargest(top_n, 'final_index')
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df_sorted['pkd_code'],
            y=df_sorted['revenue_growth_yoy'],
            name='Dynamika przychodów',
            marker_color='#3498db'
        ))
        
        fig.add_trace(go.Bar(
            x=df_sorted['pkd_code'],
            y=df_sorted['profit_growth_yoy'],
            name='Dynamika zysku',
            marker_color='#2ecc71'
        ))
        
        fig.update_layout(
            title='Porównanie dynamiki wzrostu - Top branże',
            xaxis_title='Kod PKD',
            yaxis_title='Dynamika (YoY)',
            template=self.theme,
            barmode='group',
            height=600
        )
        
        return fig
    
    def create_category_distribution(self, indicators_df: pd.DataFrame) -> go.Figure:
        """Tworzy wykres rozkładu kategorii"""
        category_counts = indicators_df['category'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=category_counts.index,
            values=category_counts.values,
            hole=0.3
        )])
        
        fig.update_layout(
            title='Rozkład branż według kondycji',
            template=self.theme
        )
        
        return fig
    
    def create_correlation_heatmap(self, indicators_df: pd.DataFrame) -> go.Figure:
        """Tworzy mapę korelacji między wskaźnikami"""
        numeric_cols = ['size_score', 'growth_score', 'profitability_score', 
                       'debt_score', 'risk_score', 'final_index']
        corr_matrix = indicators_df[numeric_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values,
            texttemplate='%{text:.2f}',
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title='Korelacja między wskaźnikami',
            template=self.theme,
            height=600
        )
        
        return fig
    
    def save_figure(self, fig: go.Figure, filename: str, format: str = 'html') -> Path:
        """
        Save figure to file.
        
        Args:
            fig: Plotly figure object
            filename: Output filename (without extension)
            format: Output format (html, png, pdf)
            
        Returns:
            Path to saved file
            
        Raises:
            VisualizationError: If saving fails
        """
        filepath = self.output_dir / f"{filename}.{format}"
        
        try:
            if format == 'html':
                fig.write_html(str(filepath))
            elif format == 'png':
                fig.write_image(str(filepath))
            elif format == 'pdf':
                fig.write_image(str(filepath), format='pdf')
            else:
                raise VisualizationError(f"Unsupported format: {format}")
            
            logger.info(f"Saved visualization: {filepath}")
            return filepath
        except Exception as e:
            error_msg = f"Error saving visualization {filename}: {e}"
            logger.error(error_msg)
            raise VisualizationError(error_msg) from e


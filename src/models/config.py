"""
Configuration models.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Weights:
    """Weights for index components."""
    
    size: float = 0.20
    growth: float = 0.25
    profitability: float = 0.20
    debt: float = 0.15
    risk: float = 0.20
    
    def validate(self) -> bool:
        """Validate that weights sum to 1.0."""
        total = self.size + self.growth + self.profitability + self.debt + self.risk
        return abs(total - 1.0) < 0.01


@dataclass
class AnalysisPeriod:
    """Analysis period configuration."""
    
    start_year: int = 2021
    end_year: int = 2024
    forecast_months: int = 12


@dataclass
class DataSource:
    """Data source configuration."""
    
    enabled: bool = True
    base_url: str = ""


@dataclass
class DataSources:
    """All data sources configuration."""
    
    gus: DataSource
    krs: DataSource
    gpw: DataSource
    nbp: DataSource


@dataclass
class Category:
    """Classification category."""
    
    name: str
    min_score: float


@dataclass
class Classification:
    """Classification configuration."""
    
    categories: List[Category]


@dataclass
class Visualization:
    """Visualization configuration."""
    
    output_format: List[str]
    theme: str = "plotly_white"
    width: int = 1200
    height: int = 800


@dataclass
class Config:
    """Main configuration model."""
    
    weights: Weights
    analysis_period: AnalysisPeriod
    data_sources: DataSources
    classification: Classification
    visualization: Visualization
    pkd_level: str = "division"
    pkd_year: int = 2007
    
    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        """Create Config from dictionary."""
        weights = Weights(**data.get("weights", {}))
        analysis_period = AnalysisPeriod(**data.get("analysis_period", {}))
        
        ds_data = data.get("data_sources", {})
        data_sources = DataSources(
            gus=DataSource(**ds_data.get("gus", {})),
            krs=DataSource(**ds_data.get("krs", {})),
            gpw=DataSource(**ds_data.get("gpw", {})),
            nbp=DataSource(**ds_data.get("nbp", {})),
        )
        
        categories = [
            Category(**cat) for cat in data.get("classification", {}).get("categories", [])
        ]
        classification = Classification(categories=categories)
        
        viz_data = data.get("visualization", {})
        visualization = Visualization(**viz_data)
        
        return cls(
            pkd_level=data.get("pkd_level", "division"),
            pkd_year=data.get("pkd_year", 2007),
            weights=weights,
            analysis_period=analysis_period,
            data_sources=data_sources,
            classification=classification,
            visualization=visualization,
        )


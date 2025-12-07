from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Weights:
    size: float = 0.20
    growth: float = 0.25
    profitability: float = 0.20
    debt: float = 0.15
    risk: float = 0.20
    
    def validate(self) -> bool:
        total = self.size + self.growth + self.profitability + self.debt + self.risk
        return abs(total - 1.0) < 0.01


@dataclass
class AnalysisPeriod:
    start_year: int = 2021
    end_year: int = 2024
    forecast_months: int = 12


@dataclass
class DataSource:
    enabled: bool = True
    base_url: str = ""


@dataclass
class DataSources:
    gus: DataSource
    krs: DataSource
    gpw: DataSource
    nbp: DataSource


@dataclass
class Category:
    name: str
    min_score: float


@dataclass
class Classification:
    categories: List[Category]


@dataclass
class Visualization:
    output_format: List[str]
    theme: str
    width: int
    height: int


@dataclass
class Config:
    pkd_level: str = "division"
    pkd_year: int = 2007
    weights: Weights = None
    analysis_period: AnalysisPeriod = None
    data_sources: DataSources = None
    classification: Classification = None
    visualization: Visualization = None
    
    def __post_init__(self):
        if self.weights is None:
            self.weights = Weights()
        if self.analysis_period is None:
            self.analysis_period = AnalysisPeriod()
        if self.data_sources is None:
            self.data_sources = DataSources(
                gus=DataSource(),
                krs=DataSource(),
                gpw=DataSource(),
                nbp=DataSource()
            )
        if self.classification is None:
            self.classification = Classification(categories=[])
        if self.visualization is None:
            self.visualization = Visualization(
                output_format=["html", "png"],
                theme="plotly_white",
                width=1200,
                height=800
            )
    
    @classmethod
    def from_dict(cls, data: dict) -> "Config":
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

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import pandas as pd


@dataclass
class SectorData:
    pkd_code: str
    year: int
    revenue: float
    profit: float
    assets: float
    debt: float
    bankruptcies: int
    num_companies: int
    
    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> list["SectorData"]:
        return [
            cls(
                pkd_code=row["pkd_code"],
                year=row["year"],
                revenue=row["revenue"],
                profit=row["profit"],
                assets=row["assets"],
                debt=row["debt"],
                bankruptcies=row["bankruptcies"],
                num_companies=row["num_companies"],
            )
            for _, row in df.iterrows()
        ]


@dataclass
class SectorIndicators:
    pkd_code: str
    size_score: float
    growth_score: float
    profitability_score: float
    debt_score: float
    risk_score: float
    final_index: float
    revenue_growth_yoy: float
    profit_growth_yoy: float
    profit_margin: float
    debt_to_assets: float
    bankruptcy_rate: float
    num_companies: int
    
    def to_dict(self) -> dict:
        return {
            "pkd_code": self.pkd_code,
            "size_score": self.size_score,
            "growth_score": self.growth_score,
            "profitability_score": self.profitability_score,
            "debt_score": self.debt_score,
            "risk_score": self.risk_score,
            "final_index": self.final_index,
            "revenue_growth_yoy": self.revenue_growth_yoy,
            "profit_growth_yoy": self.profit_growth_yoy,
            "profit_margin": self.profit_margin,
            "debt_to_assets": self.debt_to_assets,
            "bankruptcy_rate": self.bankruptcy_rate,
            "num_companies": self.num_companies,
        }


@dataclass
class SectorClassification:
    pkd_code: str
    branch_name: str
    final_index: float
    category: str
    rank: int
    indicators: SectorIndicators

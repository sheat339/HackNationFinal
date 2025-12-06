"""
Sector data models and type definitions.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import pandas as pd


@dataclass
class SectorData:
    """
    Data model for sector financial data.
    
    Attributes:
        pkd_code: PKD/NACE sector code
        year: Year of the data
        revenue: Total revenue
        profit: Total profit
        assets: Total assets
        debt: Total debt
        bankruptcies: Number of bankruptcies
        num_companies: Number of companies in the sector
    """
    
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
        """
        Create list of SectorData from DataFrame.
        
        Args:
            df: DataFrame with sector data
            
        Returns:
            List of SectorData objects
        """
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
    """
    Data model for calculated sector indicators.
    
    Attributes:
        pkd_code: PKD/NACE sector code
        size_score: Size component score (0-1)
        growth_score: Growth component score (0-1)
        profitability_score: Profitability component score (0-1)
        debt_score: Debt component score (0-1)
        risk_score: Risk component score (0-1)
        final_index: Final composite index (0-1)
        revenue_growth_yoy: Year-over-year revenue growth
        profit_growth_yoy: Year-over-year profit growth
        profit_margin: Profit margin (profit/revenue)
        debt_to_assets: Debt to assets ratio
        bankruptcy_rate: Bankruptcy rate (%)
        num_companies: Number of companies
    """
    
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
        """Convert to dictionary."""
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
    """
    Data model for sector classification result.
    
    Attributes:
        pkd_code: PKD/NACE sector code
        branch_name: Sector name
        final_index: Final composite index
        category: Classification category
        rank: Ranking position
        indicators: Sector indicators
    """
    
    pkd_code: str
    branch_name: str
    final_index: float
    category: str
    rank: int
    indicators: SectorIndicators


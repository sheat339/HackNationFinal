import pandas as pd
import numpy as np
from typing import Dict, List

from src.models.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class IndicatorCalculator:
    def __init__(self, config: Config):
        self.config = config
        self.weights = config.weights
        logger.debug("IndicatorCalculator initialized")
    
    def calculate_all_indicators(self, sector_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        results = []
        
        for pkd_code, data in sector_data.items():
            try:
                logger.debug(f"Calculating indicators for sector {pkd_code}")
                indicators = self.calculate_sector_indicators(pkd_code, data)
                results.append(indicators)
            except Exception as e:
                logger.error(f"Error calculating indicators for sector {pkd_code}: {e}")
                raise
        
        return pd.DataFrame(results)
    
    def calculate_sector_indicators(self, pkd_code: str, data: pd.DataFrame) -> Dict:
        data = data.sort_values('year')
        
        size_score = self._calculate_size_score(data)
        growth_score = self._calculate_growth_score(data)
        profitability_score = self._calculate_profitability_score(data)
        debt_score = self._calculate_debt_score(data)
        risk_score = self._calculate_risk_score(data)
        
        final_index = (
            size_score * self.weights.size +
            growth_score * self.weights.growth +
            profitability_score * self.weights.profitability +
            debt_score * self.weights.debt +
            risk_score * self.weights.risk
        )
        
        return {
            'pkd_code': pkd_code,
            'size_score': size_score,
            'growth_score': growth_score,
            'profitability_score': profitability_score,
            'debt_score': debt_score,
            'risk_score': risk_score,
            'final_index': final_index,
            'revenue_growth_yoy': self._calculate_yoy_growth(data, 'revenue'),
            'profit_growth_yoy': self._calculate_yoy_growth(data, 'profit'),
            'profit_margin': self._calculate_profit_margin(data),
            'debt_to_assets': self._calculate_debt_to_assets(data),
            'bankruptcy_rate': self._calculate_bankruptcy_rate(data),
            'num_companies': data['num_companies'].iloc[-1] if len(data) > 0 else 0
        }
    
    def _calculate_size_score(self, data: pd.DataFrame) -> float:
        if len(data) == 0:
            return 0.0
        
        latest = data.iloc[-1]
        
        revenue = latest['revenue']
        assets = latest['assets']
        num_companies = latest['num_companies']
        
        size_metric = (revenue / 10000000 + assets / 20000000 + num_companies / 10000) / 3
        return min(1.0, max(0.0, size_metric))
    
    def _calculate_growth_score(self, data: pd.DataFrame) -> float:
        if len(data) < 2:
            return 0.5
        
        revenue_growth = self._calculate_yoy_growth(data, 'revenue')
        profit_growth = self._calculate_yoy_growth(data, 'profit')
        assets_growth = self._calculate_yoy_growth(data, 'assets')
        
        avg_growth = (revenue_growth + profit_growth + assets_growth) / 3
        
        growth_score = min(1.0, max(0.0, (avg_growth + 0.1) / 0.3))
        return growth_score
    
    def _calculate_profitability_score(self, data: pd.DataFrame) -> float:
        if len(data) == 0:
            return 0.0
        
        latest = data.iloc[-1]
        profit_margin = latest['profit'] / latest['revenue'] if latest['revenue'] > 0 else 0
        
        profitability_score = min(1.0, max(0.0, profit_margin * 10))
        return profitability_score
    
    def _calculate_debt_score(self, data: pd.DataFrame) -> float:
        if len(data) == 0:
            return 0.5
        
        latest = data.iloc[-1]
        debt_to_assets = latest['debt'] / latest['assets'] if latest['assets'] > 0 else 0
        
        debt_score = max(0.0, min(1.0, 1 - debt_to_assets))
        return debt_score
    
    def _calculate_risk_score(self, data: pd.DataFrame) -> float:
        if len(data) == 0:
            return 0.5
        
        latest = data.iloc[-1]
        bankruptcy_rate = latest['bankruptcies'] / latest['num_companies'] if latest['num_companies'] > 0 else 0
        
        risk_score = max(0.0, min(1.0, 1 - bankruptcy_rate * 10))
        return risk_score
    
    def _calculate_yoy_growth(self, data: pd.DataFrame, column: str) -> float:
        if len(data) < 2:
            return 0.0
        
        latest = data[column].iloc[-1]
        previous = data[column].iloc[-2]
        
        if previous == 0:
            return 0.0
        
        return (latest - previous) / previous
    
    def _calculate_profit_margin(self, data: pd.DataFrame) -> float:
        if len(data) == 0:
            return 0.0
        
        latest = data.iloc[-1]
        return latest['profit'] / latest['revenue'] if latest['revenue'] > 0 else 0.0
    
    def _calculate_debt_to_assets(self, data: pd.DataFrame) -> float:
        if len(data) == 0:
            return 0.0
        
        latest = data.iloc[-1]
        return latest['debt'] / latest['assets'] if latest['assets'] > 0 else 0.0
    
    def _calculate_bankruptcy_rate(self, data: pd.DataFrame) -> float:
        if len(data) == 0:
            return 0.0
        
        latest = data.iloc[-1]
        return latest['bankruptcies'] / latest['num_companies'] if latest['num_companies'] > 0 else 0.0

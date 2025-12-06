"""
Calculation of indicators for sectors.
"""

import pandas as pd
import numpy as np
from typing import Dict, List

from src.models.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class IndicatorCalculator:
    """
    Class for calculating sector indicators.
    
    Calculates 5 component scores and final composite index.
    """
    
    def __init__(self, config: Config):
        """
        Initialize indicator calculator.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.weights = config.weights
        logger.debug("IndicatorCalculator initialized")
    
    def calculate_all_indicators(self, sector_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Calculate all indicators for all sectors.
        
        Args:
            sector_data: Dictionary mapping PKD codes to DataFrames with sector data
            
        Returns:
            DataFrame with indicators for all sectors
            
        Raises:
            CalculationError: If calculation fails
        """
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
        """
        Oblicza wskaźniki dla pojedynczego sektora
        
        Args:
            pkd_code: Kod PKD sektora
            data: DataFrame z danymi sektora
            
        Returns:
            Słownik ze wskaźnikami
        """
        # Sortuj dane po roku
        data = data.sort_values('year')
        
        # Wielkość branży
        size_score = self._calculate_size_score(data)
        
        # Rozwój branży
        growth_score = self._calculate_growth_score(data)
        
        # Rentowność
        profitability_score = self._calculate_profitability_score(data)
        
        # Zadłużenie
        debt_score = self._calculate_debt_score(data)
        
        # Ryzyko
        risk_score = self._calculate_risk_score(data)
        
        # Calculate final index
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
        """Oblicza wskaźnik wielkości branży (0-1)"""
        if len(data) == 0:
            return 0.0
        
        # Używamy najnowszych danych
        latest = data.iloc[-1]
        
        # Normalizacja względem średniej (w rzeczywistości względem wszystkich branż)
        revenue = latest['revenue']
        assets = latest['assets']
        num_companies = latest['num_companies']
        
        # Prosta normalizacja (w rzeczywistości użyjemy min-max scaling)
        size_metric = (revenue / 10000000 + assets / 20000000 + num_companies / 10000) / 3
        return min(1.0, max(0.0, size_metric))
    
    def _calculate_growth_score(self, data: pd.DataFrame) -> float:
        """Oblicza wskaźnik rozwoju branży (0-1)"""
        if len(data) < 2:
            return 0.5
        
        # Oblicz dynamikę przychodów, zysku i aktywów
        revenue_growth = self._calculate_yoy_growth(data, 'revenue')
        profit_growth = self._calculate_yoy_growth(data, 'profit')
        assets_growth = self._calculate_yoy_growth(data, 'assets')
        
        # Średnia dynamika (normalizowana do 0-1)
        avg_growth = (revenue_growth + profit_growth + assets_growth) / 3
        
        # Normalizacja: 0% = 0.0, 10% = 0.5, 20%+ = 1.0
        growth_score = min(1.0, max(0.0, (avg_growth + 0.1) / 0.3))
        return growth_score
    
    def _calculate_profitability_score(self, data: pd.DataFrame) -> float:
        """Oblicza wskaźnik rentowności (0-1)"""
        if len(data) == 0:
            return 0.0
        
        latest = data.iloc[-1]
        profit_margin = latest['profit'] / latest['revenue'] if latest['revenue'] > 0 else 0
        
        # Normalizacja: 0% = 0.0, 5% = 0.5, 10%+ = 1.0
        profitability_score = min(1.0, max(0.0, profit_margin * 10))
        return profitability_score
    
    def _calculate_debt_score(self, data: pd.DataFrame) -> float:
        """Oblicza wskaźnik zadłużenia (0-1, wyższy = lepszy = mniejsze zadłużenie)"""
        if len(data) == 0:
            return 0.5
        
        latest = data.iloc[-1]
        debt_to_assets = latest['debt'] / latest['assets'] if latest['assets'] > 0 else 0
        
        # Odwrotna normalizacja: 0% = 1.0, 50% = 0.5, 100%+ = 0.0
        debt_score = max(0.0, min(1.0, 1 - debt_to_assets))
        return debt_score
    
    def _calculate_risk_score(self, data: pd.DataFrame) -> float:
        """Oblicza wskaźnik ryzyka (0-1, wyższy = lepszy = mniejsze ryzyko)"""
        if len(data) == 0:
            return 0.5
        
        latest = data.iloc[-1]
        bankruptcy_rate = latest['bankruptcies'] / latest['num_companies'] if latest['num_companies'] > 0 else 0
        
        # Odwrotna normalizacja: 0% = 1.0, 5% = 0.5, 10%+ = 0.0
        risk_score = max(0.0, min(1.0, 1 - bankruptcy_rate * 10))
        return risk_score
    
    def _calculate_yoy_growth(self, data: pd.DataFrame, column: str) -> float:
        """Oblicza dynamikę rok do roku dla danej kolumny"""
        if len(data) < 2:
            return 0.0
        
        latest = data[column].iloc[-1]
        previous = data[column].iloc[-2]
        
        if previous == 0:
            return 0.0
        
        return (latest - previous) / previous
    
    def _calculate_profit_margin(self, data: pd.DataFrame) -> float:
        """Oblicza marżę zysku"""
        if len(data) == 0:
            return 0.0
        
        latest = data.iloc[-1]
        return latest['profit'] / latest['revenue'] if latest['revenue'] > 0 else 0.0
    
    def _calculate_debt_to_assets(self, data: pd.DataFrame) -> float:
        """Oblicza wskaźnik zadłużenia do aktywów"""
        if len(data) == 0:
            return 0.0
        
        latest = data.iloc[-1]
        return latest['debt'] / latest['assets'] if latest['assets'] > 0 else 0.0
    
    def _calculate_bankruptcy_rate(self, data: pd.DataFrame) -> float:
        """Oblicza wskaźnik upadłości"""
        if len(data) == 0:
            return 0.0
        
        latest = data.iloc[-1]
        return latest['bankruptcies'] / latest['num_companies'] if latest['num_companies'] > 0 else 0.0


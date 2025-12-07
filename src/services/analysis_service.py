from typing import Dict, List
import pandas as pd

from src.models.config import Config
from src.models.sector import SectorIndicators, SectorClassification
from src.analysis.indicators import IndicatorCalculator
from src.analysis.classifier import SectorClassifier
from src.utils.pkd_mapping import get_pkd_division_name
from src.utils.exceptions import CalculationError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AnalysisService:
    def __init__(self, config: Config):
        self.config = config
        self.calculator = IndicatorCalculator(config)
        self.classifier = SectorClassifier(config)
        logger.info("AnalysisService zainicjalizowany")
    
    def calculate_indicators(self, sector_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        logger.info(f"Obliczanie wskaźników dla {len(sector_data)} sektorów")
        
        try:
            indicators_df = self.calculator.calculate_all_indicators(sector_data)
            logger.info(f"Pomyślnie obliczono wskaźniki dla {len(indicators_df)} sektorów")
            return indicators_df
        except Exception as e:
            error_msg = f"Błąd obliczania wskaźników: {e}"
            logger.error(error_msg)
            raise CalculationError(error_msg) from e
    
    def classify_sectors(self, indicators_df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Klasyfikacja sektorów")
        
        try:
            classified_df = self.classifier.classify_sectors(indicators_df)
            logger.info("Sektory sklasyfikowane pomyślnie")
            return classified_df
        except Exception as e:
            error_msg = f"Błąd klasyfikacji sektorów: {e}"
            logger.error(error_msg)
            raise CalculationError(error_msg) from e
    
    def prepare_final_results(self, indicators_df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Przygotowywanie wyników końcowych")
        
        indicators_df = indicators_df.copy()
        
        indicators_df['branch_name'] = indicators_df['pkd_code'].apply(get_pkd_division_name)
        indicators_df = indicators_df.sort_values('final_index', ascending=False)
        indicators_df['rank'] = range(1, len(indicators_df) + 1)
        
        column_order = [
            'rank', 'pkd_code', 'branch_name', 'final_index', 'category',
            'size_score', 'growth_score', 'profitability_score', 'debt_score', 'risk_score',
            'revenue_growth_yoy', 'profit_growth_yoy', 'profit_margin',
            'debt_to_assets', 'bankruptcy_rate', 'num_companies'
        ]
        
        available_columns = [col for col in column_order if col in indicators_df.columns]
        indicators_df = indicators_df[available_columns]
        
        logger.info(f"Wyniki końcowe przygotowane dla {len(indicators_df)} sektorów")
        logger.info(f"Rozkład kategorii: {indicators_df['category'].value_counts().to_dict()}")
        return indicators_df
    
    def get_top_sectors(self, results_df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
        return self.classifier.get_top_sectors(results_df, n)
    
    def get_growing_sectors(self, results_df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
        return self.classifier.get_growing_sectors(results_df, n)
    
    def get_risky_sectors(self, results_df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
        return self.classifier.get_risky_sectors(results_df, n)

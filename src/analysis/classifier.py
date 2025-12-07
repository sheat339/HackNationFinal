from typing import Dict, List
import pandas as pd

from src.models.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SectorClassifier:
    def __init__(self, config: Config):
        self.config = config
        self.categories = config.classification.categories
        logger.debug("SectorClassifier initialized")
    
    def classify_sectors(self, indicators_df: pd.DataFrame) -> pd.DataFrame:
        df = indicators_df.copy()
        
        def assign_category(score: float) -> str:
            for category in sorted(self.categories, key=lambda x: x.min_score, reverse=True):
                if score >= category.min_score:
                    return category.name
            return "Bardzo słaba kondycja"
        
        df['category'] = df['final_index'].apply(assign_category)
        
        return df
    
    def get_top_sectors(self, indicators_df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
        return indicators_df.nlargest(n, 'final_index')
    
    def get_bottom_sectors(self, indicators_df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
        return indicators_df.nsmallest(n, 'final_index')
    
    def get_growing_sectors(self, indicators_df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
        return indicators_df.nlargest(n, 'growth_score')
    
    def get_risky_sectors(self, indicators_df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
        return indicators_df.nsmallest(n, 'risk_score')

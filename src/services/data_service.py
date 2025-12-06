from typing import Dict, List
import pandas as pd
from pathlib import Path

from src.models.config import Config
from src.models.sector import SectorData
from src.data_collection.data_collector import DataCollector
from src.utils.exceptions import DataCollectionError, DataProcessingError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataService:
    def __init__(self, config: Config):
        self.config = config
        self.collector = DataCollector(config)
        logger.info("DataService zainicjalizowany")
    
    def collect_sector_data(self, pkd_codes: List[str]) -> Dict[str, pd.DataFrame]:
        if not pkd_codes:
            raise DataCollectionError("Brak kodów PKD")
        
        logger.info(f"Zbieranie danych dla {len(pkd_codes)} sektorów")
        
        try:
            sector_data = self.collector.collect_all_data(pkd_codes)
            logger.info(f"Pomyślnie zebrano dane dla {len(sector_data)} sektorów")
            return sector_data
        except Exception as e:
            error_msg = f"Błąd zbierania danych sektorowych: {e}"
            logger.error(error_msg)
            raise DataCollectionError(error_msg) from e
    
    def validate_sector_data(self, data: pd.DataFrame) -> bool:
        required_columns = [
            'pkd_code', 'year', 'revenue', 'profit', 
            'assets', 'debt', 'bankruptcies', 'num_companies'
        ]
        
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            error_msg = f"Brakujące wymagane kolumny: {missing_columns}"
            logger.error(error_msg)
            raise DataProcessingError(error_msg)
        
        numeric_columns = ['revenue', 'profit', 'assets', 'debt', 'num_companies']
        for col in numeric_columns:
            if (data[col] < 0).any():
                logger.warning(f"Znaleziono ujemne wartości w {col}")
        
        missing_values = data[required_columns].isnull().sum()
        if missing_values.any():
            logger.warning(f"Wykryto brakujące wartości:\n{missing_values[missing_values > 0]}")
        
        logger.debug("Walidacja danych zakończona pomyślnie")
        return True
    
    def convert_to_models(self, sector_data: Dict[str, pd.DataFrame]) -> Dict[str, List[SectorData]]:
        models: Dict[str, List[SectorData]] = {}
        
        for pkd_code, df in sector_data.items():
            try:
                self.validate_sector_data(df)
                models[pkd_code] = SectorData.from_dataframe(df)
                logger.debug(f"Przekonwertowano {len(models[pkd_code])} rekordów dla sektora {pkd_code}")
            except Exception as e:
                logger.error(f"Błąd konwersji danych dla sektora {pkd_code}: {e}")
                raise
        
        return models

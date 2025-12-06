from typing import Dict, List, Optional
import pandas as pd
import time

from src.models.config import Config
from src.utils.exceptions import DataCollectionError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataCollector:
    def __init__(self, config: Config):
        self.config = config
        self.data_sources = config.data_sources
        logger.info("DataCollector zainicjalizowany")
        
    def collect_all_data(self, pkd_codes: List[str]) -> Dict[str, pd.DataFrame]:
        if not pkd_codes:
            raise DataCollectionError("Brak kodów PKD")
        
        results: Dict[str, pd.DataFrame] = {}
        
        for code in pkd_codes:
            try:
                logger.info(f"Zbieranie danych dla PKD {code}")
                data = self.collect_sector_data(code)
                results[code] = data
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Błąd zbierania danych dla PKD {code}: {e}")
                raise DataCollectionError(f"Nie udało się zebrać danych dla PKD {code}: {e}") from e
        
        logger.info(f"Pomyślnie zebrano dane dla {len(results)} sektorów")
        return results
    
    def collect_sector_data(self, pkd_code: str) -> pd.DataFrame:
        from src.data_collection.sample_data_generator import SampleDataGenerator
        from src.data_collection.database_loader import DatabaseLoader
        
        try:
            analysis_period = self.config.analysis_period
            start_year = analysis_period.start_year
            end_year = analysis_period.end_year
            years = list(range(start_year, end_year + 1))
            
            database_loader = DatabaseLoader()
            df = database_loader.load_sector_data_from_database(pkd_code, years)
            
            if df is None or df.empty:
                logger.info(f"Brak danych w bazie dla PKD {pkd_code}, używam generatora")
                generator = SampleDataGenerator()
                df = generator.generate_realistic_sector_data(pkd_code, years)
            else:
                logger.info(f"Załadowano dane z bazy dla PKD {pkd_code}")
            
            logger.debug(f"Zebrano {len(df)} rekordów dla sektora {pkd_code}")
            
            return df
        except Exception as e:
            error_msg = f"Błąd zbierania danych dla sektora {pkd_code}: {e}"
            logger.error(error_msg)
            raise DataCollectionError(error_msg) from e
    
    def collect_gus_data(self, pkd_code: str) -> Optional[pd.DataFrame]:
        logger.debug(f"Zbieranie danych GUS dla {pkd_code} nie jest jeszcze zaimplementowane")
        return None
    
    def collect_krs_data(self, pkd_code: str) -> Optional[pd.DataFrame]:
        logger.debug(f"Zbieranie danych KRS dla {pkd_code} nie jest jeszcze zaimplementowane")
        return None
    
    def collect_gpw_data(self, pkd_code: str) -> Optional[pd.DataFrame]:
        logger.debug(f"Zbieranie danych GPW dla {pkd_code} nie jest jeszcze zaimplementowane")
        return None
    
    def collect_nbp_data(self) -> Optional[pd.DataFrame]:
        logger.debug("Zbieranie danych NBP nie jest jeszcze zaimplementowane")
        return None

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
        skipped = []
        
        for code in pkd_codes:
            try:
                logger.info(f"Zbieranie danych dla PKD {code}")
                data = self.collect_sector_data(code)
                if data is not None and not data.empty:
                    results[code] = data
                else:
                    skipped.append(code)
                    logger.warning(f"Pominięto PKD {code} - brak danych")
            except DataCollectionError as e:
                skipped.append(code)
                logger.warning(f"Pominięto PKD {code}: {e}")
            except Exception as e:
                skipped.append(code)
                logger.warning(f"Pominięto PKD {code} z powodu błędu: {e}")
        
        if skipped:
            logger.info(f"Pominięto {len(skipped)} sektorów bez danych: {skipped}")
        
        if not results:
            raise DataCollectionError("Nie udało się zebrać danych dla żadnego sektora")
        
        logger.info(f"Pomyślnie zebrano dane dla {len(results)} sektorów")
        return results
    
    def collect_sector_data(self, pkd_code: str) -> Optional[pd.DataFrame]:
        from src.data_collection.database_loader import DatabaseLoader
        
        try:
            analysis_period = self.config.analysis_period
            start_year = analysis_period.start_year
            end_year = analysis_period.end_year
            years = list(range(start_year, end_year + 1))
            
            database_loader = DatabaseLoader()
            df = database_loader.load_sector_data_from_database(pkd_code, years)
            
            if df is None or df.empty:
                logger.warning(f"Brak danych w bazie dla PKD {pkd_code}")
                return None
            
            logger.info(f"Załadowano dane z bazy dla PKD {pkd_code}")
            logger.debug(f"Zebrano {len(df)} rekordów dla sektora {pkd_code}")
            
            return df
        except Exception as e:
            logger.warning(f"Błąd zbierania danych dla sektora {pkd_code}: {e}")
            return None
    
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

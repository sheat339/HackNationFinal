from pathlib import Path
from typing import Optional
import pandas as pd
import datetime

from src.models.config import Config
from src.utils.exceptions import DataProcessingError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ExportService:
    def __init__(self, config: Config, output_dir: Path):
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ExportService zainicjalizowany z katalogiem wyjściowym: {output_dir}")
    
    def export_to_csv(
        self, 
        df: pd.DataFrame, 
        filename: str = "indeks_branz.csv"
    ) -> Path:
        filepath = self.output_dir / filename
        
        try:
            if filepath.exists():
                try:
                    with open(filepath, 'a', encoding='utf-8-sig'):
                        pass
                except PermissionError:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_filename = f"{filepath.stem}_{timestamp}{filepath.suffix}"
                    filepath = self.output_dir / backup_filename
                    logger.warning(
                        f"Oryginalny plik jest zablokowany, używam nazwy kopii zapasowej: {backup_filename}"
                    )
            
            logger.info(f"Eksportowanie do CSV: {filepath}")
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            logger.info(f"Pomyślnie wyeksportowano CSV: {filepath}")
            return filepath
        except PermissionError as e:
            error_msg = (
                f"Odmowa dostępu: {filepath}. "
                "Zamknij plik, jeśli jest otwarty w Excelu lub innej aplikacji."
            )
            logger.error(error_msg)
            raise DataProcessingError(error_msg) from e
        except Exception as e:
            error_msg = f"Błąd eksportowania do CSV: {e}"
            logger.error(error_msg)
            raise DataProcessingError(error_msg) from e
    
    def export_to_excel(
        self, 
        df: pd.DataFrame,
        main_sheet_name: str = "Indeks Branż",
        filename: str = "indeks_branz.xlsx",
        additional_sheets: Optional[dict] = None
    ) -> Path:
        filepath = self.output_dir / filename
        
        try:
            if filepath.exists():
                try:
                    import openpyxl
                    wb = openpyxl.load_workbook(filepath)
                    wb.close()
                except PermissionError:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_filename = f"{filepath.stem}_{timestamp}{filepath.suffix}"
                    filepath = self.output_dir / backup_filename
                    logger.warning(
                        f"Oryginalny plik jest zablokowany, używam nazwy kopii zapasowej: {backup_filename}"
                    )
                except Exception:
                    pass
            
            logger.info(f"Eksportowanie do Excel: {filepath}")
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=main_sheet_name, index=False)
                
                if additional_sheets:
                    for sheet_name, sheet_df in additional_sheets.items():
                        sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
                        logger.debug(f"Dodano arkusz: {sheet_name}")
            
            logger.info(f"Pomyślnie wyeksportowano Excel: {filepath}")
            return filepath
        except PermissionError as e:
            error_msg = (
                f"Odmowa dostępu: {filepath}. "
                "Zamknij plik, jeśli jest otwarty w Excelu lub innej aplikacji."
            )
            logger.error(error_msg)
            raise DataProcessingError(error_msg) from e
        except Exception as e:
            error_msg = f"Błąd eksportowania do Excel: {e}"
            logger.error(error_msg)
            raise DataProcessingError(error_msg) from e
    
    def export_results(
        self,
        results_df: pd.DataFrame,
        top_10_df: Optional[pd.DataFrame] = None,
        growing_df: Optional[pd.DataFrame] = None,
        risky_df: Optional[pd.DataFrame] = None
    ) -> dict:
        logger.info("Eksportowanie wszystkich wyników")
        
        csv_path = self.export_to_csv(results_df)
        
        additional_sheets = {}
        if top_10_df is not None:
            additional_sheets["Top 10"] = top_10_df
        if growing_df is not None:
            additional_sheets["Najszybciej rozwijające się"] = growing_df
        if risky_df is not None:
            additional_sheets["Najbardziej ryzykowne"] = risky_df
        
        excel_path = self.export_to_excel(
            results_df,
            additional_sheets=additional_sheets if additional_sheets else None
        )
        
        return {
            "csv": csv_path,
            "excel": excel_path
        }

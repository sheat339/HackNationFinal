from pathlib import Path
from typing import Optional, List, Set, Dict
import pandas as pd

from src.utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseLoader:
    def __init__(self, database_dir: Path = Path("database")):
        self.database_dir = Path(database_dir)
        self.wsk_fin_path = self.database_dir / "wsk_fin.csv"
        self.krz_pkd_path = self.database_dir / "krz_pkd.csv"
        self.mapowanie_path = self.database_dir / "mapowanie_pkd.xlsx"
    
    def get_available_pkd_codes(self) -> Set[str]:
        pkd_codes = set()
        
        if self.wsk_fin_path.exists():
            try:
                df = pd.read_csv(self.wsk_fin_path, sep=';', encoding='utf-8', low_memory=False, usecols=['PKD'])
                if not df.empty and 'PKD' in df.columns:
                    for pkd in df['PKD'].dropna().unique():
                        pkd_str = str(pkd).strip()
                        if len(pkd_str) >= 2 and pkd_str != 'OG':
                            pkd_codes.add(pkd_str[:2])
                logger.info(f"Znaleziono {len(pkd_codes)} kodów PKD w wsk_fin.csv")
            except Exception as e:
                logger.error(f"Błąd odczytu PKD z wsk_fin.csv: {e}")
        else:
            logger.warning(f"Plik {self.wsk_fin_path} nie istnieje")
        
        return pkd_codes
    
    def get_available_years(self) -> List[int]:
        years = []
        if self.wsk_fin_path.exists():
            try:
                df = pd.read_csv(self.wsk_fin_path, sep=';', encoding='utf-8', low_memory=False, nrows=1)
                year_cols = [col for col in df.columns if col.isdigit() and 2000 <= int(col) <= 2030]
                years = sorted([int(col) for col in year_cols])
            except Exception as e:
                logger.error(f"Błąd odczytu lat z wsk_fin.csv: {e}")
        return years
    
    def load_financial_data(self, pkd_code: str, years: list) -> Optional[pd.DataFrame]:
        if not self.wsk_fin_path.exists():
            logger.warning(f"Plik {self.wsk_fin_path} nie istnieje")
            return None
        
        try:
            df = pd.read_csv(self.wsk_fin_path, sep=';', encoding='utf-8', low_memory=False)
            
            if df.empty:
                return None
            
            if 'PKD' not in df.columns:
                logger.error("Kolumna 'PKD' nie istnieje w pliku wsk_fin.csv")
                return None
            
            pkd_code_short = pkd_code[:2] if len(pkd_code) >= 2 else pkd_code
            
            filtered = df[df['PKD'].astype(str).str.startswith(pkd_code_short, na=False)]
            
            if filtered.empty:
                logger.warning(f"Brak danych dla PKD {pkd_code_short} w wsk_fin.csv")
                return None
            
            def parse_value(val):
                if pd.isna(val) or val is None:
                    return None
                try:
                    val_str = str(val).replace('\xa0', ' ').replace(' ', '').replace(',', '.')
                    return float(val_str)
                except:
                    return None
            
            year_columns = [str(year) for year in years]
            available_years = [col for col in year_columns if col in df.columns]
            
            if not available_years:
                all_year_cols = [col for col in df.columns if col.isdigit() and 2000 <= int(col) <= 2030]
                available_years = sorted(all_year_cols, key=int)[-len(years):] if len(all_year_cols) >= len(years) else all_year_cols
                logger.info(f"Używam dostępnych lat z pliku: {available_years}")
            
            result_by_year: Dict[int, Dict[str, float]] = {}
            
            for idx, row in filtered.iterrows():
                wskaznik = str(row.get('WSKAZNIK', '')).upper() if 'WSKAZNIK' in row.index else ''
                
                for year in years:
                    year_str = str(year)
                    if year_str not in df.columns:
                        continue
                    
                    value = parse_value(row[year_str])
                    if value is None or value <= 0:
                        continue
                    
                    if year not in result_by_year:
                        result_by_year[year] = {
                            'revenue': None,
                            'profit': None,
                            'assets': None,
                            'debt': None,
                            'num_companies': None
                        }
                    
                    value_scaled = value * 1000 if value < 1000000 else value
                    
                    if 'PRZYCHOD' in wskaznik or 'REVENUE' in wskaznik or 'GS' in wskaznik:
                        if result_by_year[year]['revenue'] is None:
                            result_by_year[year]['revenue'] = value_scaled
                    elif 'ZYSK' in wskaznik or 'PROFIT' in wskaznik or 'NP' in wskaznik or 'WYNIK' in wskaznik:
                        if result_by_year[year]['profit'] is None:
                            result_by_year[year]['profit'] = value_scaled
                    elif 'AKTYWA' in wskaznik or 'ASSETS' in wskaznik:
                        if result_by_year[year]['assets'] is None:
                            result_by_year[year]['assets'] = value_scaled
                    elif 'ZADŁUŻENIE' in wskaznik or 'DEBT' in wskaznik or 'DŁUG' in wskaznik:
                        if result_by_year[year]['debt'] is None:
                            result_by_year[year]['debt'] = value_scaled
                    elif 'LICZBA' in wskaznik or 'EN' in wskaznik:
                        if result_by_year[year]['num_companies'] is None:
                            result_by_year[year]['num_companies'] = int(value)
            
            result_data = []
            for year, data in result_by_year.items():
                revenue = data['revenue'] or (data['profit'] * 12.5 if data['profit'] else 1000000)
                profit = data['profit'] or (revenue * 0.08 if revenue else 0)
                assets = data['assets'] or (revenue * 1.8 if revenue else 2000000)
                debt = data['debt'] or (assets * 0.4 if assets else 800000)
                num_companies = data['num_companies'] or 1000
                
                result_data.append({
                    'year': year,
                    'revenue': revenue,
                    'profit': profit,
                    'assets': assets,
                    'debt': debt,
                    'bankruptcies': 0,
                    'num_companies': num_companies
                })
            
            if result_data:
                return pd.DataFrame(result_data)
            return None
            
        except Exception as e:
            logger.error(f"Błąd ładowania danych finansowych: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def load_bankruptcy_data(self, pkd_code: str, years: list) -> Optional[pd.DataFrame]:
        if not self.krz_pkd_path.exists():
            logger.warning(f"Plik {self.krz_pkd_path} nie istnieje")
            return None
        
        try:
            df = pd.read_csv(self.krz_pkd_path, sep=';', encoding='utf-8')
            
            if df.empty:
                return None
            
            pkd_col = None
            for col in ['pkd', 'PKD', 'kod_pkd', 'KOD_PKD']:
                if col in df.columns:
                    pkd_col = col
                    break
            
            if not pkd_col:
                logger.warning("Nie znaleziono kolumny z kodem PKD w krz_pkd.csv")
                return None
            
            rok_col = None
            for col in ['rok', 'Rok', 'ROK', 'year', 'Year']:
                if col in df.columns:
                    rok_col = col
                    break
            
            if not rok_col:
                logger.warning("Nie znaleziono kolumny z rokiem w krz_pkd.csv")
                return None
            
            upadlosci_col = None
            for col in ['liczba_upadlosci', 'liczba_upadłości', 'upadlosci', 'upadłości', 'liczba']:
                if col in df.columns:
                    upadlosci_col = col
                    break
            
            if not upadlosci_col:
                logger.warning("Nie znaleziono kolumny z liczbą upadłości w krz_pkd.csv")
                return None
            
            pkd_code_short = pkd_code[:2] if len(pkd_code) >= 2 else pkd_code
            
            filtered = df[df[pkd_col].astype(str).str.startswith(pkd_code_short, na=False)]
            
            if filtered.empty:
                return None
            
            result = {}
            for _, row in filtered.iterrows():
                try:
                    year = int(row[rok_col])
                    if year in years:
                        if year not in result:
                            result[year] = 0
                        upadlosci = int(row[upadlosci_col]) if pd.notna(row[upadlosci_col]) else 0
                        result[year] += upadlosci
                except (ValueError, KeyError):
                    continue
            
            if result:
                return pd.DataFrame([{'year': k, 'bankruptcies': v} for k, v in result.items()])
            return None
            
        except Exception as e:
            logger.error(f"Błąd ładowania danych o upadłościach: {e}")
            return None
    
    def load_sector_data_from_database(self, pkd_code: str, years: list = None) -> Optional[pd.DataFrame]:
        if years is None:
            years = self.get_available_years()
            if not years:
                years = list(range(2005, 2025))
            logger.info(f"Ładowanie danych dla PKD {pkd_code} z lat: {years}")
        
        financial_df = self.load_financial_data(pkd_code, years)
        bankruptcy_df = self.load_bankruptcy_data(pkd_code, years)
        
        if financial_df is None or financial_df.empty:
            logger.warning(f"Brak danych finansowych dla PKD {pkd_code}")
            return None
        
        financial_df['bankruptcies'] = 0
        
        if bankruptcy_df is not None and not bankruptcy_df.empty:
            financial_df = financial_df.merge(
                bankruptcy_df[['year', 'bankruptcies']],
                on='year',
                how='left',
                suffixes=('', '_new')
            )
            if 'bankruptcies_new' in financial_df.columns:
                financial_df['bankruptcies'] = financial_df['bankruptcies_new'].fillna(0).astype(int)
                financial_df = financial_df.drop(columns=['bankruptcies_new'])
            else:
                financial_df['bankruptcies'] = financial_df['bankruptcies'].fillna(0).astype(int)
        else:
            financial_df['bankruptcies'] = 0
        
        financial_df['pkd_code'] = pkd_code
        if 'num_companies' not in financial_df.columns:
            financial_df['num_companies'] = 1000
        
        logger.info(f"Załadowano {len(financial_df)} rekordów dla PKD {pkd_code}, lata: {sorted(financial_df['year'].unique().tolist())}")
        return financial_df[['pkd_code', 'year', 'revenue', 'profit', 'assets', 'debt', 'bankruptcies', 'num_companies']]

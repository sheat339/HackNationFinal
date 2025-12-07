from typing import Dict, List, Optional
import requests
from datetime import datetime

from src.utils.logger import get_logger

logger = get_logger(__name__)


class RealtimeDataService:
    def __init__(self, api_key: Optional[str] = None):
        self.bdl_base_url = "https://bdl.stat.gov.pl/api/v1"
        self.api_key = api_key
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({"X-ClientId": self.api_key})
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        url = f"{self.bdl_base_url}/{endpoint}"
        params = params or {}
        params.setdefault("format", "json")
        params.setdefault("lang", "pl")
        
        try:
            logger.info(f"Żądanie do BDL API: {url} z parametrami: {params}")
            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 404:
                raise Exception("Dane nie znalezione")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Błąd żądania do BDL API: {e}")
            if hasattr(e, 'response') and e.response is not None and e.response.status_code == 404:
                raise Exception("Dane nie znalezione")
            raise Exception(f"Błąd połączenia z BDL API: {str(e)}")
        except Exception as e:
            if "404" in str(e) or "Not Found" in str(e):
                raise Exception("Dane nie znalezione")
            raise
    
    def get_subjects(self, parent_id: Optional[str] = None, search: Optional[str] = None) -> List[Dict]:
        try:
            if search:
                result = self._make_request("subjects/search", {"name": search})
            elif parent_id:
                result = self._make_request("subjects", {"parent-id": parent_id})
            else:
                result = self._make_request("subjects")
            
            if isinstance(result, dict) and "data" in result:
                return result["data"]
            elif isinstance(result, list):
                return result
            else:
                return []
        except Exception as e:
            logger.error(f"Błąd pobierania tematów: {e}")
            return []
    
    def get_variables(self, subject_id: Optional[str] = None, search: Optional[str] = None, 
                     years: Optional[List[int]] = None) -> List[Dict]:
        try:
            params = {}
            if subject_id:
                params["subject-id"] = subject_id
            if search:
                params["name"] = search
            if years:
                for year in years:
                    params.setdefault("year", []).append(str(year))
            
            if search:
                result = self._make_request("variables/search", params)
            else:
                result = self._make_request("variables", params)
            
            if isinstance(result, dict) and "data" in result:
                return result["data"]
            elif isinstance(result, list):
                return result
            else:
                return []
        except Exception as e:
            logger.error(f"Błąd pobierania zmiennych: {e}")
            return []
    
    def get_variable_details(self, variable_id: str) -> Optional[Dict]:
        try:
            result = self._make_request(f"variables/{variable_id}")
            return result
        except Exception as e:
            logger.error(f"Błąd pobierania szczegółów zmiennej: {e}")
            return None
    
    def get_data_by_variable(self, variable_id: str, unit_level: Optional[int] = None,
                            unit_parent_id: Optional[str] = None, years: Optional[List[int]] = None,
                            page: int = 1, page_size: int = 100) -> Dict:
        try:
            params = {
                "page": page,
                "page-size": page_size
            }
            
            if unit_level is not None:
                params["unit-level"] = unit_level
            if unit_parent_id:
                params["unit-parent-id"] = unit_parent_id
            if years:
                for year in years:
                    params.setdefault("year", []).append(str(year))
            
            result = self._make_request(f"data/by-variable/{variable_id}", params)
            return result
        except Exception as e:
            logger.error(f"Błąd pobierania danych dla zmiennej: {e}")
            raise Exception(f"Błąd pobierania danych dla zmiennej {variable_id}: {str(e)}")
    
    def get_data_by_unit(self, unit_id: str, variable_ids: List[str],
                         years: Optional[List[int]] = None) -> Dict:
        try:
            params = {}
            for var_id in variable_ids:
                params.setdefault("var-id", []).append(var_id)
            if years:
                for year in years:
                    params.setdefault("year", []).append(str(year))
            
            result = self._make_request(f"data/by-unit/{unit_id}", params)
            return result
        except Exception as e:
            logger.error(f"Błąd pobierania danych dla jednostki: {e}")
            raise Exception(f"Błąd pobierania danych dla jednostki {unit_id}: {str(e)}")
    
    def get_units(self, level: Optional[int] = None, parent_id: Optional[str] = None,
                  page: int = 1, page_size: int = 100) -> Dict:
        try:
            params = {
                "page": page,
                "page-size": page_size
            }
            if level is not None:
                params["level"] = level
            if parent_id:
                params["parent-id"] = parent_id
            
            result = self._make_request("units", params)
            return result
        except Exception as e:
            logger.error(f"Błąd pobierania jednostek: {e}")
            return {}
    
    def search_subjects_by_keyword(self, keyword: str) -> List[Dict]:
        return self.get_subjects(search=keyword)
    
    def get_popular_statistics(self, unit_level: int = 2) -> Dict:
        try:
            popular_subjects = ["Ludność", "Gospodarka", "Przemysł", "Handel", "Bezrobocie"]
            results = {}
            
            for subject_name in popular_subjects:
                subjects = self.search_subjects_by_keyword(subject_name)
                if subjects:
                    subject = subjects[0]
                    subject_id = subject.get("id") or subject.get("Id")
                    
                    if subject_id:
                        variables = self.get_variables(subject_id=subject_id)
                        if variables:
                            var = variables[0]
                            var_id = var.get("id") or var.get("Id")
                            
                            if var_id:
                                try:
                                    data = self.get_data_by_variable(
                                        str(var_id),
                                        unit_level=unit_level,
                                        page_size=20
                                    )
                                    results[subject_name] = {
                                        "subject": subject,
                                        "variable": var,
                                        "data": data
                                    }
                                except Exception as e:
                                    logger.warning(f"Nie udało się pobrać danych dla {subject_name}: {e}")
                                    results[subject_name] = {
                                        "subject": subject,
                                        "variable": var,
                                        "error": str(e)
                                    }
            
            return {
                "timestamp": datetime.now().isoformat(),
                "unit_level": unit_level,
                "statistics": results
            }
        except Exception as e:
            logger.error(f"Błąd pobierania popularnych statystyk: {e}")
            raise Exception(f"Błąd pobierania popularnych statystyk: {str(e)}")
    
    def get_sector_data_from_bdl(self, pkd_code: str, unit_level: int = 2, years: Optional[List[int]] = None) -> Dict:
        try:
            logger.info(f"Pobieranie danych BDL dla PKD {pkd_code}")
            
            economic_subjects = ["Gospodarka", "Przemysł", "Handel", "Usługi", "Ludność"]
            metrics = {}
            
            for subject_name in economic_subjects:
                subjects = self.search_subjects_by_keyword(subject_name)
                if subjects:
                    subject = subjects[0]
                    subject_id = subject.get("id") or subject.get("Id")
                    
                    if subject_id:
                        variables = self.get_variables(subject_id=subject_id, years=years)
                        if variables:
                            var = variables[0]
                            var_id = var.get("id") or var.get("Id")
                            var_name = var.get("name") or var.get("Name", subject_name)
                            
                            if var_id:
                                try:
                                    data = self.get_data_by_variable(
                                        str(var_id),
                                        unit_level=unit_level,
                                        years=years,
                                        page_size=50
                                    )
                                    
                                    results = data.get("results") or data.get("data") or []
                                    if isinstance(results, list) and len(results) > 0:
                                        total_value = 0
                                        count = 0
                                        for item in results:
                                            values = item.get("values") or item.get("Values") or []
                                            if isinstance(values, list):
                                                for v in values:
                                                    val = v.get("value") or v.get("Value")
                                                    if val is not None:
                                                        try:
                                                            total_value += float(val)
                                                            count += 1
                                                        except (ValueError, TypeError):
                                                            pass
                                        
                                        if count > 0:
                                            avg_value = total_value / count
                                            metrics[var_name] = {
                                                "value": avg_value,
                                                "count": count,
                                                "variable_id": var_id
                                            }
                                except Exception as e:
                                    logger.warning(f"Nie udało się pobrać danych dla {subject_name}: {e}")
            
            return {
                "pkd_code": pkd_code,
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics,
                "unit_level": unit_level
            }
        except Exception as e:
            logger.error(f"Błąd pobierania danych BDL dla PKD {pkd_code}: {e}")
            raise Exception(f"Błąd pobierania danych BDL: {str(e)}")
    
    def fetch_gus_data(self, pkd_code: str) -> Dict:
        try:
            logger.info(f"Pobieranie danych BDL dla PKD {pkd_code}")
            return self.get_sector_data_from_bdl(pkd_code, unit_level=2)
        except Exception as e:
            logger.error(f"Błąd pobierania danych BDL: {e}")
            return {
                "pkd_code": pkd_code,
                "timestamp": datetime.now().isoformat(),
                "metrics": {},
                "error": str(e)
            }
    
    def fetch_all_sources(self, pkd_code: str) -> Dict:
        results = {
            "pkd_code": pkd_code,
            "timestamp": datetime.now().isoformat(),
            "sources": {}
        }
        
        results["sources"]["gus"] = self.fetch_gus_data(pkd_code)
        
        return results

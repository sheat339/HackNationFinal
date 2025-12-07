from typing import Dict, Optional, List
import requests
from datetime import datetime

from src.utils.logger import get_logger

logger = get_logger(__name__)


class IntegrationService:
    def __init__(self):
        self.nbp_api_url = "https://api.nbp.pl/api"
        self.gpw_api_url = "https://www.gpw.pl"
    
    def get_nbp_exchange_rates(self, currency: str = "EUR", days: int = 30) -> Optional[Dict]:
        try:
            url = f"{self.nbp_api_url}/exchangerates/rates/A/{currency}/last/{days}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "currency": currency,
                "rates": data.get("rates", []),
                "source": "NBP"
            }
        except Exception as e:
            logger.warning(f"Błąd pobierania kursów NBP: {e}")
            return None
    
    def get_economic_indicators(self) -> Dict:
        try:
            indicators = {}
            
            eur_rate = self.get_nbp_exchange_rates("EUR", 1)
            if eur_rate and eur_rate.get("rates"):
                latest_rate = eur_rate["rates"][-1]
                indicators["eur_rate"] = {
                    "value": latest_rate.get("mid", 0),
                    "date": latest_rate.get("effectiveDate", ""),
                    "source": "NBP"
                }
            
            usd_rate = self.get_nbp_exchange_rates("USD", 1)
            if usd_rate and usd_rate.get("rates"):
                latest_rate = usd_rate["rates"][-1]
                indicators["usd_rate"] = {
                    "value": latest_rate.get("mid", 0),
                    "date": latest_rate.get("effectiveDate", ""),
                    "source": "NBP"
                }
            
            return {
                "timestamp": datetime.now().isoformat(),
                "indicators": indicators
            }
        except Exception as e:
            logger.error(f"Błąd pobierania wskaźników ekonomicznych: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "indicators": {}
            }
    
    def enrich_sector_data(self, sector_data: Dict, pkd_code: str) -> Dict:
        try:
            enriched = sector_data.copy()
            
            economic_indicators = self.get_economic_indicators()
            enriched["economic_context"] = economic_indicators.get("indicators", {})
            
            return enriched
        except Exception as e:
            logger.warning(f"Błąd wzbogacania danych sektora: {e}")
            return sector_data


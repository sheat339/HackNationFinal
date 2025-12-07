from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

from src.utils.logger import get_logger

logger = get_logger(__name__)


class AlertService:
    def __init__(self):
        self.alert_thresholds = {
            'index_change': 0.1,
            'growth_change': 0.15,
            'risk_change': 0.2
        }
    
    def check_index_change(self, current_sector: Dict, previous_sector: Optional[Dict]) -> Optional[Dict]:
        if not previous_sector:
            return None
        
        try:
            current_index = current_sector.get('final_index', 0)
            previous_index = previous_sector.get('final_index', 0)
            
            if previous_index == 0:
                return None
            
            change = (current_index - previous_index) / previous_index
            threshold = self.alert_thresholds['index_change']
            
            if abs(change) >= threshold:
                return {
                    'type': 'index_change',
                    'severity': 'high' if abs(change) >= threshold * 2 else 'medium',
                    'message': f"Znaczna zmiana indeksu: {change*100:.1f}%",
                    'change': change,
                    'current': current_index,
                    'previous': previous_index
                }
            
            return None
        except Exception as e:
            logger.warning(f"Błąd sprawdzania zmiany indeksu: {e}")
            return None
    
    def check_growth_change(self, current_sector: Dict, previous_sector: Optional[Dict]) -> Optional[Dict]:
        if not previous_sector:
            return None
        
        try:
            current_growth = current_sector.get('growth_score', 0)
            previous_growth = previous_sector.get('growth_score', 0)
            
            change = abs(current_growth - previous_growth)
            threshold = self.alert_thresholds['growth_change']
            
            if change >= threshold:
                direction = 'wzrost' if current_growth > previous_growth else 'spadek'
                return {
                    'type': 'growth_change',
                    'severity': 'high' if change >= threshold * 2 else 'medium',
                    'message': f"Znaczna zmiana wskaźnika wzrostu: {direction} o {change*100:.1f}%",
                    'change': current_growth - previous_growth,
                    'current': current_growth,
                    'previous': previous_growth
                }
            
            return None
        except Exception as e:
            logger.warning(f"Błąd sprawdzania zmiany wzrostu: {e}")
            return None
    
    def check_risk_change(self, current_sector: Dict, previous_sector: Optional[Dict]) -> Optional[Dict]:
        if not previous_sector:
            return None
        
        try:
            current_risk = current_sector.get('risk_score', 0)
            previous_risk = previous_sector.get('risk_score', 0)
            
            change = abs(current_risk - previous_risk)
            threshold = self.alert_thresholds['risk_change']
            
            if change >= threshold:
                direction = 'wzrost' if current_risk > previous_risk else 'spadek'
                severity = 'high' if current_risk > previous_risk else 'medium'
                return {
                    'type': 'risk_change',
                    'severity': severity,
                    'message': f"Znaczna zmiana ryzyka: {direction} o {change*100:.1f}%",
                    'change': current_risk - previous_risk,
                    'current': current_risk,
                    'previous': previous_risk
                }
            
            return None
        except Exception as e:
            logger.warning(f"Błąd sprawdzania zmiany ryzyka: {e}")
            return None
    
    def check_all_alerts(self, current_sector: Dict, previous_sector: Optional[Dict]) -> List[Dict]:
        alerts = []
        
        alert = self.check_index_change(current_sector, previous_sector)
        if alert:
            alerts.append(alert)
        
        alert = self.check_growth_change(current_sector, previous_sector)
        if alert:
            alerts.append(alert)
        
        alert = self.check_risk_change(current_sector, previous_sector)
        if alert:
            alerts.append(alert)
        
        return alerts
    
    def check_category_change(self, current_sector: Dict, previous_sector: Optional[Dict]) -> Optional[Dict]:
        if not previous_sector:
            return None
        
        try:
            current_category = current_sector.get('category')
            previous_category = previous_sector.get('category')
            
            if current_category != previous_category:
                category_order = [
                    'Bardzo dobra kondycja',
                    'Dobra kondycja',
                    'Średnia kondycja',
                    'Słaba kondycja',
                    'Bardzo słaba kondycja'
                ]
                
                current_idx = category_order.index(current_category) if current_category in category_order else 2
                previous_idx = category_order.index(previous_category) if previous_category in category_order else 2
                
                improvement = current_idx < previous_idx
                
                return {
                    'type': 'category_change',
                    'severity': 'high',
                    'message': f"Zmiana kategorii: {previous_category} → {current_category}",
                    'improvement': improvement,
                    'current': current_category,
                    'previous': previous_category
                }
            
            return None
        except Exception as e:
            logger.warning(f"Błąd sprawdzania zmiany kategorii: {e}")
            return None


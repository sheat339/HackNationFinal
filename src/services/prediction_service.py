from typing import Dict, List, Optional
import pandas as pd
import numpy as np

from src.utils.logger import get_logger

logger = get_logger(__name__)


class PredictionService:
    def __init__(self):
        pass
    
    def predict_next_year(self, history_data: List[Dict]) -> Optional[Dict]:
        if not history_data or len(history_data) < 2:
            return None
        
        try:
            df = pd.DataFrame(history_data)
            df = df.sort_values('year')
            
            predictions = {}
            
            for column in ['revenue', 'profit', 'assets', 'debt']:
                if column in df.columns:
                    values = df[column].values
                    if len(values) >= 2:
                        trend = self._calculate_trend(values)
                        last_value = values[-1]
                        predicted = last_value * (1 + trend)
                        predictions[column] = max(0, predicted)
            
            if predictions:
                last_year = df['year'].max()
                predictions['year'] = int(last_year) + 1
                predictions['predicted'] = True
                return predictions
            
            return None
        except Exception as e:
            logger.error(f"Błąd prognozowania: {e}")
            return None
    
    def _calculate_trend(self, values: np.ndarray) -> float:
        if len(values) < 2:
            return 0.0
        
        try:
            growth_rates = []
            for i in range(1, len(values)):
                if values[i-1] > 0:
                    rate = (values[i] - values[i-1]) / values[i-1]
                    growth_rates.append(rate)
            
            if growth_rates:
                avg_growth = np.mean(growth_rates)
                return float(avg_growth)
            
            return 0.0
        except Exception as e:
            logger.warning(f"Błąd obliczania trendu: {e}")
            return 0.0
    
    def get_trend_indicator(self, history_data: List[Dict], metric: str = 'revenue') -> str:
        if not history_data or len(history_data) < 2:
            return "→"
        
        try:
            df = pd.DataFrame(history_data)
            df = df.sort_values('year')
            
            if metric not in df.columns:
                return "→"
            
            values = df[metric].values
            if len(values) < 2:
                return "→"
            
            recent_values = values[-3:] if len(values) >= 3 else values
            trend = self._calculate_trend(recent_values)
            
            if trend > 0.05:
                return "↑"
            elif trend < -0.05:
                return "↓"
            else:
                return "→"
        except Exception as e:
            logger.warning(f"Błąd określania trendu: {e}")
            return "→"
    
    def predict_sector_index(self, sector_data: Dict, history_data: List[Dict]) -> Optional[float]:
        if not history_data or len(history_data) < 2:
            return None
        
        try:
            df = pd.DataFrame(history_data)
            df = df.sort_values('year')
            
            if 'revenue' in df.columns and 'profit' in df.columns:
                revenue_trend = self._calculate_trend(df['revenue'].values)
                profit_trend = self._calculate_trend(df['profit'].values)
                
                current_index = sector_data.get('final_index', 0)
                
                predicted_change = (revenue_trend * 0.4 + profit_trend * 0.6) * 0.5
                predicted_index = current_index * (1 + predicted_change)
                
                return max(0.0, min(1.0, predicted_index))
            
            return None
        except Exception as e:
            logger.error(f"Błąd prognozowania indeksu: {e}")
            return None


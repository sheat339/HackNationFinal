from typing import Dict, List, Optional
import pandas as pd
import numpy as np

from src.utils.logger import get_logger

logger = get_logger(__name__)


class AnalyticsService:
    def __init__(self):
        pass
    
    def calculate_correlations(self, sectors_df: pd.DataFrame) -> Dict[str, float]:
        try:
            numeric_cols = sectors_df.select_dtypes(include=[np.number]).columns
            correlations = {}
            
            if 'final_index' in numeric_cols:
                for col in numeric_cols:
                    if col != 'final_index':
                        corr = sectors_df['final_index'].corr(sectors_df[col])
                        if not pd.isna(corr):
                            correlations[col] = float(corr)
            
            return correlations
        except Exception as e:
            logger.error(f"Błąd obliczania korelacji: {e}")
            return {}
    
    def find_correlated_sectors(self, sector1: Dict, sector2: Dict) -> float:
        try:
            metrics = [
                'size_score', 'growth_score', 'profitability_score',
                'debt_score', 'risk_score'
            ]
            
            correlations = []
            
            for metric in metrics:
                val1 = sector1.get(metric, 0)
                val2 = sector2.get(metric, 0)
                
                if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                    if val1 != 0 or val2 != 0:
                        corr = 1.0 - abs(val1 - val2) / max(abs(val1), abs(val2), 1.0)
                        correlations.append(corr)
            
            if correlations:
                return float(np.mean(correlations))
            
            return 0.0
        except Exception as e:
            logger.warning(f"Błąd obliczania korelacji sektorów: {e}")
            return 0.0
    
    def analyze_seasonality(self, history_data: List[Dict]) -> Optional[Dict]:
        if not history_data or len(history_data) < 4:
            return None
        
        try:
            df = pd.DataFrame(history_data)
            df = df.sort_values('year')
            
            if 'revenue' not in df.columns:
                return None
            
            revenues = df['revenue'].values
            
            if len(revenues) < 4:
                return None
            
            avg_growth = np.mean([(revenues[i] - revenues[i-1]) / revenues[i-1] 
                                 for i in range(1, len(revenues)) if revenues[i-1] > 0])
            
            volatility = np.std(revenues) / np.mean(revenues) if np.mean(revenues) > 0 else 0
            
            return {
                'average_growth': float(avg_growth),
                'volatility': float(volatility),
                'trend': 'wzrostowy' if avg_growth > 0.05 else 'spadkowy' if avg_growth < -0.05 else 'stabilny'
            }
        except Exception as e:
            logger.error(f"Błąd analizy sezonowości: {e}")
            return None
    
    def cluster_sectors(self, sectors_df: pd.DataFrame, n_clusters: int = 5) -> pd.DataFrame:
        try:
            from sklearn.cluster import KMeans
            from sklearn.preprocessing import StandardScaler
            
            numeric_cols = ['size_score', 'growth_score', 'profitability_score', 
                          'debt_score', 'risk_score']
            
            available_cols = [col for col in numeric_cols if col in sectors_df.columns]
            
            if len(available_cols) < 2:
                return sectors_df
            
            X = sectors_df[available_cols].fillna(0).values
            
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(X_scaled)
            
            sectors_df = sectors_df.copy()
            sectors_df['cluster'] = clusters
            
            return sectors_df
        except ImportError:
            logger.warning("scikit-learn nie jest zainstalowany, pomijam klasteryzację")
            return sectors_df
        except Exception as e:
            logger.error(f"Błąd klasteryzacji: {e}")
            return sectors_df
    
    def calculate_statistics(self, sectors_df: pd.DataFrame) -> Dict:
        try:
            stats = {}
            
            numeric_cols = sectors_df.select_dtypes(include=[np.number]).columns
            
            for col in numeric_cols:
                if col in sectors_df.columns:
                    stats[col] = {
                        'mean': float(sectors_df[col].mean()),
                        'median': float(sectors_df[col].median()),
                        'std': float(sectors_df[col].std()),
                        'min': float(sectors_df[col].min()),
                        'max': float(sectors_df[col].max())
                    }
            
            if 'category' in sectors_df.columns:
                stats['category_distribution'] = sectors_df['category'].value_counts().to_dict()
            
            return stats
        except Exception as e:
            logger.error(f"Błąd obliczania statystyk: {e}")
            return {}


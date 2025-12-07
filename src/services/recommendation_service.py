from typing import List, Dict, Optional
import pandas as pd
import numpy as np

from src.utils.logger import get_logger

logger = get_logger(__name__)


class RecommendationService:
    def __init__(self):
        pass
    
    def find_similar_sectors(self, target_sector: Dict, all_sectors: List[Dict], top_n: int = 5) -> List[Dict]:
        if not all_sectors or len(all_sectors) < 2:
            return []
        
        try:
            target_pkd = target_sector.get('pkd_code')
            if not target_pkd:
                return []
            
            similarities = []
            
            for sector in all_sectors:
                if sector.get('pkd_code') == target_pkd:
                    continue
                
                similarity = self._calculate_similarity(target_sector, sector)
                if similarity > 0:
                    similarities.append({
                        'sector': sector,
                        'similarity': similarity
                    })
            
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            return [item['sector'] for item in similarities[:top_n]]
        except Exception as e:
            logger.error(f"Błąd znajdowania podobnych sektorów: {e}")
            return []
    
    def _calculate_similarity(self, sector1: Dict, sector2: Dict) -> float:
        try:
            metrics = [
                'size_score', 'growth_score', 'profitability_score',
                'debt_score', 'risk_score', 'final_index'
            ]
            
            similarity_score = 0.0
            weight_sum = 0.0
            
            for metric in metrics:
                val1 = sector1.get(metric, 0)
                val2 = sector2.get(metric, 0)
                
                if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                    diff = abs(val1 - val2)
                    similarity = 1.0 - min(1.0, diff)
                    
                    weight = 1.0 if metric == 'final_index' else 0.8
                    similarity_score += similarity * weight
                    weight_sum += weight
            
            if weight_sum > 0:
                return similarity_score / weight_sum
            
            return 0.0
        except Exception as e:
            logger.warning(f"Błąd obliczania podobieństwa: {e}")
            return 0.0
    
    def recommend_based_on_history(self, target_sector: Dict, all_sectors: List[Dict]) -> List[Dict]:
        try:
            target_category = target_sector.get('category')
            target_growth = target_sector.get('growth_score', 0)
            
            recommendations = []
            
            for sector in all_sectors:
                if sector.get('pkd_code') == target_sector.get('pkd_code'):
                    continue
                
                sector_category = sector.get('category')
                sector_growth = sector.get('growth_score', 0)
                
                score = 0.0
                
                if sector_category == target_category:
                    score += 0.3
                
                if abs(sector_growth - target_growth) < 0.1:
                    score += 0.4
                
                if sector.get('final_index', 0) > target_sector.get('final_index', 0):
                    score += 0.3
                
                if score > 0.5:
                    recommendations.append({
                        'sector': sector,
                        'score': score
                    })
            
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return [item['sector'] for item in recommendations[:5]]
        except Exception as e:
            logger.error(f"Błąd rekomendacji: {e}")
            return []
    
    def get_trending_sectors(self, all_sectors: List[Dict], top_n: int = 5) -> List[Dict]:
        try:
            trending = []
            
            for sector in all_sectors:
                growth = sector.get('growth_score', 0)
                final_index = sector.get('final_index', 0)
                
                trend_score = growth * 0.6 + final_index * 0.4
                
                trending.append({
                    'sector': sector,
                    'trend_score': trend_score
                })
            
            trending.sort(key=lambda x: x['trend_score'], reverse=True)
            return [item['sector'] for item in trending[:top_n]]
        except Exception as e:
            logger.error(f"Błąd znajdowania trendujących sektorów: {e}")
            return []


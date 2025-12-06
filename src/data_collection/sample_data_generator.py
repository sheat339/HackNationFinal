"""
Generator przykładowych danych do testowania (symulacja rzeczywistych danych)
"""

import pandas as pd
import numpy as np
from typing import List, Dict

class SampleDataGenerator:
    """Generator przykładowych danych dla testów"""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        np.random.seed(seed)
    
    def generate_sector_data(self, pkd_code: str, years: List[int], 
                            base_revenue: float = None,
                            base_profit_margin: float = None,
                            growth_trend: float = None) -> pd.DataFrame:
        """
        Generuje przykładowe dane dla sektora
        
        Args:
            pkd_code: Kod PKD
            years: Lista lat
            base_revenue: Bazowy przychód (jeśli None, losowy)
            base_profit_margin: Bazowa marża zysku (jeśli None, losowa)
            growth_trend: Trend wzrostu (jeśli None, losowy)
        """
        if base_revenue is None:
            base_revenue = np.random.uniform(1000000, 10000000)
        
        if base_profit_margin is None:
            base_profit_margin = np.random.uniform(0.02, 0.15)
        
        if growth_trend is None:
            growth_trend = np.random.uniform(-0.05, 0.20)
        
        data = []
        current_revenue = base_revenue
        current_assets = base_revenue * np.random.uniform(1.5, 3.0)
        current_debt = current_assets * np.random.uniform(0.2, 0.6)
        num_companies = np.random.randint(1000, 10000)
        
        for year in years:
            # Dodaj trend wzrostu z losowym szumem
            revenue_growth = growth_trend + np.random.uniform(-0.05, 0.05)
            current_revenue *= (1 + revenue_growth)
            
            # Zysk zależy od przychodu i marży (z małą zmiennością)
            profit_margin = base_profit_margin + np.random.uniform(-0.02, 0.02)
            profit = current_revenue * profit_margin
            
            # Aktywa rosną wraz z przychodami
            assets_growth = revenue_growth * np.random.uniform(0.8, 1.2)
            current_assets *= (1 + assets_growth)
            
            # Zadłużenie zależy od aktywów
            debt_ratio = np.random.uniform(0.2, 0.6)
            current_debt = current_assets * debt_ratio
            
            # Upadłości zależą od kondycji sektora
            bankruptcy_rate = max(0.01, min(0.10, 0.05 - profit_margin * 0.3))
            bankruptcies = int(num_companies * bankruptcy_rate)
            
            data.append({
                'pkd_code': pkd_code,
                'year': year,
                'revenue': max(0, current_revenue),
                'profit': max(0, profit),
                'assets': max(0, current_assets),
                'debt': max(0, current_debt),
                'bankruptcies': max(0, bankruptcies),
                'num_companies': max(100, num_companies + np.random.randint(-100, 200))
            })
        
        return pd.DataFrame(data)
    
    def generate_realistic_sector_data(self, pkd_code: str, years: List[int]) -> pd.DataFrame:
        """
        Generuje bardziej realistyczne dane dla sektora na podstawie jego charakterystyki
        """
        # Charakterystyki różnych sektorów
        sector_profiles = {
            "10": {"base_revenue": 5000000, "profit_margin": 0.08, "growth": 0.10},  # Produkcja żywności - stabilna
            "20": {"base_revenue": 8000000, "profit_margin": 0.12, "growth": 0.15},  # Chemikalia - dobra rentowność
            "25": {"base_revenue": 6000000, "profit_margin": 0.06, "growth": 0.08},  # Wyroby metalowe - średnia
            "26": {"base_revenue": 4000000, "profit_margin": 0.15, "growth": 0.20},  # Elektronika - wysoki wzrost
            "28": {"base_revenue": 10000000, "profit_margin": 0.05, "growth": 0.12}, # Pojazdy - duża skala
            "36": {"base_revenue": 7000000, "profit_margin": 0.04, "growth": 0.18},  # Budownictwo - wysokie tempo
            "46": {"base_revenue": 9000000, "profit_margin": 0.03, "growth": 0.10},  # Handel hurtowy - niska marża
            "47": {"base_revenue": 8500000, "profit_margin": 0.04, "growth": 0.08},  # Handel detaliczny
            "49": {"base_revenue": 5500000, "profit_margin": 0.05, "growth": 0.10},  # Transport
            "55": {"base_revenue": 3000000, "profit_margin": 0.10, "growth": 0.15},  # Zakwaterowanie
            "61": {"base_revenue": 6000000, "profit_margin": 0.12, "growth": 0.12},  # Telekomunikacja
            "62": {"base_revenue": 3500000, "profit_margin": 0.18, "growth": 0.25},  # IT - bardzo wysoki wzrost
            "64": {"base_revenue": 12000000, "profit_margin": 0.20, "growth": 0.08}, # Finanse - wysoka rentowność
            "68": {"base_revenue": 4500000, "profit_margin": 0.15, "growth": 0.10},  # Nieruchomości
            "86": {"base_revenue": 6500000, "profit_margin": 0.08, "growth": 0.12}   # Opieka zdrowotna
        }
        
        profile = sector_profiles.get(pkd_code, {
            "base_revenue": 5000000,
            "profit_margin": 0.08,
            "growth": 0.10
        })
        
        return self.generate_sector_data(
            pkd_code,
            years,
            base_revenue=profile["base_revenue"],
            base_profit_margin=profile["profit_margin"],
            growth_trend=profile["growth"]
        )


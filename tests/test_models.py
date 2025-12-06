"""
Unit tests for models.
"""

import pytest
from src.models.config import Weights, Config, Category, Classification
from src.models.sector import SectorData
import pandas as pd


class TestWeights:
    """Tests for Weights model."""
    
    def test_valid_weights(self):
        """Test that valid weights sum to 1.0."""
        weights = Weights(
            size=0.20,
            growth=0.25,
            profitability=0.20,
            debt=0.15,
            risk=0.20
        )
        assert weights.validate() is True
    
    def test_invalid_weights(self):
        """Test that invalid weights don't sum to 1.0."""
        weights = Weights(
            size=0.30,
            growth=0.30,
            profitability=0.30,
            debt=0.20,
            risk=0.20
        )
        assert weights.validate() is False
    
    def test_weights_from_dict(self):
        """Test creating weights from dictionary."""
        data = {
            "size": 0.20,
            "growth": 0.25,
            "profitability": 0.20,
            "debt": 0.15,
            "risk": 0.20
        }
        weights = Weights(**data)
        assert weights.size == 0.20
        assert weights.validate() is True


class TestSectorData:
    """Tests for SectorData model."""
    
    def test_sector_data_creation(self):
        """Test creating SectorData object."""
        sector = SectorData(
            pkd_code="62",
            year=2024,
            revenue=1000000.0,
            profit=150000.0,
            assets=2000000.0,
            debt=500000.0,
            bankruptcies=10,
            num_companies=1000
        )
        assert sector.pkd_code == "62"
        assert sector.year == 2024
        assert sector.revenue == 1000000.0
    
    def test_sector_data_from_dataframe(self):
        """Test creating SectorData from DataFrame."""
        df = pd.DataFrame({
            "pkd_code": ["62", "62"],
            "year": [2023, 2024],
            "revenue": [900000.0, 1000000.0],
            "profit": [135000.0, 150000.0],
            "assets": [1800000.0, 2000000.0],
            "debt": [450000.0, 500000.0],
            "bankruptcies": [8, 10],
            "num_companies": [950, 1000]
        })
        
        sectors = SectorData.from_dataframe(df)
        assert len(sectors) == 2
        assert sectors[0].pkd_code == "62"
        assert sectors[1].year == 2024


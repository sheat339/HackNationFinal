"""
Unit tests for services.
"""

import pytest
import pandas as pd
from pathlib import Path

from src.models.config import Config, Weights, AnalysisPeriod, DataSources, DataSource, Classification, Category, Visualization
from src.services.data_service import DataService
from src.services.analysis_service import AnalysisService
from src.services.export_service import ExportService


@pytest.fixture
def sample_config():
    """Create sample configuration for tests."""
    weights = Weights()
    analysis_period = AnalysisPeriod(start_year=2023, end_year=2024)
    data_sources = DataSources(
        gus=DataSource(),
        krs=DataSource(),
        gpw=DataSource(),
        nbp=DataSource()
    )
    categories = [
        Category(name="Bardzo dobra kondycja", min_score=0.75),
        Category(name="Dobra kondycja", min_score=0.60),
    ]
    classification = Classification(categories=categories)
    visualization = Visualization(output_format=["html"])
    
    return Config(
        pkd_level="division",
        pkd_year=2007,
        weights=weights,
        analysis_period=analysis_period,
        data_sources=data_sources,
        classification=classification,
        visualization=visualization
    )


@pytest.fixture
def sample_sector_data():
    """Create sample sector data for tests."""
    return pd.DataFrame({
        "pkd_code": ["62", "62"],
        "year": [2023, 2024],
        "revenue": [900000.0, 1000000.0],
        "profit": [135000.0, 150000.0],
        "assets": [1800000.0, 2000000.0],
        "debt": [450000.0, 500000.0],
        "bankruptcies": [8, 10],
        "num_companies": [950, 1000]
    })


class TestDataService:
    """Tests for DataService."""
    
    def test_data_service_initialization(self, sample_config):
        """Test DataService initialization."""
        service = DataService(sample_config)
        assert service.config == sample_config
        assert service.collector is not None
    
    def test_validate_sector_data(self, sample_config, sample_sector_data):
        """Test sector data validation."""
        service = DataService(sample_config)
        assert service.validate_sector_data(sample_sector_data) is True
    
    def test_validate_sector_data_missing_columns(self, sample_config):
        """Test validation with missing columns."""
        service = DataService(sample_config)
        invalid_data = pd.DataFrame({"pkd_code": ["62"], "year": [2024]})
        
        with pytest.raises(Exception):
            service.validate_sector_data(invalid_data)


class TestExportService:
    """Tests for ExportService."""
    
    def test_export_service_initialization(self, sample_config, tmp_path):
        """Test ExportService initialization."""
        service = ExportService(sample_config, tmp_path)
        assert service.output_dir == tmp_path
        assert tmp_path.exists()
    
    def test_export_to_csv(self, sample_config, sample_sector_data, tmp_path):
        """Test CSV export."""
        service = ExportService(sample_config, tmp_path)
        filepath = service.export_to_csv(sample_sector_data, "test.csv")
        
        assert filepath.exists()
        assert filepath.suffix == ".csv"
        
        # Verify content
        loaded = pd.read_csv(filepath)
        assert len(loaded) == len(sample_sector_data)
    
    def test_export_to_excel(self, sample_config, sample_sector_data, tmp_path):
        """Test Excel export."""
        service = ExportService(sample_config, tmp_path)
        filepath = service.export_to_excel(sample_sector_data, "test.xlsx")
        
        assert filepath.exists()
        assert filepath.suffix == ".xlsx"
        
        # Verify content
        loaded = pd.read_excel(filepath)
        assert len(loaded) == len(sample_sector_data)


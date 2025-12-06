from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from typing import Optional
import pandas as pd
from pathlib import Path

from src.models.config import Config
from src.utils.config_loader import load_config
from src.services.data_service import DataService
from src.services.analysis_service import AnalysisService
from src.utils.logger import get_logger

logger = get_logger(__name__)

config: Optional[Config] = None
data_service: Optional[DataService] = None
analysis_service: Optional[AnalysisService] = None


def create_app() -> FastAPI:
    app = FastAPI(
        title="Indeks Branż API",
        description="API do analizy kondycji sektorów polskiej gospodarki",
        version="1.0.0",
    )
    
    @app.on_event("startup")
    async def startup_event():
        global config, data_service, analysis_service
        
        try:
            logger.info("Inicjalizacja serwisów API...")
            config = load_config()
            data_service = DataService(config)
            analysis_service = AnalysisService(config)
            logger.info("Serwisy API zainicjalizowane pomyślnie")
        except Exception as e:
            logger.error(f"Błąd inicjalizacji serwisów API: {e}")
            raise
    
    @app.get("/", response_class=HTMLResponse)
    async def root():
        template_path = Path(__file__).parent / "templates" / "index.html"
        if template_path.exists():
            return template_path.read_text(encoding="utf-8")
        return """
        <html>
            <head><title>Indeks Branż API</title></head>
            <body>
                <h1>Indeks Branż API</h1>
                <p>Wersja 1.0.0</p>
                <ul>
                    <li><a href="/health">/health</a> - Sprawdzenie stanu</li>
                    <li><a href="/sectors">/sectors</a> - Lista sektorów</li>
                    <li><a href="/docs">/docs</a> - Dokumentacja Swagger</li>
                </ul>
            </body>
        </html>
        """
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "services": {
            "config": config is not None,
            "data_service": data_service is not None,
            "analysis_service": analysis_service is not None,
        }}
    
    @app.get("/sectors")
    async def get_sectors(
        limit: Optional[int] = Query(None, ge=1, le=100),
        category: Optional[str] = None,
    ):
        try:
            results_path = Path("data/output/indeks_branz.csv")
            if not results_path.exists():
                raise HTTPException(
                    status_code=404,
                    detail="Plik wyników nie znaleziony. Uruchom najpierw analizę."
                )
            
            df = pd.read_csv(results_path)
            df["pkd_code"] = df["pkd_code"].astype(str)
            
            if category:
                df = df[df["category"] == category]
            
            if limit:
                df = df.head(limit)
            
            return df.to_dict(orient="records")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Błąd pobierania sektorów: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/sector/{pkd_code}")
    async def get_sector(pkd_code: str):
        try:
            results_path = Path("data/output/indeks_branz.csv")
            if not results_path.exists():
                raise HTTPException(
                    status_code=404,
                    detail="Plik wyników nie znaleziony. Uruchom najpierw analizę."
                )
            
            df = pd.read_csv(results_path)
            df["pkd_code"] = df["pkd_code"].astype(str)
            sector = df[df["pkd_code"] == pkd_code]
            
            if sector.empty:
                raise HTTPException(
                    status_code=404,
                    detail=f"Sektor {pkd_code} nie znaleziony"
                )
            
            return sector.iloc[0].to_dict()
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Błąd pobierania sektora {pkd_code}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/rankings")
    async def get_rankings(
        top_n: Optional[int] = Query(10, ge=1, le=50),
        sort_by: Optional[str] = Query("final_index", regex="^(final_index|growth_score|risk_score)$"),
    ):
        try:
            results_path = Path("data/output/indeks_branz.csv")
            if not results_path.exists():
                raise HTTPException(
                    status_code=404,
                    detail="Plik wyników nie znaleziony. Uruchom najpierw analizę."
                )
            
            df = pd.read_csv(results_path)
            df["pkd_code"] = df["pkd_code"].astype(str)
            df = df.sort_values(sort_by, ascending=False).head(top_n)
            
            return df.to_dict(orient="records")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Błąd pobierania rankingu: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return app


app = create_app()

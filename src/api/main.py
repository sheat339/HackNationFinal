from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, Response, StreamingResponse
from typing import Optional, List
import pandas as pd
from pathlib import Path
import io
from datetime import timedelta

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
            
            if category and category.strip():
                logger.info(f"Filtrowanie po kategorii: '{category}'")
                df_filtered = df[df["category"].str.strip() == category.strip()]
                logger.info(f"Znaleziono {len(df_filtered)} sektorów w kategorii '{category}' z {len(df)} ogółem")
                df = df_filtered
            
            if limit:
                df = df.head(limit)
            
            logger.info(f"Zwracam {len(df)} sektorów")
            return df.to_dict(orient="records")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Błąd pobierania sektorów: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/sector/{pkd_code}")
    async def get_sector(pkd_code: str):
        try:
            from src.services.cache_service import CacheService
            
            cache_service = CacheService()
            cached = cache_service.get("sector", pkd_code)
            if cached:
                logger.info(f"Cache hit dla sektora {pkd_code}")
                return cached
            
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
            
            result = sector.iloc[0].to_dict()
            cache_service.set("sector", pkd_code, result)
            
            return result
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Błąd pobierania sektora {pkd_code}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/rankings")
    async def get_rankings(
        top_n: Optional[int] = Query(100, ge=1, le=200),
        sort_by: Optional[str] = Query("final_index", regex="^(final_index|growth_score|risk_score|profitability_score|size_score|debt_score)$"),
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
            
            if sort_by not in df.columns:
                sort_by = "final_index"
            
            df = df.sort_values(sort_by, ascending=False).head(top_n)
            
            return df.to_dict(orient="records")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Błąd pobierania rankingu: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/available-pkd")
    async def get_available_pkd():
        try:
            from src.services.cache_service import CacheService
            from src.data_collection.database_loader import DatabaseLoader
            
            cache_service = CacheService()
            cached = cache_service.get("available", "pkd")
            if cached:
                logger.info("Cache hit dla dostępnych PKD")
                return cached
            
            loader = DatabaseLoader()
            available_pkd = sorted(list(loader.get_available_pkd_codes()))
            
            results_path = Path("data/output/indeks_branz.csv")
            sectors = []
            
            if results_path.exists():
                df = pd.read_csv(results_path)
                df["pkd_code"] = df["pkd_code"].astype(str)
                sectors = df[['pkd_code', 'branch_name', 'category', 'final_index']].to_dict(orient="records")
                sectors = [s for s in sectors if s['pkd_code'] in available_pkd]
            
            if not sectors:
                from src.utils.pkd_mapping import get_pkd_division_name
                sectors = [
                    {
                        'pkd_code': pkd,
                        'branch_name': get_pkd_division_name(pkd),
                        'category': 'Brak danych',
                        'final_index': 0.0
                    }
                    for pkd in available_pkd
                ]
            
            result = {
                "pkd_codes": available_pkd,
                "sectors": sectors
            }
            
            cache_service.set("available", "pkd", result, ttl=timedelta(hours=1))
            
            return result
        except Exception as e:
            logger.error(f"Błąd pobierania dostępnych PKD: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/sector/{pkd_code}/history")
    async def get_sector_history(pkd_code: str):
        try:
            from src.data_collection.database_loader import DatabaseLoader
            from src.services.cache_service import CacheService
            
            cache_service = CacheService()
            cached = cache_service.get("history", pkd_code)
            if cached:
                logger.info(f"Cache hit dla historii sektora {pkd_code}")
                return cached
            
            loader = DatabaseLoader()
            df = loader.load_sector_data_from_database(pkd_code, years=None)
            
            if df is None or df.empty:
                logger.warning(f"Brak danych historycznych dla sektora {pkd_code}")
                raise HTTPException(
                    status_code=404,
                    detail=f"Brak danych historycznych dla sektora {pkd_code}"
                )
            
            df = df.sort_values('year')
            result = df.to_dict(orient="records")
            
            cache_service.set("history", pkd_code, result, ttl=timedelta(hours=6))
            
            logger.info(f"Zwracam {len(result)} rekordów historii dla PKD {pkd_code}, lata: {sorted(df['year'].unique().tolist())}")
            return result
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Błąd pobierania historii sektora {pkd_code}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/realtime/{pkd_code}")
    async def get_realtime_data(
        pkd_code: str,
        source: Optional[str] = Query("all", regex="^(all|gus)$")
    ):
        try:
            from src.services.realtime_service import RealtimeDataService
            
            service = RealtimeDataService()
            
            if source == "all":
                result = service.fetch_all_sources(pkd_code)
            elif source == "gus":
                result = service.fetch_gus_data(pkd_code)
            else:
                raise HTTPException(status_code=400, detail=f"Nieznane źródło: {source}")
            
            logger.info(f"Zwracam dane realtime dla PKD {pkd_code} ze źródła {source}")
            return result
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Błąd pobierania danych realtime dla sektora {pkd_code}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/bdl/subjects")
    async def get_bdl_subjects(
        parent_id: Optional[str] = None,
        search: Optional[str] = None
    ):
        """Get BDL subjects (topics)."""
        try:
            from src.services.realtime_service import RealtimeDataService
            service = RealtimeDataService()
            subjects = service.get_subjects(parent_id=parent_id, search=search)
            return {"subjects": subjects}
        except Exception as e:
            logger.error(f"Błąd pobierania tematów BDL: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/bdl/variables")
    async def get_bdl_variables(
        subject_id: Optional[str] = None,
        search: Optional[str] = None,
        years: Optional[str] = None
    ):
        """Get BDL variables."""
        try:
            from src.services.realtime_service import RealtimeDataService
            service = RealtimeDataService()
            
            year_list = None
            if years:
                year_list = [int(y.strip()) for y in years.split(",")]
            
            variables = service.get_variables(subject_id=subject_id, search=search, years=year_list)
            return {"variables": variables}
        except Exception as e:
            logger.error(f"Błąd pobierania zmiennych BDL: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/bdl/variables/{variable_id}")
    async def get_bdl_variable_details(variable_id: str):
        """Get BDL variable details."""
        try:
            from src.services.realtime_service import RealtimeDataService
            service = RealtimeDataService()
            variable = service.get_variable_details(variable_id)
            if variable is None:
                raise HTTPException(status_code=404, detail=f"Zmienna {variable_id} nie znaleziona")
            return variable
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Błąd pobierania szczegółów zmiennej BDL: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/bdl/data/variable/{variable_id}")
    async def get_bdl_data_by_variable(
        variable_id: str,
        unit_level: Optional[int] = Query(None, ge=0, le=7),
        unit_parent_id: Optional[str] = None,
        years: Optional[str] = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(100, ge=1, le=1000)
    ):
        """Get BDL data for a specific variable."""
        try:
            from src.services.realtime_service import RealtimeDataService
            service = RealtimeDataService()
            
            year_list = None
            if years:
                year_list = [int(y.strip()) for y in years.split(",")]
            
            data = service.get_data_by_variable(
                variable_id=variable_id,
                unit_level=unit_level,
                unit_parent_id=unit_parent_id,
                years=year_list,
                page=page,
                page_size=page_size
            )
            return data
        except Exception as e:
            logger.error(f"Błąd pobierania danych BDL dla zmiennej {variable_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/bdl/units")
    async def get_bdl_units(
        level: Optional[int] = Query(None, ge=0, le=7),
        parent_id: Optional[str] = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(100, ge=1, le=1000)
    ):
        """Get BDL territorial units."""
        try:
            from src.services.realtime_service import RealtimeDataService
            service = RealtimeDataService()
            units = service.get_units(level=level, parent_id=parent_id, page=page, page_size=page_size)
            return units
        except Exception as e:
            logger.error(f"Błąd pobierania jednostek BDL: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/realtime/quick")
    async def get_quick_statistics(
        source: Optional[str] = Query("gus"),
        unit_level: Optional[int] = Query(2, ge=0, le=7)
    ):
        """Get quick statistics from BDL."""
        try:
            from src.services.realtime_service import RealtimeDataService
            service = RealtimeDataService()
            stats = service.get_popular_statistics(unit_level=unit_level)
            return stats
        except Exception as e:
            logger.error(f"Błąd pobierania szybkich statystyk: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/sector/{pkd_code}/compare")
    async def compare_sectors(
        pkd_code: str,
        compare_with: str = Query(..., description="Kody PKD do porównania, oddzielone przecinkami")
    ):
        """Compare multiple sectors."""
        try:
            results_path = Path("data/output/indeks_branz.csv")
            if not results_path.exists():
                raise HTTPException(status_code=404, detail="Plik wyników nie znaleziony")
            
            df = pd.read_csv(results_path)
            df["pkd_code"] = df["pkd_code"].astype(str)
            
            pkd_codes = [pkd_code] + [p.strip() for p in compare_with.split(",")]
            sectors = df[df["pkd_code"].isin(pkd_codes)]
            
            if sectors.empty:
                raise HTTPException(status_code=404, detail="Sektory nie znalezione")
            
            return sectors.to_dict(orient="records")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Błąd porównywania sektorów: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/sector/{pkd_code}/predict")
    async def predict_sector(pkd_code: str):
        """Get prediction for next year."""
        try:
            from src.services.prediction_service import PredictionService
            from src.data_collection.database_loader import DatabaseLoader
            
            loader = DatabaseLoader()
            history_data = loader.load_sector_data_from_database(pkd_code, years=None)
            
            if history_data is None or history_data.empty:
                raise HTTPException(status_code=404, detail="Brak danych historycznych")
            
            results_path = Path("data/output/indeks_branz.csv")
            if results_path.exists():
                df = pd.read_csv(results_path)
                df["pkd_code"] = df["pkd_code"].astype(str)
                sector = df[df["pkd_code"] == pkd_code]
                if not sector.empty:
                    sector_dict = sector.iloc[0].to_dict()
                else:
                    sector_dict = {}
            else:
                sector_dict = {}
            
            prediction_service = PredictionService()
            prediction = prediction_service.predict_next_year(history_data.to_dict(orient="records"))
            trend = prediction_service.get_trend_indicator(history_data.to_dict(orient="records"))
            
            return {
                "pkd_code": pkd_code,
                "prediction": prediction,
                "trend_indicator": trend,
                "current_sector": sector_dict
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Błąd prognozowania sektora {pkd_code}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/sector/{pkd_code}/recommendations")
    async def get_recommendations(pkd_code: str, limit: int = Query(5, ge=1, le=10)):
        """Get recommended similar sectors."""
        try:
            from src.services.recommendation_service import RecommendationService
            
            results_path = Path("data/output/indeks_branz.csv")
            if not results_path.exists():
                raise HTTPException(status_code=404, detail="Plik wyników nie znaleziony")
            
            df = pd.read_csv(results_path)
            df["pkd_code"] = df["pkd_code"].astype(str)
            
            target_sector = df[df["pkd_code"] == pkd_code]
            if target_sector.empty:
                raise HTTPException(status_code=404, detail=f"Sektor {pkd_code} nie znaleziony")
            
            recommendation_service = RecommendationService()
            recommendations = recommendation_service.find_similar_sectors(
                target_sector.iloc[0].to_dict(),
                df.to_dict(orient="records"),
                top_n=limit
            )
            
            return {"recommendations": recommendations}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Błąd pobierania rekomendacji: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/sector/{pkd_code}/alerts")
    async def get_sector_alerts(pkd_code: str):
        """Get alerts for sector changes."""
        try:
            from src.services.alert_service import AlertService
            
            results_path = Path("data/output/indeks_branz.csv")
            if not results_path.exists():
                return {"alerts": []}
            
            df = pd.read_csv(results_path)
            df["pkd_code"] = df["pkd_code"].astype(str)
            
            current_sector = df[df["pkd_code"] == pkd_code]
            if current_sector.empty:
                return {"alerts": []}
            
            alert_service = AlertService()
            alerts = alert_service.check_all_alerts(
                current_sector.iloc[0].to_dict(),
                None
            )
            
            return {"alerts": alerts}
        except Exception as e:
            logger.error(f"Błąd pobierania alertów: {e}")
            return {"alerts": []}
    
    @app.get("/analytics/correlations")
    async def get_correlations():
        """Get correlations between metrics."""
        try:
            from src.services.analytics_service import AnalyticsService
            
            results_path = Path("data/output/indeks_branz.csv")
            if not results_path.exists():
                raise HTTPException(status_code=404, detail="Plik wyników nie znaleziony")
            
            df = pd.read_csv(results_path)
            analytics_service = AnalyticsService()
            correlations = analytics_service.calculate_correlations(df)
            statistics = analytics_service.calculate_statistics(df)
            
            return {
                "correlations": correlations,
                "statistics": statistics
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Błąd obliczania korelacji: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/dashboard")
    async def get_dashboard():
        """Get dashboard statistics."""
        try:
            results_path = Path("data/output/indeks_branz.csv")
            if not results_path.exists():
                raise HTTPException(status_code=404, detail="Plik wyników nie znaleziony")
            
            df = pd.read_csv(results_path)
            
            total_sectors = len(df)
            avg_index = df["final_index"].mean() if "final_index" in df.columns else 0
            
            category_dist = df["category"].value_counts().to_dict() if "category" in df.columns else {}
            
            top_5 = df.nlargest(5, "final_index")[["pkd_code", "branch_name", "final_index", "category"]].to_dict(orient="records")
            bottom_5 = df.nsmallest(5, "final_index")[["pkd_code", "branch_name", "final_index", "category"]].to_dict(orient="records")
            
            return {
                "total_sectors": total_sectors,
                "average_index": float(avg_index),
                "category_distribution": category_dist,
                "top_5": top_5,
                "bottom_5": bottom_5
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Błąd pobierania dashboardu: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/sector/{pkd_code}/export")
    async def export_sector(
        pkd_code: str,
        format: str = Query("csv", regex="^(csv|excel|pdf)$")
    ):
        """Export sector data."""
        try:
            from src.services.export_service import ExportService
            
            results_path = Path("data/output/indeks_branz.csv")
            if not results_path.exists():
                raise HTTPException(status_code=404, detail="Plik wyników nie znaleziony")
            
            df = pd.read_csv(results_path)
            df["pkd_code"] = df["pkd_code"].astype(str)
            
            sector = df[df["pkd_code"] == pkd_code]
            if sector.empty:
                raise HTTPException(status_code=404, detail=f"Sektor {pkd_code} nie znaleziony")
            
            export_service = ExportService(config, Path("data/output"))
            
            if format == "csv":
                csv_data = sector.to_csv(index=False, encoding='utf-8-sig')
                return Response(content=csv_data, media_type="text/csv", 
                              headers={"Content-Disposition": f"attachment; filename=sector_{pkd_code}.csv"})
            elif format == "excel":
                excel_path = export_service.export_to_excel(sector, filename=f"sector_{pkd_code}.xlsx")
                return Response(content=excel_path.read_bytes(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                              headers={"Content-Disposition": f"attachment; filename=sector_{pkd_code}.xlsx"})
            elif format == "pdf":
                pdf_data = export_service.export_to_pdf({"sector": sector.iloc[0].to_dict()}, f"sector_{pkd_code}.pdf")
                return Response(content=pdf_data, media_type="application/pdf",
                              headers={"Content-Disposition": f"attachment; filename=sector_{pkd_code}.pdf"})
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Błąd eksportowania sektora: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/sectors/search")
    async def search_sectors(
        query: Optional[str] = None,
        min_index: Optional[float] = None,
        max_index: Optional[float] = None,
        min_growth: Optional[float] = None,
        max_growth: Optional[float] = None,
        categories: Optional[str] = None,
        limit: int = Query(20, ge=1, le=100)
    ):
        """Advanced search for sectors."""
        try:
            results_path = Path("data/output/indeks_branz.csv")
            if not results_path.exists():
                raise HTTPException(status_code=404, detail="Plik wyników nie znaleziony")
            
            df = pd.read_csv(results_path)
            df["pkd_code"] = df["pkd_code"].astype(str)
            
            if query:
                mask = df["branch_name"].str.contains(query, case=False, na=False) | \
                       df["pkd_code"].str.contains(query, case=False, na=False)
                df = df[mask]
            
            if min_index is not None:
                df = df[df["final_index"] >= min_index]
            if max_index is not None:
                df = df[df["final_index"] <= max_index]
            if min_growth is not None:
                df = df[df["growth_score"] >= min_growth]
            if max_growth is not None:
                df = df[df["growth_score"] <= max_growth]
            if categories:
                category_list = [c.strip() for c in categories.split(",")]
                df = df[df["category"].isin(category_list)]
            
            df = df.head(limit)
            return df.to_dict(orient="records")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Błąd wyszukiwania sektorów: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/sector/{pkd_code}/history/compare")
    async def compare_history_periods(
        pkd_code: str,
        period1: str = Query(..., description="Okres 1: start_year-end_year"),
        period2: str = Query(..., description="Okres 2: start_year-end_year")
    ):
        """Compare two time periods."""
        try:
            from src.data_collection.database_loader import DatabaseLoader
            
            loader = DatabaseLoader()
            all_data = loader.load_sector_data_from_database(pkd_code, years=None)
            
            if all_data is None or all_data.empty:
                raise HTTPException(status_code=404, detail="Brak danych historycznych")
            
            def parse_period(period_str):
                start, end = period_str.split("-")
                return int(start), int(end)
            
            start1, end1 = parse_period(period1)
            start2, end2 = parse_period(period2)
            
            period1_data = all_data[(all_data["year"] >= start1) & (all_data["year"] <= end1)]
            period2_data = all_data[(all_data["year"] >= start2) & (all_data["year"] <= end2)]
            
            if period1_data.empty or period2_data.empty:
                raise HTTPException(status_code=404, detail="Brak danych dla wybranych okresów")
            
            numeric_cols = period1_data.select_dtypes(include=['number']).columns.tolist()
            period1_avg = period1_data[numeric_cols].mean().to_dict()
            period2_avg = period2_data[numeric_cols].mean().to_dict()
            
            changes = {}
            for key in period1_avg:
                if isinstance(period1_avg[key], (int, float)) and isinstance(period2_avg[key], (int, float)):
                    if period1_avg[key] != 0:
                        changes[key] = ((period2_avg[key] - period1_avg[key]) / period1_avg[key]) * 100
                    else:
                        changes[key] = 0
            
            return {
                "period1": {
                    "range": f"{start1}-{end1}",
                    "data": period1_avg
                },
                "period2": {
                    "range": f"{start2}-{end2}",
                    "data": period2_avg
                },
                "changes": changes
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Błąd porównywania okresów: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/integrations/economic-indicators")
    async def get_economic_indicators():
        """Get economic indicators from external sources."""
        try:
            from src.services.integration_service import IntegrationService
            
            service = IntegrationService()
            indicators = service.get_economic_indicators()
            return indicators
        except Exception as e:
            logger.error(f"Błąd pobierania wskaźników ekonomicznych: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return app


app = create_app()

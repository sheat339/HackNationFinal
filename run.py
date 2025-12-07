import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.config_loader import load_config
from src.utils.logger import setup_logger
from src.services.data_service import DataService
from src.services.analysis_service import AnalysisService
from src.services.export_service import ExportService
from src.visualization.charts import Visualizer
from src.utils.exceptions import IndeksBranzError

def run_analysis(logger):
    logger.info("=" * 60)
    logger.info("Indeks Branż - Analiza kondycji sektorów polskiej gospodarki")
    logger.info("=" * 60)
    
    logger.info("[1/7] Ładowanie konfiguracji...")
    config = load_config()
    logger.info("Konfiguracja załadowana pomyślnie")
    
    logger.info("[2/7] Przygotowywanie struktury katalogów...")
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    (data_dir / "raw").mkdir(exist_ok=True)
    (data_dir / "processed").mkdir(exist_ok=True)
    (data_dir / "output").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    Path("visualizations").mkdir(exist_ok=True)
    
    logger.info("[3/7] Wybór sektorów do analizy...")
    from src.data_collection.database_loader import DatabaseLoader
    loader = DatabaseLoader()
    available_pkd = loader.get_available_pkd_codes()
    
    if available_pkd:
        selected_pkd_codes = sorted(list(available_pkd))
        logger.info(f"Znaleziono {len(selected_pkd_codes)} sektorów w bazie danych: {selected_pkd_codes}")
    else:
        logger.warning("Nie znaleziono żadnych kodów PKD w bazie danych, używam domyślnych")
        selected_pkd_codes = [
            "10", "20", "25", "26", "28", "36", "46", "47", "49", "55", "61", "62", "64", "68", "86"
        ]
    logger.info(f"Wybrano {len(selected_pkd_codes)} sektorów do analizy")
    
    data_service = DataService(config)
    analysis_service = AnalysisService(config)
    export_service = ExportService(config, data_dir / "output")
    
    logger.info("[4/7] Zbieranie danych...")
    sector_data = data_service.collect_sector_data(selected_pkd_codes)
    
    logger.info("[5/7] Obliczanie wskaźników i indeksu...")
    indicators_df = analysis_service.calculate_indicators(sector_data)
    
    classified_df = analysis_service.classify_sectors(indicators_df)
    
    results_df = analysis_service.prepare_final_results(classified_df)
    
    top_10 = analysis_service.get_top_sectors(results_df, 10)
    growing = analysis_service.get_growing_sectors(results_df, 10)
    risky = analysis_service.get_risky_sectors(results_df, 10)
    
    logger.info("[6/7] Eksportowanie wyników...")
    export_paths = export_service.export_results(
        results_df,
        top_10_df=top_10,
        growing_df=growing,
        risky_df=risky
    )
    logger.info(f"Wyniki wyeksportowane do: {export_paths['csv']}, {export_paths['excel']}")
    
    logger.info("[7/7] Tworzenie wizualizacji...")
    visualizer = Visualizer(config)
    
    fig_ranking = visualizer.create_index_ranking(results_df, top_n=20)
    visualizer.save_figure(fig_ranking, 'ranking_indeksu', 'html')
    
    fig_growth = visualizer.create_growth_comparison(results_df, top_n=15)
    visualizer.save_figure(fig_growth, 'porownanie_wzrostu', 'html')
    
    fig_categories = visualizer.create_category_distribution(results_df)
    visualizer.save_figure(fig_categories, 'rozkład_kategorii', 'html')
    
    fig_corr = visualizer.create_correlation_heatmap(results_df)
    visualizer.save_figure(fig_corr, 'korelacja_wskaźników', 'html')
    
    for pkd_code in results_df.head(3)['pkd_code']:
        fig_radar = visualizer.create_radar_chart(results_df, pkd_code)
        visualizer.save_figure(fig_radar, f'radar_{pkd_code}', 'html')
    
    logger.info("=" * 60)
    logger.info("Analiza zakończona pomyślnie!")
    logger.info("=" * 60)
    
    return results_df, export_paths

def main():
    log_file = Path("logs") / "indeks_branz.log"
    logger = setup_logger(log_file=log_file)
    
    try:
        results_df, export_paths = run_analysis(logger)
        
        logger.info("=" * 60)
        logger.info("Uruchamianie serwera API...")
        logger.info("Serwer będzie dostępny pod adresem: http://localhost:8000")
        logger.info("Swagger UI: http://localhost:8000/docs")
        logger.info("Naciśnij CTRL+C aby zatrzymać serwer")
        logger.info("=" * 60)
        
        import uvicorn
        uvicorn.run(
            "src.api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        logger.info("\nZatrzymano przez użytkownika")
        sys.exit(0)
    except IndeksBranzError as e:
        logger.error(f"Błąd aplikacji: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Nieoczekiwany błąd: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


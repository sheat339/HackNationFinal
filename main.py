"""
Główny skrypt uruchomieniowy dla Indeksu Branż
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Dodaj ścieżkę src do PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.config_loader import load_config
from src.utils.pkd_mapping import get_all_divisions, get_pkd_division_name
from src.data_collection.data_collector import DataCollector
from src.analysis.indicators import IndicatorCalculator
from src.analysis.classifier import SectorClassifier
from src.visualization.charts import Visualizer

def main():
    """Główna funkcja uruchomieniowa"""
    print("=" * 60)
    print("Indeks Branż - Analiza kondycji sektorów polskiej gospodarki")
    print("=" * 60)
    
    # Ładowanie konfiguracji
    print("\n[1/6] Ładowanie konfiguracji...")
    config = load_config()
    
    # Przygotowanie katalogów
    print("\n[2/6] Przygotowanie struktury katalogów...")
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    (data_dir / "raw").mkdir(exist_ok=True)
    (data_dir / "processed").mkdir(exist_ok=True)
    (data_dir / "output").mkdir(exist_ok=True)
    
    # Wybór branż do analizy (przykładowe działy PKD)
    print("\n[3/6] Wybór branż do analizy...")
    all_divisions = get_all_divisions()
    
    # Wybieramy przykładowe branże do analizy
    selected_pkd_codes = [
        "10",  # Produkcja żywności
        "20",  # Produkcja chemikaliów
        "25",  # Produkcja wyrobów metalowych
        "26",  # Produkcja komputerów i elektroniki
        "28",  # Produkcja pojazdów samochodowych
        "36",  # Budownictwo
        "46",  # Handel hurtowy
        "47",  # Handel detaliczny
        "49",  # Transport lądowy
        "55",  # Zakwaterowanie
        "61",  # Telekomunikacja
        "62",  # Działalność związana z oprogramowaniem
        "64",  # Działalność usługowa w zakresie pośrednictwa finansowego
        "68",  # Obrót nieruchomościami
        "86"   # Opieka zdrowotna
    ]
    
    print(f"Wybrano {len(selected_pkd_codes)} branż do analizy")
    
    # Zbieranie danych
    print("\n[4/6] Zbieranie danych...")
    collector = DataCollector(config)
    sector_data = collector.collect_all_data(selected_pkd_codes)
    
    # Obliczanie wskaźników
    print("\n[5/6] Obliczanie wskaźników i indeksu...")
    calculator = IndicatorCalculator(config)
    indicators_df = calculator.calculate_all_indicators(sector_data)
    
    # Klasyfikacja branż
    classifier = SectorClassifier(config)
    indicators_df = classifier.classify_sectors(indicators_df)
    
    # Dodanie nazw branż
    indicators_df['branch_name'] = indicators_df['pkd_code'].apply(get_pkd_division_name)
    
    # Sortowanie według indeksu
    indicators_df = indicators_df.sort_values('final_index', ascending=False)
    
    # Dodanie rankingu
    indicators_df['rank'] = range(1, len(indicators_df) + 1)
    
    # Reorganizacja kolumn
    column_order = [
        'rank', 'pkd_code', 'branch_name', 'final_index', 'category',
        'size_score', 'growth_score', 'profitability_score', 'debt_score', 'risk_score',
        'revenue_growth_yoy', 'profit_growth_yoy', 'profit_margin',
        'debt_to_assets', 'bankruptcy_rate', 'num_companies'
    ]
    indicators_df = indicators_df[[col for col in column_order if col in indicators_df.columns]]
    
    # Zapis wyników
    print("\n[6/6] Zapis wyników...")
    
    # CSV
    csv_path = data_dir / "output" / "indeks_branz.csv"
    indicators_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"✓ Zapisano CSV: {csv_path}")
    
    # Excel
    excel_path = data_dir / "output" / "indeks_branz.xlsx"
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        indicators_df.to_excel(writer, sheet_name='Indeks Branż', index=False)
        
        # Dodatkowy arkusz z top 10
        top_10 = indicators_df.head(10)
        top_10.to_excel(writer, sheet_name='Top 10', index=False)
        
        # Arkusz z najszybciej rozwijającymi się
        growing = classifier.get_growing_sectors(indicators_df, 10)
        growing.to_excel(writer, sheet_name='Najszybciej rozwijające się', index=False)
        
        # Arkusz z najbardziej ryzykownymi
        risky = classifier.get_risky_sectors(indicators_df, 10)
        risky.to_excel(writer, sheet_name='Najbardziej ryzykowne', index=False)
    
    print(f"✓ Zapisano Excel: {excel_path}")
    
    # Tworzenie wizualizacji
    print("\n[7/7] Tworzenie wizualizacji...")
    visualizer = Visualizer(config)
    
    # Ranking
    fig_ranking = visualizer.create_index_ranking(indicators_df, top_n=20)
    visualizer.save_figure(fig_ranking, 'ranking_indeksu', 'html')
    
    # Porównanie wzrostu
    fig_growth = visualizer.create_growth_comparison(indicators_df, top_n=15)
    visualizer.save_figure(fig_growth, 'porownanie_wzrostu', 'html')
    
    # Rozkład kategorii
    fig_categories = visualizer.create_category_distribution(indicators_df)
    visualizer.save_figure(fig_categories, 'rozkład_kategorii', 'html')
    
    # Mapa korelacji
    fig_corr = visualizer.create_correlation_heatmap(indicators_df)
    visualizer.save_figure(fig_corr, 'korelacja_wskaźników', 'html')
    
    # Wykres radarowy dla top 3 branż
    for i, pkd_code in enumerate(indicators_df.head(3)['pkd_code']):
        fig_radar = visualizer.create_radar_chart(indicators_df, pkd_code)
        visualizer.save_figure(fig_radar, f'radar_{pkd_code}', 'html')
    
    # Podsumowanie
    print("\n" + "=" * 60)
    print("PODSUMOWANIE")
    print("=" * 60)
    print(f"\nPrzeanalizowano {len(indicators_df)} branż")
    print(f"\nTop 5 branż według indeksu:")
    for idx, row in indicators_df.head(5).iterrows():
        print(f"  {row['rank']}. {row['pkd_code']} - {row['branch_name'][:50]}")
        print(f"     Indeks: {row['final_index']:.3f} | Kategoria: {row['category']}")
    
    print(f"\n\nRozkład kategorii:")
    category_counts = indicators_df['category'].value_counts()
    for category, count in category_counts.items():
        print(f"  {category}: {count}")
    
    print(f"\n\nPliki wygenerowane:")
    print(f"  - {csv_path}")
    print(f"  - {excel_path}")
    print(f"  - Wizualizacje w folderze: visualizations/")
    
    print("\n" + "=" * 60)
    print("Zakończono pomyślnie!")
    print("=" * 60)

if __name__ == "__main__":
    main()


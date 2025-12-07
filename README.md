# Indeks Branż - Analiza Kondycji Sektorów Polskiej Gospodarki

## Opis projektu

Indeks Branż to kompleksowy system analizy kondycji i perspektyw rozwoju wybranych branż w Polsce. System wykorzystuje dane finansowe i informacje o upadłościach z bazy danych do obliczania wskaźników kondycji sektorów gospodarki. Projekt został stworzony dla analityków kredytowych, menedżerów ryzyka i ekonomistów do podejmowania decyzji dotyczących finansowania przedsiębiorstw.

## Główne funkcjonalności

### Analiza i obliczenia
- **Analiza sektorów gospodarki** na podstawie kodów PKD/NACE
- **Obliczanie wskaźników kondycji** (wielkość, rozwój, rentowność, zadłużenie, ryzyko)
- **Klasyfikacja sektorów** do 5 kategorii kondycji
- **Rankingi sektorów** według różnych kryteriów z zaawansowanymi filtrami
- **Porównywanie sektorów** - wizualizacja i tabele porównawcze
- **Analiza historyczna** - porównywanie okresów czasowych
- **Prognozy i trendy** - przewidywanie przyszłych wartości
- **Rekomendacje** - znajdowanie podobnych sektorów

### Interfejs webowy
- **Nowoczesny interfejs** z motywem jasnym/ciemnym
- **Dashboard** z interaktywnymi wykresami i statystykami
- **Wizualizacje** - wykresy trendów, porównawcze, radarowe
- **Zaawansowane wyszukiwanie** z filtrami
- **Ulubione sektory** - szybki dostęp do wybranych sektorów
- **Notatki** - dodawanie notatek do sektorów
- **Eksport danych** - CSV, Excel, PDF z profesjonalnym formatowaniem

### API i integracje
- **REST API** z pełną dokumentacją Swagger
- **Integracja z BDL GUS** - dane w czasie rzeczywistym
- **Cache** - optymalizacja wydajności
- **Analytics** - analiza korelacji między wskaźnikami

## Technologie

- **Python 3.8+** - język programowania
- **FastAPI** - framework do budowy REST API
- **Pandas & NumPy** - analiza i przetwarzanie danych
- **Plotly** - wizualizacje interaktywne
- **ReportLab** - generowanie PDF z obsługą polskich znaków
- **Uvicorn** - serwer ASGI
- **Pytest** - testy jednostkowe

## Struktura projektu

```
HackNation/
├── database/                  # Pliki danych źródłowych
│   ├── wsk_fin.csv           # Dane finansowe
│   ├── krz_pkd.csv           # Dane o upadłościach
│   └── mapowanie_pkd.xlsx    # Mapowanie kodów PKD
├── data/                     # Dane przetworzone
│   ├── raw/                  # Surowe dane
│   ├── processed/            # Przetworzone dane
│   └── output/               # Wyniki końcowe (CSV/XLSX/PDF)
├── cache/                    # Cache danych API
├── src/                      # Kod źródłowy
│   ├── api/                  # REST API
│   │   ├── main.py           # Główny plik API (24 endpoints)
│   │   └── templates/        # Szablony HTML
│   ├── analysis/             # Analiza i obliczanie wskaźników
│   │   ├── indicators.py     # Kalkulator wskaźników
│   │   └── classifier.py     # Klasyfikator sektorów
│   ├── data_collection/      # Zbieranie danych
│   │   ├── data_collector.py # Główny kolektor danych
│   │   ├── database_loader.py # Ładowanie z bazy
│   │   └── sample_data_generator.py # Generator przykładowych danych
│   ├── models/               # Modele danych
│   │   ├── config.py         # Modele konfiguracji
│   │   └── sector.py         # Modele sektorów
│   ├── services/             # Serwisy biznesowe
│   │   ├── data_service.py   # Serwis danych
│   │   ├── analysis_service.py # Serwis analizy
│   │   ├── export_service.py # Serwis eksportu (CSV/Excel/PDF)
│   │   ├── analytics_service.py # Analiza korelacji
│   │   ├── cache_service.py  # Zarządzanie cache
│   │   ├── prediction_service.py # Prognozy
│   │   ├── recommendation_service.py # Rekomendacje
│   │   ├── realtime_service.py # Dane w czasie rzeczywistym
│   │   ├── integration_service.py # Integracje zewnętrzne
│   │   └── alert_service.py  # System alertów
│   ├── utils/                # Narzędzia pomocnicze
│   │   ├── config_loader.py  # Ładowanie konfiguracji
│   │   ├── logger.py         # Logowanie
│   │   ├── exceptions.py     # Wyjątki
│   │   └── pkd_mapping.py    # Mapowanie kodów PKD
│   └── visualization/        # Wizualizacje
│       └── charts.py         # Generowanie wykresów
├── config/                   # Konfiguracja
│   └── config.yaml           # Plik konfiguracyjny
├── tests/                    # Testy jednostkowe
├── logs/                     # Logi aplikacji
├── visualizations/           # Wygenerowane wizualizacje
├── run.py                    # Główny skrypt uruchomieniowy
├── main.py                   # Skrypt analizy
└── requirements.txt          # Zależności Python
```

## Instalacja

1. Sklonuj repozytorium:
```bash
git clone <repository-url>
cd HackNation
```

2. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

3. Upewnij się, że pliki danych znajdują się w folderze `database/`:
   - `wsk_fin.csv` - dane finansowe
   - `krz_pkd.csv` - dane o upadłościach
   - `mapowanie_pkd.xlsx` - mapowanie kodów PKD

## Uruchomienie

### Pełny system (analiza + API)

Uruchomienie pełnego systemu z analizą danych i serwerem API:

```bash
python run.py
```

System automatycznie:
1. Wykona analizę wszystkich sektorów
2. Wygeneruje pliki wynikowe (CSV, Excel)
3. Utworzy wizualizacje
4. Uruchomi serwer API na porcie 8000

### Tylko analiza

```bash
python main.py --mode analysis
```

### Tylko API

```bash
python main.py --mode api
```

### API z niestandardowym portem

```bash
python main.py --mode api --port 8080
```

## Dostęp do systemu

Po uruchomieniu serwera API:

- **Interfejs webowy**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health

## Funkcjonalności interfejsu webowego

### Wyszukiwanie i przeglądanie
- **Wyszukiwanie sektora** - wyszukiwanie po kodzie PKD
- **Lista sektorów** - przeglądanie wszystkich sektorów
- **Zaawansowane wyszukiwanie** - filtry po kategorii, indeksie, wzroście
- **Rankingi** - rankingi z filtrami (kategoria, zakres indeksu, sortowanie)

### Analiza i porównywanie
- **Porównywanie sektorów** - porównanie do 3 sektorów jednocześnie z tabelami i wykresami
- **Porównanie okresów** - analiza zmian w czasie dla wybranego sektora
- **Prognoza i trendy** - przewidywanie przyszłych wartości
- **Rekomendacje** - znajdowanie podobnych sektorów

### Dashboard i statystyki
- **Dashboard** - interaktywne wykresy, statystyki, top/bottom sektory
- **Analiza korelacji** - korelacje między wskaźnikami
- **Historia zmian** - wykresy zmian przychodów w czasie

### Narzędzia
- **Ulubione sektory** - szybki dostęp do wybranych sektorów
- **Notatki** - dodawanie notatek do sektorów
- **Eksport danych** - CSV, Excel, PDF z profesjonalnym formatowaniem

### Dane w czasie rzeczywistym
- **BDL GUS** - integracja z Bankiem Danych Lokalnych
- **Dane realtime** - aktualne dane z zewnętrznych źródeł

## Endpointy API

### Podstawowe

#### GET `/`
Główna strona z interfejsem webowym.

#### GET `/health`
Sprawdzenie stanu serwera i serwisów.

#### GET `/sectors`
Lista wszystkich sektorów.

**Parametry:**
- `limit` (opcjonalny): Maksymalna liczba wyników (1-100)
- `category` (opcjonalny): Filtrowanie po kategorii kondycji

**Przykład:**
```
GET /sectors?limit=10&category=Dobra kondycja
```

#### GET `/sector/{pkd_code}`
Szczegóły pojedynczego sektora.

**Przykład:**
```
GET /sector/62
```

#### GET `/sector/{pkd_code}/history`
Dane historyczne sektora do wykresów.

**Przykład:**
```
GET /sector/62/history
```

### Rankingi

#### GET `/rankings`
Ranking sektorów z zaawansowanymi opcjami.

**Parametry:**
- `top_n` (opcjonalny, domyślnie 100): Liczba sektorów w rankingu (1-200)
- `sort_by` (opcjonalny, domyślnie "final_index"): Kryterium sortowania
  - `final_index` - Indeks końcowy
  - `growth_score` - Wzrost
  - `risk_score` - Ryzyko
  - `profitability_score` - Rentowność
  - `size_score` - Wielkość
  - `debt_score` - Zadłużenie

**Przykład:**
```
GET /rankings?top_n=20&sort_by=growth_score
```

#### GET `/available-pkd`
Lista dostępnych kodów PKD z podstawowymi informacjami.

### Porównywanie i analiza

#### GET `/sector/{pkd_code}/compare`
Porównanie wielu sektorów.

**Parametry:**
- `compare_with` (wymagany): Kody PKD do porównania, oddzielone przecinkami

**Przykład:**
```
GET /sector/62/compare?compare_with=64,68
```

#### GET `/sector/{pkd_code}/history/compare`
Porównanie dwóch okresów czasowych dla sektora.

**Parametry:**
- `period1` (wymagany): Okres 1 w formacie `start_year-end_year`
- `period2` (wymagany): Okres 2 w formacie `start_year-end_year`

**Przykład:**
```
GET /sector/62/history/compare?period1=2020-2022&period2=2022-2024
```

### Prognozy i rekomendacje

#### GET `/sector/{pkd_code}/predict`
Prognoza dla sektora na następny rok.

**Przykład:**
```
GET /sector/62/predict
```

#### GET `/sector/{pkd_code}/recommendations`
Rekomendacje podobnych sektorów.

**Parametry:**
- `limit` (opcjonalny, domyślnie 5): Liczba rekomendacji

**Przykład:**
```
GET /sector/62/recommendations?limit=10
```

### Wyszukiwanie

#### GET `/sectors/search`
Zaawansowane wyszukiwanie sektorów.

**Parametry:**
- `query` (opcjonalny): Wyszukiwanie po nazwie lub kodzie PKD
- `min_index` (opcjonalny): Minimalny indeks
- `max_index` (opcjonalny): Maksymalny indeks
- `min_growth` (opcjonalny): Minimalny wzrost
- `max_growth` (opcjonalny): Maksymalny wzrost
- `categories` (opcjonalny): Kategorie oddzielone przecinkami
- `limit` (opcjonalny, domyślnie 20): Maksymalna liczba wyników (1-100)

**Przykład:**
```
GET /sectors/search?query=IT&min_index=0.6&categories=Dobra kondycja,Bardzo dobra kondycja
```

### Analytics

#### GET `/dashboard`
Statystyki dashboardu - top/bottom sektory, rozkład kategorii, średnie.

#### GET `/analytics/correlations`
Analiza korelacji między wskaźnikami a indeksem końcowym.

### Dane w czasie rzeczywistym

#### GET `/realtime/{pkd_code}`
Dane w czasie rzeczywistym z zewnętrznych źródeł.

**Parametry:**
- `source` (opcjonalny, domyślnie "all"): Źródło danych (all, gus)

**Przykład:**
```
GET /realtime/62?source=gus
```

#### GET `/bdl/subjects`
Lista tematów z BDL GUS.

**Parametry:**
- `parent_id` (opcjonalny): ID rodzica
- `search` (opcjonalny): Wyszukiwanie

#### GET `/bdl/variables`
Lista zmiennych z BDL GUS.

**Parametry:**
- `subject_id` (opcjonalny): ID tematu
- `search` (opcjonalny): Wyszukiwanie
- `years` (opcjonalny): Lata oddzielone przecinkami

#### GET `/bdl/variables/{variable_id}`
Szczegóły zmiennej z BDL.

#### GET `/bdl/data/variable/{variable_id}`
Dane dla zmiennej z BDL.

**Parametry:**
- `years` (opcjonalny): Lata oddzielone przecinkami

#### GET `/bdl/units`
Jednostki terytorialne z BDL.

#### GET `/realtime/quick`
Szybkie statystyki z BDL.

**Parametry:**
- `source` (opcjonalny, domyślnie "gus"): Źródło danych
- `unit_level` (opcjonalny, domyślnie 2): Poziom jednostki (0-7)

### Eksport

#### GET `/sector/{pkd_code}/export`
Eksport danych sektora.

**Parametry:**
- `format` (opcjonalny, domyślnie "csv"): Format eksportu (csv, excel, pdf)

**Przykład:**
```
GET /sector/62/export?format=pdf
```

### Integracje

#### GET `/integrations/economic-indicators`
Wskaźniki ekonomiczne z zewnętrznych źródeł.

**Parametry:**
- `indicator` (opcjonalny): Nazwa wskaźnika
- `years` (opcjonalny): Lata oddzielone przecinkami

## Metodologia obliczeń

### Definicja branży
Branże definiowane są na poziomie **działu PKD/NACE** (np. 46 - Handel hurtowy).

### Formuły obliczeń

#### 1. Indeks Końcowy (Final Index)
Wzór ważony składający się z 5 komponentów:

```
Final Index = (Size × 0.20) + (Growth × 0.25) + (Profitability × 0.20) + (Debt × 0.15) + (Risk × 0.20)
```

#### 2. Wielkość (Size Score) - 20%
Ocena wielkości branży na podstawie trzech metryk:

```
size_metric = (revenue / 10,000,000 + assets / 20,000,000 + num_companies / 10,000) / 3
size_score = min(1.0, max(0.0, size_metric))
```

- **Przychody**: normalizacja przez 10M zł
- **Aktywa**: normalizacja przez 20M zł
- **Liczba firm**: normalizacja przez 10K firm
- **Wynik**: średnia z trzech metryk, ograniczona do [0, 1]

#### 3. Rozwój (Growth Score) - 25%
Ocena dynamiki rozwoju branży:

```
revenue_growth = (revenue_current - revenue_previous) / revenue_previous
profit_growth = (profit_current - profit_previous) / profit_previous
assets_growth = (assets_current - assets_previous) / assets_previous

avg_growth = (revenue_growth + profit_growth + assets_growth) / 3
growth_score = min(1.0, max(0.0, (avg_growth + 0.1) / 0.3))
```

- **YoY Growth**: wzrost rok do roku dla przychodów, zysku i aktywów
- **Normalizacja**: (średni_wzrost + 0.1) / 0.3 → [0, 1]
- Wzrost 20% = score 1.0, wzrost -10% = score 0.0

#### 4. Rentowność (Profitability Score) - 20%
Ocena rentowności branży:

```
profit_margin = profit / revenue
profitability_score = min(1.0, max(0.0, profit_margin × 10))
```

- **Marża zysku**: zysk / przychody
- **Normalizacja**: marża × 10 → [0, 1]
- Marża 10% = score 1.0, marża 0% = score 0.0

#### 5. Zadłużenie (Debt Score) - 15%
Ocena poziomu zadłużenia (odwrotna - mniej długu = lepiej):

```
debt_to_assets = debt / assets
debt_score = max(0.0, min(1.0, 1 - debt_to_assets))
```

- **Dług do aktywów**: dług / aktywa
- **Normalizacja**: 1 - debt_to_assets → [0, 1]
- Dług 0% = score 1.0, dług 100% = score 0.0

#### 6. Ryzyko (Risk Score) - 20%
Ocena ryzyka branży (odwrotna - mniej bankructw = lepiej):

```
bankruptcy_rate = bankruptcies / num_companies
risk_score = max(0.0, min(1.0, 1 - bankruptcy_rate × 10))
```

- **Wskaźnik upadłości**: upadłości / liczba firm
- **Normalizacja**: 1 - (rate × 10) → [0, 1]
- Upadłości 0% = score 1.0, upadłości 10% = score 0.0

### Dodatkowe metryki

#### YoY Growth (Year-over-Year)
```
yoy_growth = (value_current_year - value_previous_year) / value_previous_year
```

#### Profit Margin
```
profit_margin = profit / revenue
```

#### Debt to Assets Ratio
```
debt_to_assets = debt / assets
```

#### Bankruptcy Rate
```
bankruptcy_rate = bankruptcies / num_companies
```

### Klasyfikacja sektorów

Sektory klasyfikowane są do 5 kategorii na podstawie finalnego indeksu:

- **Bardzo dobra kondycja**: indeks ≥ 0.75
- **Dobra kondycja**: indeks ≥ 0.60
- **Średnia kondycja**: indeks ≥ 0.45
- **Słaba kondycja**: indeks ≥ 0.30
- **Bardzo słaba kondycja**: indeks < 0.30

## Interfejs webowy - szczegóły

### Dashboard
- **Statystyki ogólne**: łączna liczba sektorów, średni indeks, top sektory
- **Top 5 sektorów**: najlepsze sektory z wizualnym wyróżnieniem
- **Bottom 5 sektorów**: najgorsze sektory
- **Rozkład kategorii**: interaktywna wykres kołowy

### Porównywanie sektorów
- **Tabela porównawcza**: wszystkie metryki obok siebie z kolorowym wyróżnieniem najlepszych/worst wartości
- **Wykresy porównawcze**: wykresy słupkowe dla kluczowych metryk
- **Szczegóły sektorów**: pełne karty sektorów z wszystkimi danymi

### Rankingi z filtrami
- **Filtry**: kategoria, zakres indeksu (min/max)
- **Sortowanie**: po dowolnym wskaźniku
- **Liczba wyników**: od 1 do 50

### Eksport PDF
- **Profesjonalne formatowanie**: gradienty, kolorowe tabele, wyróżnienia
- **Obsługa polskich znaków**: pełna obsługa Unicode
- **Struktura**: nagłówek, metryki, dodatkowe wskaźniki, stopka z datą

## Źródła danych

System wykorzystuje dane z plików w folderze `database/`:

- **wsk_fin.csv** - dane finansowe przedsiębiorstw według kodów PKD
- **krz_pkd.csv** - dane o upadłościach według kodów PKD
- **mapowanie_pkd.xlsx** - mapowanie kodów PKD do nazw branż

Dodatkowo system integruje się z:
- **BDL GUS** - Bank Danych Lokalnych Głównego Urzędu Statystycznego

## Wyniki

Projekt generuje następujące pliki:

- `data/output/indeks_branz.csv` - plik CSV z indeksem i wskaźnikami
- `data/output/indeks_branz.xlsx` - plik Excel z indeksem i arkuszami rankingów
- `visualizations/*.html` - interaktywne wizualizacje w formacie HTML
- Eksportowane PDF - profesjonalnie sformatowane raporty sektorów

## Testy

Uruchomienie testów jednostkowych:

```bash
pytest
```

Z raportem pokrycia kodu:

```bash
pytest --cov=src
```

## Konfiguracja

Konfiguracja znajduje się w pliku `config/config.yaml`. Można zmienić:

- **Wagi komponentów indeksu**: size, growth, profitability, debt, risk
- **Okres analizy**: start_year, end_year
- **Kategorie klasyfikacji**: progi dla każdej kategorii
- **Ustawienia wizualizacji**: format, motyw, rozmiary

### Przykładowa konfiguracja wag:

```yaml
weights:
  size: 0.20          # Wielkość branży
  growth: 0.25        # Rozwój branży
  profitability: 0.20 # Rentowność
  debt: 0.15          # Zadłużenie
  risk: 0.20          # Ryzyko
```

## Logi

Logi aplikacji zapisywane są w folderze `logs/indeks_branz.log`.

## Cache

System wykorzystuje cache do optymalizacji wydajności:
- Cache sektorów: 1 godzina
- Cache historii: 6 godzin
- Cache dostępnych PKD: 1 godzina

## Bezpieczeństwo i wydajność

- **Walidacja danych**: sprawdzanie poprawności danych wejściowych
- **Obsługa błędów**: szczegółowe komunikaty błędów
- **Cache**: optymalizacja zapytań do bazy danych
- **Async API**: asynchroniczne przetwarzanie żądań

## Rozwój i rozszerzenia

### Możliwe rozszerzenia:
- Integracja z dodatkowymi źródłami danych
- Zaawansowane modele predykcyjne (ML)
- Eksport do innych formatów
- Powiadomienia o zmianach
- API dla aplikacji mobilnych

## Autorzy

Zespół HackNation

## Licencja

Projekt stworzony w ramach wyzwania HackNation.

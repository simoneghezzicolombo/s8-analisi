# Riproducibilità dei grafici pubblicati

Questa pagina serve a distinguere tre cose diverse: il dataset finale usato nel grafico, lo script che lo visualizza, e la fonte primaria da cui arriva il dato. La pagina interattiva legge i CSV finali in `data/processed`; gli script in `scripts/reproducibility` servono invece a ricostruire o controllare i passaggi più delicati.

## Mappa grafico per grafico

| # | Grafico | Dataset usato dalla pagina | Script utile | Fonti dirette | Stato | Cosa manca per ricostruire da zero |
|---:|---|---|---|---|---|---|
| 1 | Evoluzione delle linee suburbane Trenord | `data/processed/linee_s_indice_2019_2025.csv` | `scripts/static_charts/genera_grafici_fedeli_canva.py` per il PNG finale | Trenord 2025, Trenord 2024, Regione Lombardia linee SFR | Riproducibile dal CSV finale | Manca uno script unico che ricostruisca l'intera serie 2019-2025 partendo solo dai comunicati/portali raw. |
| 2 | Variazione assoluta 2025-2024 | `data/processed/variazione_linee_suburbane_2024_2025.csv` e `data/processed/variazione_linee_suburbane_2024_2025_dettaglio.csv` | `scripts/reproducibility/linee_meratese/02_variazione_linee_suburbane_2024_2025.py` | Regione Lombardia linee SFR | Completo | Nulla di sostanziale: il metodo confronta solo le campagne presenti in entrambi gli anni; per questo S7 risulta in calo. |
| 3 | Passeggeri annui per linea, Top 20 | `data/processed/top20_linee_locali_italia.csv` | `scripts/reproducibility/top20/calculate_lombardia_annualization.py`, `scripts/reproducibility/top20/check_reproducibility.py` | `data/reproducibility/top20/sources_by_line.csv`, `DATA_SOURCES.md`, `TRENORD_L25_CALCULATION.md` | Completo per le linee Lombardia/Trenord/TILO 2025; parziale per alcune linee fuori Lombardia | Per alcune linee nazionali non esiste nel repo un raw ufficiale linea-per-linea comparabile: il valore finale e la fonte sono documentati, ma non sempre automatizzati. |
| 4 | S8 e metropolitane italiane | `data/processed/benchmark_metropolitane_s8.csv` | `assets/app.js` per interattivo; `scripts/static_charts/genera_grafici_fedeli_canva.py` per il PNG finale | Le colonne `fonte_passeggeri` e `fonte_frequenza` del CSV portano alla fonte riga per riga | Curato e verificabile | Manca uno script di scraping: il benchmark è un dataset ragionato, con fonte esplicita per ogni metropolitana. |
| 5 | Passeggeri nelle stazioni S8, 2015-2025 | `data/processed/stazioni_s8_indice_2015_2025.csv` | `scripts/static_charts/genera_grafici_fedeli_canva.py` per il PNG finale | Regione Lombardia Flussi stazioni 2015-2023; Regione Lombardia frequentazione stazioni 2024-2025 | Riproducibile dal CSV finale | Manca uno script separato, pulito, che ricostruisca esattamente questo CSV dai due raw regionali. |
| 6 | Crescita passeggeri nelle stazioni lombarde | `data/processed/scatter_stazioni_lombarde_2019_2025.csv` | `scripts/reproducibility/scatter/make_scatter_intensificazione_carico.py` | Regione Lombardia Flussi stazioni; Regione Lombardia frequentazione stazioni | Quasi completo | Lo script ricostruisce il dataset scatter; la resa grafica finale della presentazione resta nello script Canva statico. |
| 7 | Peso della punta mattutina nelle stazioni S8 | `data/processed/peso_punta_stazioni_s8_2015_2025.csv` | `scripts/static_charts/genera_grafici_fedeli_canva.py` per il PNG finale | Regione Lombardia Flussi stazioni; Regione Lombardia frequentazione stazioni | Riproducibile dal CSV finale | Manca uno script separato che ricostruisca la serie percentuale `Saliti7-9 / Saliti24H` dai raw regionali. |
| 8 | Crescita in punta e fuori punta | `data/processed/crescita_meratese_punta_morbida_2015_2025.csv` e `data/processed/punta_morbida_meratese_2019_2025.csv` | `scripts/reproducibility/linee_meratese/01_punta_morbida_meratese.py` | Regione Lombardia Flussi stazioni; Regione Lombardia frequentazione stazioni | Completo per il confronto 2019-2025 | Per la serie storica completa 2015-2025 resta pubblicato il CSV finale; il controllo automatico completo riguarda soprattutto il confronto 2019-2025. |

## File di fonti rapide

- `data/source_links_by_chart.csv` contiene i link diretti alle fonti per ogni grafico.
- `data/sources_intervento_iniziale.csv` raccoglie i link citati nel documento iniziale dell'intervento.
- `data/reproducibility/top20/sources_by_line.csv` documenta le fonti riga per riga della classifica ferroviaria.
- `data/reproducibility/top20/estimation_log.csv` spiega quali valori della Top 20 sono dati diretti, quali sono stime e quali sono calcoli da raw Lombardia 2025.

## Cosa ho lasciato fuori

Negli zip c'erano anche prove grafiche, mappe e script laterali usati durante il lavoro. Nel repo pubblico ho tenuto solo i materiali utili a difendere i grafici presenti nella presentazione e nella pagina interattiva. La mappa sperimentale sulle stazioni, per esempio, non è inclusa tra gli script principali perché non è uno dei grafici esposti.

# Struttura dei dati

## Cartelle

- `figures`: grafici PNG usati nella presentazione.
- `data/processed`: dataset puliti o aggregati collegati ai grafici.
- `data/raw`: dati grezzi principali scaricati o usati come base.
- `docs`: note metodologiche, reference e fonti sintetiche.
- `presentation`: PDF della presentazione.

## Manifest

Il file `data/manifest.csv` collega ogni slide a:

- titolo del grafico;
- immagine PNG;
- dataset CSV;
- nota fonte sintetica.

## Dataset processati

### `linee_s_indice_2019_2025.csv`

Serie temporale 2019-2025 per S8, S1/S12, S5, S6 e totale Trenord.

Campi principali:

- `Anno`
- `Serie`
- `Valore`
- `Unita`
- `Tipo_dato`
- `Indice_2019_100`

### `variazione_linee_suburbane_2024_2025.csv`

Confronto 2025 vs 2024 per linee suburbane.

Campi principali:

- `N. linea`
- `2024`
- `2025`
- `Delta`
- `Delta_pct`

### `top20_linee_locali_italia.csv`

Dataset usato per la classifica delle linee ferroviarie locali piu' usate.

Campi principali:

- `rank`
- `line_code`
- `line_name`
- `central_mln`
- `data_year`
- `method`
- `primary_source`
- `secondary_source`

### `benchmark_metropolitane_s8.csv`

Confronto tra S8 e alcune linee metropolitane.

Campi principali:

- `servizio`
- `tipo`
- `passeggeri_annui`
- `passeggeri_annui_label`
- `freq_punta`
- `freq_ordinaria`
- `fonte_pass_desc`
- `fonte_pass_url`
- `fonte_freq_desc`
- `fonte_freq_url`

### `stazioni_s8_indice_2015_2025.csv`

Serie stazioni S8 con indice 2019=100.

Campi principali:

- `Anno`
- `Stazione_std`
- `Stazione`
- `Saliti24H`
- `Indice_2019_100`
- `Fonte_periodo`

### `scatter_stazioni_lombarde_2019_2025.csv`

Dataset filtrato per confronto Lombardia 2019-2025.

Campi principali:

- `StationKey`
- `Saliti24H_2019`
- `Saliti24H_2025`
- `Corse24H_2019`
- `Corse24H_2025`
- `Growth_pct_Saliti24H`
- `Growth_pct_Saliti_per_corsa`
- `Delta_abs_Saliti24H`
- `IsMeratese`

### `peso_punta_stazioni_s8_2015_2025.csv`

Serie storica del peso della punta 7-9.

Campi principali:

- `Anno`
- `Stazione`
- `Peso_punta_pct`

### `crescita_meratese_punta_morbida_2015_2025.csv`

Serie usata per scomporre la crescita tra punta e fuori punta.

Campi principali:

- `Anno`
- `Stazione`
- `Saliti7-9`
- `Saliti24H`


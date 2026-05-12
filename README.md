# S8 Milano-Lecco: dati e grafici

Repository pubblico di supporto alla presentazione sulla linea S8 Lecco-Carnate-Milano e sulle stazioni del Meratese.

Pagina navigabile, se GitHub Pages e' attivo:

https://simoneghezzicolombo.github.io/s8-analisi/

Il repository raccoglie:

- i grafici finali usati nella presentazione;
- i dataset CSV collegati a ciascun grafico;
- i principali dati grezzi di partenza da Regione Lombardia;
- gli script di analisi e visualizzazione usati per costruire grafici e pagina interattiva;
- una mappa extra dei bacini potenziali delle fermate S8 tra Arcore e Lecco;
- note metodologiche e reference sintetiche per verificare i numeri.

## Come usare il repository

Per chi deve controllare rapidamente un dato:

1. aprire `data/manifest.csv`;
2. individuare la slide o il grafico;
3. aprire il CSV collegato nella colonna `dataset`;
4. confrontarlo con il PNG nella colonna `figure`.

Per una lettura piu' discorsiva, partire da:

- [docs/reference_dati_presentazione_S8.md](docs/reference_dati_presentazione_S8.md)
- [docs/metodologia.md](docs/metodologia.md)
- [presentation/comparazione_s8_a_varie_linee_italiane.pdf](presentation/comparazione_s8_a_varie_linee_italiane.pdf)
- [scripts/README.md](scripts/README.md)

## Grafici e dataset

| Slide | Grafico | PNG | Dataset |
|---:|---|---|---|
| 4 | Evoluzione linee S, indice 2019=100 | [PNG](figures/01_linee_suburbane_indice_2019_100.png) | [CSV](data/processed/linee_s_indice_2019_2025.csv) |
| 5 | Variazione assoluta passeggeri linee suburbane | [PNG](figures/02_variazione_assoluta_linee_suburbane.png) | [CSV](data/processed/variazione_linee_suburbane_2024_2025.csv) |
| 6 | Top 20 linee ferroviarie locali in Italia | [PNG](figures/04_top20_linee_locali_italia.png) | [CSV](data/processed/top20_linee_locali_italia.csv) |
| 7 | Confronto S8 con alcune metropolitane | [PNG](figures/03_comparazione_metro_s8.png) | [CSV](data/processed/benchmark_metropolitane_s8.csv) |
| 8 | Passeggeri nelle stazioni S8, 2015-2025 | [PNG](figures/05_stazioni_s8_indice_2019_100.png) | [CSV](data/processed/stazioni_s8_indice_2015_2025.csv) |
| 9 | Crescita stazioni lombarde e carico per corsa | [PNG](figures/06_saliti_per_corsa_stazioni_s8.png) | [CSV](data/processed/scatter_stazioni_lombarde_2019_2025.csv) |
| 10 | Peso della punta nelle stazioni S8 | [PNG](figures/07_peso_punta_stazioni_s8.png) | [CSV](data/processed/peso_punta_stazioni_s8_2015_2025.csv) |
| 11 | Crescita meratese: punta e morbida | [PNG](figures/08_crescita_punta_morbida_meratese.png) | [CSV](data/processed/crescita_meratese_punta_morbida_2015_2025.csv) |
| Extra | Bacini potenziali delle fermate S8 | [HTML](maps/mappa_isochrone_s8.html) | [Fonti](data/reproducibility/isochrone_s8/sources.csv) |

## Numeri principali

- La S8 passa da 32.484 utenti/giorno feriale nel 2019 a 51.240 nel 2025: indice 157,7, cioe' +57,7% rispetto al 2019.
- Nel confronto 2025 vs 2024 tra linee suburbane, la S8 registra +22.800 nell'indicatore di confronto delle campagne feriali.
- La S8 e' stimata a 14,8 milioni di passeggeri annui: 4o posto tra le linee ferroviarie locali non AV considerate.
- Le quattro stazioni meratesi passano da 4.620 saliti24H nel 2019 a 8.980 nel 2025: +4.360, cioe' +94,4%.
- Nel dataset filtrato di 148 stazioni lombarde con almeno 700 saliti24H nel 2019, Airuno e Osnago sono rispettivamente 1a e 2a per crescita percentuale 2019-2025.
- Nel Meratese, l'87,6% della crescita 2019-2025 e' fuori dalla fascia 7-9.

## Dati grezzi

I principali file grezzi sono in [data/raw](data/raw):

- `regione_lombardia_frequentazione_linee_sfr_20260424.csv`
- `regione_lombardia_flussi_stazioni_2015_2023_20260424.csv`
- `regione_lombardia_frequentazione_stazioni_sfr_20260424.csv`

I CSV in [data/processed](data/processed) sono invece dataset gia' puliti o aggregati per i grafici.

## Script

Gli script del progetto sono in [scripts](scripts). La pagina interattiva usa direttamente [assets/app.js](assets/app.js), mentre i grafici statici e le prove grafiche sono conservati nella cartella `scripts` per rendere tracciabile il lavoro di elaborazione e visualizzazione.

## Fonti

Le fonti principali sono:

- Regione Lombardia, dati di frequentazione delle linee del servizio ferroviario regionale;
- Regione Lombardia, flussi delle stazioni ferroviarie;
- Regione Lombardia, frequentazione delle stazioni del servizio ferroviario regionale;
- comunicati, relazioni e dati Trenord;
- per i confronti nazionali e metropolitani: fonti indicate nei dataset dedicati.

Per dettagli su definizioni, filtri e confronti, vedere [docs/metodologia.md](docs/metodologia.md).

## Riutilizzo e citazione

Quando si riutilizzano grafici o tabelle:

> Analisi di Simone Ghezzi Colombo su dati Regione Lombardia, Trenord e fonti indicate nei dataset.

I dati di origine mantengono licenze e condizioni delle rispettive fonti pubbliche. Le elaborazioni, i grafici e la documentazione sono pensati per favorire verifica, discussione pubblica e riuso istituzionale con citazione della fonte.

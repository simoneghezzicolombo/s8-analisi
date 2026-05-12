# Script di analisi e visualizzazione

Questa cartella raccoglie gli script usati per costruire i grafici e la pagina dati del progetto S8 Milano-Lecco.

## Script principali

- [`../assets/app.js`](../assets/app.js): genera i grafici interattivi della pagina GitHub Pages a partire dai CSV in `data/processed`.
- [`static_charts/genera_grafici_fedeli_canva.py`](static_charts/genera_grafici_fedeli_canva.py): script principale per generare i PNG statici 16:9 usati nella presentazione/Canva.

## Script di riproducibilita'

- [`reproducibility/core/build_all.py`](reproducibility/core/build_all.py): ricostruisce i CSV pubblicati per linee suburbane, stazioni S8, peso punta, punta/morbida e scatter Lombardia dai raw regionali/locali. Il controllo `reproducibility/core/validate_against_processed.py` verifica che i CSV rigenerati corrispondano a quelli pubblicati in `data/processed`.
- [`reproducibility/top20`](reproducibility/top20): calcolo della classifica Top 20 e controllo dell'annualizzazione Lombardia/Trenord 2025, inclusa la S8 a 14,8063 mln.
- [`reproducibility/source_audit`](reproducibility/source_audit): audit automatico delle fonti web/PDF per Top 20 nazionale e benchmark metropolitane; verifica link, download, ancoraggi numerici e gap rimasti.
- [`reproducibility/scatter/make_scatter_intensificazione_carico.py`](reproducibility/scatter/make_scatter_intensificazione_carico.py): costruzione dello scatter stazioni lombarde 2019-2025 dal raw Regione Lombardia.
- [`reproducibility/linee_meratese/02_variazione_linee_suburbane_2024_2025.py`](reproducibility/linee_meratese/02_variazione_linee_suburbane_2024_2025.py): variazione assoluta 2025-2024 delle linee suburbane con confronto solo tra campagne disponibili in entrambi gli anni.
- [`reproducibility/linee_meratese/01_punta_morbida_meratese.py`](reproducibility/linee_meratese/01_punta_morbida_meratese.py): scomposizione della crescita meratese tra punta 7-9 e resto della giornata.

## Script di lavoro

- [`prototipi/canva_verde`](prototipi/canva_verde): versione precedente dello stile Canva verde.
- [`prototipi/top20`](prototipi/top20): prove grafiche per il grafico top 20 linee locali.
- [`prototipi/bbcstyle`](prototipi/bbcstyle): prove con stile BBC/Datawrapper-like.
- [`prototipi/sleek`](prototipi/sleek): prime prove di stile piu' neutro/sleek.
- [`utilities/genera_catalogo_grafici.py`](utilities/genera_catalogo_grafici.py): utility per catalogare rapidamente i grafici della presentazione iniziale.

## Requisiti

Gli script Python usano principalmente:

- `pandas`
- `numpy`
- `matplotlib`
- `Pillow`
- `openpyxl`
- `plotly`
- `folium`
- `branca`

I file pubblici stabili per verifica e riuso sono i CSV in [`../data/processed`](../data/processed). La mappa completa tra grafici, script e fonti e' in [`../docs/riproducibilita_grafici.md`](../docs/riproducibilita_grafici.md).

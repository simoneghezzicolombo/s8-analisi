# Script di analisi e visualizzazione

Questa cartella raccoglie gli script usati per costruire i grafici e la pagina dati del progetto S8 Milano-Lecco.

## Script principali

- [`../assets/app.js`](../assets/app.js): genera i grafici interattivi della pagina GitHub Pages a partire dai CSV in `data/processed`.
- [`static_charts/genera_grafici_fedeli_canva.py`](static_charts/genera_grafici_fedeli_canva.py): script principale per generare i PNG statici 16:9 usati nella presentazione/Canva.

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

Alcuni script storici assumono la stessa struttura locale usata durante la preparazione del lavoro. I file pubblici stabili per verifica e riuso sono i CSV in [`../data/processed`](../data/processed).

# Riproducibilità

## Risposta breve

Con questo pacchetto una persona può riprodurre **i grafici finali** e **tutti i valori Lombardia/Trenord/TILO marcati `L25`**, inclusa la S8 a 14,8063 milioni, partendo dai file inclusi nel repo.

Non può invece ricalcolare automaticamente da zero tutte le stime nazionali marcate `S`, perché per alcune regioni non esiste un dataset pubblico recente linea-per-linea comparabile o non è stato archiviato nel repo. In quei casi il repo rende riproducibile il **valore finale usato** e la **regola/assunzione**, ma non una pipeline automatica da raw ufficiale.

## Come riprodurre tutto ciò che è automatizzato

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r scripts/requirements.txt
python scripts/reproducibility/top20/make_all.py
python scripts/reproducibility/top20/check_reproducibility.py
```

Output atteso:

- `figures/reproducibility/top20/s8_top20_static_bar_slide.png`
- `data/reproducibility/top20/s8_14_8063_calculation_detail.csv`
- `data/reproducibility/top20/lombardia_2025_annualized_top20_lines.csv`

## Cosa viene verificato automaticamente

Lo script `scripts/reproducibility/top20/check_reproducibility.py` controlla:

1. esistenza dei file dati principali;
2. che i valori `L25` in `top20_lines.csv` coincidano con quelli ricalcolati da raw Lombardia 2025;
3. che la S8 risulti `14.8063` milioni;
4. che i grafici principali esistano.

## Livelli di riproducibilità

| Status | Cosa significa | Riproducibilità |
|---|---|---|
| `L25` | Calcolo da raw Lombardia 2025 incluso | piena |
| `R` | Dato ufficiale diretto archiviato nel CSV | alta, con verifica manuale sulla fonte |
| `R/S` | Dato ufficiale parziale trasformato in stima | parziale |
| `S` | Stima modellata/manuale | trasparente, non automatica |

## Perché non tutto è `L25`/`R`

Non esiste un dataset nazionale unico e pubblico, post-Covid, con passeggeri annui linea-per-linea per tutte le linee regionali/suburbane italiane. Per questo la classifica combina dati ufficiali, calcoli diretti e stime ragionate. Le stime sono dichiarate in `data/reproducibility/top20/estimation_log.csv` e `data/reproducibility/top20/ESTIMATION_LOG.md`.

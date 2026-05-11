# Riproducibilità core

Questi script ricostruiscono i principali CSV pubblicati sul sito a partire dai raw locali in `data/raw` e dai parametri documentati in `data/reproducibility`.

## Comando unico

```bash
python scripts/reproducibility/core/build_all.py --rawdir data/raw --outdir outputs/rebuilt --threshold 700
python scripts/reproducibility/core/validate_against_processed.py --rebuilt outputs/rebuilt
```

Il comando genera:

- `linee_suburbane/linee_s_indice_2019_2025.csv`
- `s8_indice_stazioni/stazioni_s8_indice_2015_2025.csv`
- `s8_peso_punta/peso_punta_stazioni_s8_2015_2025.csv`
- `s8_peso_punta/crescita_meratese_punta_morbida_2015_2025.csv`
- `scatter_lombardia/scatter_stazioni_lombarde_2019_2025.csv`

## Script

- `00_download_data.py`: scarica i dataset regionali grezzi, quando gli URL pubblici sono disponibili.
- `01_s8_indice_stazioni_saliti24h.py`: ricostruisce la serie 2015-2025 delle stazioni S8, base 2019 = 100.
- `02_linee_suburbane_comunicati.py`: ricostruisce l'indice 2019-2025 delle linee suburbane Trenord dai valori pubblicati e dalle ipotesi documentate.
- `03_s8_peso_punta_mattutina.py`: ricostruisce peso della punta e crescita meratese in punta/morbida.
- `04_scatter_lombardia_crescita_carico.py`: ricostruisce lo scatter Lombardia 2019-2025 con filtro base 700 saliti/24h.
- `validate_against_processed.py`: controlla che i CSV rigenerati corrispondano ai CSV pubblicati in `data/processed`.

I CSV prodotti sono stati confrontati con quelli in `data/processed` e corrispondono esattamente per righe, colonne e valori.

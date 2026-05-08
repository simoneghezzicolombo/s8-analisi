# Calcolo Lombardia/Trenord 2025: dettaglio annualizzazione

Questo file documenta esattamente come sono stati calcolati i valori `L25` usati nella classifica, inclusa la S8 = **14,8063 milioni**.

## Fonte dati

Dataset raw incluso nel pacchetto:

- `data/raw/regione_lombardia_frequentazione_linee_sfr_20260424.csv`

Fonte web indicata nella base dati:

- https://hub.dati.lombardia.it/Mobilit-e-trasporti/Dati-di-frequentazione-delle-linee-del-servizio-fe/dpns-ehdj

Nel dataset il campo `Viaggiatori` è letto come **migliaia di viaggiatori medi giornalieri** per linea, campagna e tipo giorno.

## Perché non basta moltiplicare il feriale di novembre per 300

Per S8 il dato feriale di novembre 2025 è **51,6 mila/giorno**, ma non rappresenta tutti i giorni dell’anno. Il calcolo usa anche sabati, festivi e stagionalità:

- novembre = proxy del periodo ordinario/lavorativo;
- maggio = proxy del periodo spalla/inizio estate;
- luglio = proxy del periodo estivo/vacanza, incluso agosto.

## Pesi calendario usati

I 365 giorni del 2025 sono stati divisi così:

| Periodo | Mesi coperti | Campagna proxy | Feriali | Sabati | Festivi | Totale |
|---|---:|---|---:|---:|---:|---:|
| Ordinario | gennaio, febbraio, marzo, aprile, ottobre, novembre, dicembre | c2025Novembre | 145 | 29 | 38 | 212 |
| Spalla | maggio, giugno, settembre | c2025Maggio | 63 | 13 | 15 | 91 |
| Estate | luglio, agosto | c2025Luglio | 43 | 9 | 10 | 62 |
| **Totale** | anno 2025 | — | **251** | **51** | **63** | **365** |

Le festività nazionali italiane del 2025 sono trattate come `Festivo`, anche quando cadono in un giorno feriale o di sabato. La tabella è in `data/reproducibility/top20/lombardia_2025_holidays.csv`.

## Formula generale

Per ogni linea:

```text
passeggeri_annui_mln = Σ(viaggiatori_medi_giornalieri_migliaia × giorni_del_tipo / 1000)
```

La somma è fatta su 9 celle:

```text
Novembre × Feriale/Sabato/Festivo
Maggio   × Feriale/Sabato/Festivo
Luglio   × Feriale/Sabato/Festivo
```

## S8: calcolo numerico

| Proxy | Tipo giorno | Viaggiatori medi giornalieri, migliaia | Giorni usati | Contributo annuo, mln |
|---|---|---:|---:|---:|
| c2025Novembre | Feriale | 51,6 | 145 | 7,4820 |
| c2025Novembre | Sabato | 30,5 | 29 | 0,8845 |
| c2025Novembre | Festivo | 17,0 | 38 | 0,6460 |
| c2025Maggio | Feriale | 47,2 | 63 | 2,9736 |
| c2025Maggio | Sabato | 30,0 | 13 | 0,3900 |
| c2025Maggio | Festivo | 15,5 | 15 | 0,2325 |
| c2025Luglio | Feriale | 40,9 | 43 | 1,7587 |
| c2025Luglio | Sabato | 32,0 | 9 | 0,2880 |
| c2025Luglio | Festivo | 15,1 | 10 | 0,1510 |
| **Totale** |  |  | **365** | **14,8063** |

Quindi:

```text
S8 = 14,8063 mln ≈ 14,8 milioni di passeggeri annui
```

## Valori Lombardia/Trenord presenti nella Top 20

Il file `data/reproducibility/top20/lombardia_2025_annualized_top20_lines.csv` contiene il controllo riga-per-riga. I valori finali sono:

| Linea | Valore annuo, mln |
|---|---:|
| S5 | 17.4844 |
| S8 | 14.8063 |
| RE6 | 13.9342 |
| S6 | 12.6148 |
| S1 | 10.4265 |
| S11 | 9.4652 |
| RE80 | 9.0559 |
| S13 | 8.2505 |
| S9 | 8.0912 |


## File di controllo inclusi

- `data/reproducibility/top20/lombardia_2025_weights.csv` — pesi calendario usati.
- `data/reproducibility/top20/lombardia_2025_holidays.csv` — festività trattate come `Festivo`.
- `data/reproducibility/top20/s8_14_8063_calculation_detail.csv` — dettaglio completo S8.
- `data/reproducibility/top20/lombardia_2025_line_contributions_top20.csv` — contributi per le linee Lombardia/TILO presenti nella Top 20.
- `data/reproducibility/top20/lombardia_2025_annualized_top20_lines.csv` — controllo valori finali vs `top20_lines.csv`.
- `data/reproducibility/top20/lombardia_2025_annualized_all_lines.csv` — stessa annualizzazione applicata a tutte le linee presenti nel dataset Lombardia 2025 con le 9 celle disponibili.

## Limite metodologico

Questa annualizzazione è una stima/calcolo operativo, non un dato ufficiale annuo pubblicato da Regione Lombardia per singola linea. È però tracciabile, riproducibile e usa solo dati post-Covid del dataset Lombardia 2025.

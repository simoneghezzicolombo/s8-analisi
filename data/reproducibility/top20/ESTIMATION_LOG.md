# Estimation log e riproducibilità delle cifre

Questo file distingue ciò che è **ricalcolabile automaticamente** da ciò che è una **stima trasparente**.

## Legenda

- `L25`: calcolo deterministico da raw Lombardia 2025 incluso nel repo.
- `R`: dato ufficiale diretto, archiviato nel dataset e verificabile nella fonte primaria.
- `R/S`: dato ufficiale parziale trasformato in stima annuale; il valore finale è archiviato.
- `S`: stima modellata/manuale; non esiste un raw pubblico linea-per-linea sufficiente nel repo.

## Tabella

| Rank | Linea | mln | Status | Riproducibilità | Regola/formula |
|---:|---|---:|---:|---|---|
| 1 | FL1 | 20.7 | S | trasparente ma non deterministica: il valore è riproducibile perché archiviato, non ricalcolabile automaticamente da raw ufficiale completo nel repo | central_mln = stima modellata/manuale post-Covid; valore assunto esplicitamente come parametro della classifica |
| 2 | Metromare | 20.34 | R | deterministica se la fonte pubblica resta disponibile; valore finale archiviato in top20_lines.csv | central_mln = valore ufficiale consuntivo riportato dalla fonte, trasformato in milioni se necessario |
| 3 | S5 | 17.48 | L25 | deterministica: rigenerabile dal raw incluso | central_mln = Σ(Viaggiatori_migliaia_giorno × days_weight / 1000), calcolato da data/raw/regione_lombardia_frequentazione_linee_sfr_20260424.csv con scripts/reproducibility/top20/calculate_lombardia_annualization.py |
| 4 | S8 | 14.81 | L25 | deterministica: rigenerabile dal raw incluso | central_mln = Σ(Viaggiatori_migliaia_giorno × days_weight / 1000), calcolato da data/raw/regione_lombardia_frequentazione_linee_sfr_20260424.csv con scripts/reproducibility/top20/calculate_lombardia_annualization.py |
| 5 | FL3 | 14.5 | S | trasparente ma non deterministica: il valore è riproducibile perché archiviato, non ricalcolabile automaticamente da raw ufficiale completo nel repo | central_mln = stima modellata/manuale post-Covid; valore assunto esplicitamente come parametro della classifica |
| 6 | RE6 | 13.93 | L25 | deterministica: rigenerabile dal raw incluso | central_mln = Σ(Viaggiatori_migliaia_giorno × days_weight / 1000), calcolato da data/raw/regione_lombardia_frequentazione_linee_sfr_20260424.csv con scripts/reproducibility/top20/calculate_lombardia_annualization.py |
| 7 | Roma-Viterbo | 12.73 | R | deterministica se la fonte pubblica resta disponibile; valore finale archiviato in top20_lines.csv | central_mln = valore ufficiale consuntivo riportato dalla fonte, trasformato in milioni se necessario |
| 8 | S6 | 12.61 | L25 | deterministica: rigenerabile dal raw incluso | central_mln = Σ(Viaggiatori_migliaia_giorno × days_weight / 1000), calcolato da data/raw/regione_lombardia_frequentazione_linee_sfr_20260424.csv con scripts/reproducibility/top20/calculate_lombardia_annualization.py |
| 9 | FL5 | 11.6 | S | trasparente ma non deterministica: il valore è riproducibile perché archiviato, non ricalcolabile automaticamente da raw ufficiale completo nel repo | central_mln = stima modellata/manuale post-Covid; valore assunto esplicitamente come parametro della classifica |
| 10 | Firenze-Pistoia-Lucca | 11 | S | trasparente ma non deterministica: il valore è riproducibile perché archiviato, non ricalcolabile automaticamente da raw ufficiale completo nel repo | central_mln = stima modellata/manuale post-Covid; valore assunto esplicitamente come parametro della classifica |
| 11 | Bologna-Piacenza-Milano | 10.56 | R/S | parziale: valore finale archiviato; passaggi di ricostruzione descritti ma non tutti automatizzati | central_mln = stima da frequentazioni ufficiali disponibili per linea/stazione/tipo giorno; trasformazione annuale non pienamente automatizzata nel repo |
| 12 | S1 | 10.43 | L25 | deterministica: rigenerabile dal raw incluso | central_mln = Σ(Viaggiatori_migliaia_giorno × days_weight / 1000), calcolato da data/raw/regione_lombardia_frequentazione_linee_sfr_20260424.csv con scripts/reproducibility/top20/calculate_lombardia_annualization.py |
| 13 | FL8 | 9.9 | S | trasparente ma non deterministica: il valore è riproducibile perché archiviato, non ricalcolabile automaticamente da raw ufficiale completo nel repo | central_mln = stima modellata/manuale post-Covid; valore assunto esplicitamente come parametro della classifica |
| 14 | FL4 | 9.85 | S | trasparente ma non deterministica: il valore è riproducibile perché archiviato, non ricalcolabile automaticamente da raw ufficiale completo nel repo | central_mln = stima modellata/manuale post-Covid; valore assunto esplicitamente come parametro della classifica |
| 15 | FL6 | 9.7 | S | trasparente ma non deterministica: il valore è riproducibile perché archiviato, non ricalcolabile automaticamente da raw ufficiale completo nel repo | central_mln = stima modellata/manuale post-Covid; valore assunto esplicitamente come parametro della classifica |
| 16 | S11 | 9.465 | L25 | deterministica: rigenerabile dal raw incluso | central_mln = Σ(Viaggiatori_migliaia_giorno × days_weight / 1000), calcolato da data/raw/regione_lombardia_frequentazione_linee_sfr_20260424.csv con scripts/reproducibility/top20/calculate_lombardia_annualization.py |
| 17 | RE80 | 9.056 | L25 | deterministica: rigenerabile dal raw incluso | central_mln = Σ(Viaggiatori_migliaia_giorno × days_weight / 1000), calcolato da data/raw/regione_lombardia_frequentazione_linee_sfr_20260424.csv con scripts/reproducibility/top20/calculate_lombardia_annualization.py |
| 18 | S13 | 8.251 | L25 | deterministica: rigenerabile dal raw incluso | central_mln = Σ(Viaggiatori_migliaia_giorno × days_weight / 1000), calcolato da data/raw/regione_lombardia_frequentazione_linee_sfr_20260424.csv con scripts/reproducibility/top20/calculate_lombardia_annualization.py |
| 19 | S9 | 8.091 | L25 | deterministica: rigenerabile dal raw incluso | central_mln = Σ(Viaggiatori_migliaia_giorno × days_weight / 1000), calcolato da data/raw/regione_lombardia_frequentazione_linee_sfr_20260424.csv con scripts/reproducibility/top20/calculate_lombardia_annualization.py |
| 20 | Padova-Venezia | 8 | S | trasparente ma non deterministica: il valore è riproducibile perché archiviato, non ricalcolabile automaticamente da raw ufficiale completo nel repo | central_mln = stima modellata/manuale post-Covid; valore assunto esplicitamente come parametro della classifica |

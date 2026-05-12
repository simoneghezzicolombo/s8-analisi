# Audit fonti web/PDF

Questi script non sostituiscono i dataset finali: servono a verificare automaticamente che le fonti usate siano raggiungibili e contengano gli ancoraggi numerici o testuali dichiarati.

## Comandi

```bash
python scripts/reproducibility/source_audit/audit_metro_sources.py
python scripts/reproducibility/source_audit/audit_top20_sources.py
```

Output principali:

- `data/reproducibility/source_audit/metro_source_audit.csv`
- `data/reproducibility/source_audit/metro_source_audit_summary.csv`
- `data/reproducibility/source_audit/metro_automation_gaps.csv`
- `data/reproducibility/source_audit/top20_source_audit.csv`
- `data/reproducibility/source_audit/top20_automation_gaps.csv`

La cartella `_cache` contiene copie locali temporanee delle pagine/PDF scaricati durante l'audit. Non e' necessaria per la pagina pubblica.

## Interpretazione

- `recomputed_from_structured_lombardia_raw`: valore ricostruito da CSV strutturato, come per le righe Lombardia/Trenord/TILO.
- `direct_value_anchor_found_in_source`: lo script trova nella fonte un numero compatibile con il valore usato.
- `supporting_sources_checked_estimate_not_fully_automatic`: le fonti sono verificabili, ma il valore resta una stima modellata perche' non esiste un dato ufficiale linea-per-linea gia' pronto.
- `regional_source_checked_line_parser_needed`: la fonte regionale e' presente, ma serve un parser dedicato per trasformarla in valore annuo comparabile.
- `metro_automation_gaps.csv`: segnala le fonti metro raggiungibili ma senza ancoraggio atteso, oppure bloccate lato sito durante lo scraping automatico.

In pratica: l'audit rende difendibile la catena fonti -> dataset, ma non inventa un dato ufficiale quando la fonte pubblica non lo contiene.

# Mappa bacini potenziali S8

Questa cartella contiene la dashboard standalone `mappa_isochrone_s8.html`, integrata nella pagina principale come sezione extra prima dei dataset e delle fonti.

La mappa contiene direttamente GeoJSON delle isocrone, stazioni e conteggi di popolazione. Le fonti esterne dichiarate sono WorldPop, OpenStreetMap e Valhalla; l'indice sintetico e' in `../data/reproducibility/isochrone_s8/sources.csv`.

Nota di riproducibilita': questa versione pubblica conserva il dashboard HTML auto-contenuto, non lo script originale di generazione delle isocrone. Per rifare l'elaborazione da zero servono raster WorldPop, rete OSM/Valhalla, lista stazioni e script network-nearest.

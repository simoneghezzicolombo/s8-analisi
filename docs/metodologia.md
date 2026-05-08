# Metodologia

Questa nota descrive in modo sintetico come sono stati costruiti i grafici e i dataset della presentazione sulla S8 Lecco-Carnate-Milano.

## Unita' principali

- `Saliti24H`: passeggeri saliti in stazione nell'arco della giornata.
- `Saliti7-9`: passeggeri saliti nella fascia 7-9.
- `Indice_2019_100`: indicatore normalizzato con valore 2019 = 100.
- `Passeggeri/giorno feriale`: frequentazione in un giorno feriale tipo.
- `Passeggeri annui`: stima o dato annuale, a seconda della fonte indicata nel dataset.

## Linee suburbane Trenord, indice 2019=100

Dataset: `data/processed/linee_s_indice_2019_2025.csv`.

Il grafico confronta S8, S1/S12, S5, S6 e il totale Trenord, riportando ogni serie a base 2019=100.

Per le linee S sono usati valori di utenti/giorno feriale. Per il totale Trenord sono usati passeggeri annui. Il confronto e' possibile perche' il grafico mostra l'indice e non i valori assoluti.

## Variazione assoluta 2025 vs 2024

Dataset: `data/processed/variazione_linee_suburbane_2024_2025.csv`.

Per ogni linea sono confrontate solo le campagne presenti in entrambi gli anni. Questo evita di confrontare una linea con piu' mesi disponibili in un anno rispetto all'altro.

Esempio importante: per S7 sono disponibili maggio e novembre nel 2024 e maggio, luglio, novembre nel 2025. Nel confronto corretto si usano solo maggio e novembre, quindi S7 risulta a -1.000 e non a +7.000.

Sono escluse S10, S30, S31, S40, S50.

## Top 20 linee ferroviarie locali in Italia

Dataset: `data/processed/top20_linee_locali_italia.csv`.

Il dataset combina dati e stime da fonti diverse. Per la Lombardia sono usate campagne di frequentazione 2025; per le altre linee sono usate fonti regionali, operatori o documenti indicati nel dataset.

Il grafico serve a collocare l'ordine di grandezza della S8 nel panorama delle linee ferroviarie locali non AV.

## Benchmark con metropolitane

Dataset: `data/processed/benchmark_metropolitane_s8.csv`.

Il grafico confronta la S8 con alcune metropolitane o linee metropolitane italiane. Il confronto non intende equiparare tecnicamente servizi diversi, ma mostrare che la domanda annuale della S8 e' dello stesso ordine di grandezza di alcune infrastrutture metropolitane.

Le frequenze sono riportate come benchmark indicativo. Le fonti puntuali sono indicate nel dataset.

## Stazioni S8, 2015-2025

Dataset: `data/processed/stazioni_s8_indice_2015_2025.csv`.

Il grafico usa i saliti24H di novembre feriale e li riporta a indice 2019=100. La serie combina:

- `Flussi Stazioni Ferroviarie` per gli anni 2015-2023;
- `Frequentazione stazioni SFR` per il periodo 2024-2025.

Il focus e' sulle stazioni della S8, con particolare attenzione alle quattro stazioni del Meratese:

- Airuno;
- Osnago;
- Cernusco-Merate;
- Olgiate-Calco-Brivio.

## Scatter stazioni lombarde

Dataset: `data/processed/scatter_stazioni_lombarde_2019_2025.csv`.

Il grafico include stazioni lombarde con almeno 700 saliti24H nel 2019. Questo filtro evita che piccole stazioni con basi molto basse dominino il confronto percentuale.

Assi del grafico:

- asse X: crescita percentuale dei saliti24H tra 2019 e 2025;
- asse Y: cambiamento percentuale dei passeggeri per corsa tra 2019 e 2025;
- dimensione del punto: crescita assoluta dei saliti24H.

L'obiettivo e' mostrare se la crescita di domanda e' accompagnata da maggiore carico medio per treno.

## Peso della punta

Dataset: `data/processed/peso_punta_stazioni_s8_2015_2025.csv`.

Il peso della punta e' definito come:

`Saliti7-9 / Saliti24H * 100`

Il grafico mostra come cambia la quota di domanda concentrata nella fascia 7-9 sul totale giornaliero.

## Punta e morbida

Dataset: `data/processed/crescita_meratese_punta_morbida_2015_2025.csv`.

Per ogni stazione:

- `punta` = variazione dei saliti7-9 tra 2019 e 2025;
- `morbida` = variazione dei saliti24H meno variazione dei saliti7-9.

Questa scomposizione serve a distinguere la crescita pendolare classica dalla crescita distribuita fuori dalla punta mattutina.

## Limiti interpretativi

- I dati derivano da campagne di frequentazione, non da conteggi continui giornalieri.
- Alcune serie combinano fonti o metodologie differenti; quando accade, la trasformazione e' esplicitata nel dataset o nella reference.
- I confronti tra linee ferroviarie e metropolitane hanno funzione di benchmark pubblico, non di equivalenza tecnica tra servizi.
- I valori annuali per alcune linee sono stime o conversioni da dati giornalieri; la colonna fonte/metodo va sempre consultata.


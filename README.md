# Grafo delle notizie di giustizia di Ottorighe

Rete di persone, enti, fonti, categorie e articoli dell'archivio di [Ottorighe](https://www.ottorighe.it/), con i collegamenti tra loro: chi compare in quale articolo, da quali testate arriva la notizia, quali articoli sono correlati. Si esplora dal browser nella [mappa delle notizie](https://www.ottorighe.it/mappa-notizie/) e si legge in forma di testo nell'[indice dei collegamenti](https://www.ottorighe.it/mappa-notizie/indice/).

> **In breve.** 1.317 nodi e 7.311 collegamenti (copia del 28/10/2026): 898 articoli pubblicati dal 6 aprile al 27 ottobre 2026, 23 schede di persone ed enti, 387 fonti, 9 categorie. Quattro file pronti per un foglio di calcolo, per Gephi o per i dati collegati.

## Che cosa c'è in questo repository

| Percorso | Contenuto |
|---|---|
| [`dati/nodi.csv`](dati/nodi.csv) | Un nodo per riga: persone, enti, fonti, categorie, articoli |
| [`dati/archi.csv`](dati/archi.csv) | Un collegamento per riga, con tipo e peso |
| [`dati/grafo.graphml`](dati/grafo.graphml) | Il grafo intero, per Gephi, Cytoscape, NetworkX, igraph |
| [`dati/grafo.jsonld`](dati/grafo.jsonld) | Articoli, persone ed enti come dati strutturati schema.org |
| [`DIZIONARIO-DATI.md`](DIZIONARIO-DATI.md) | Significato di ogni colonna e di ogni tipo di collegamento |
| [`src/grafo_dataset.py`](src/grafo_dataset.py) | Ricrea i quattro file dal JSON pubblico del sito (solo libreria standard di Python) |
| [`CITATION.cff`](CITATION.cff) | Come citare questo lavoro |

I file qui sono una **copia datata**. La versione sempre aggiornata, rigenerata ogni mattina alle 07:00, si scarica da:

- https://www.ottorighe.it/wp-json/ottorighe/v1/grafo-dati/nodi.csv
- https://www.ottorighe.it/wp-json/ottorighe/v1/grafo-dati/archi.csv
- https://www.ottorighe.it/wp-json/ottorighe/v1/grafo-dati/grafo.graphml
- https://www.ottorighe.it/wp-json/ottorighe/v1/grafo-dati/grafo.jsonld

## Come sono fatti i dati

- **Articoli**: quelli pubblicati da Ottorighe, con titolo, indirizzo, data e tag.
- **Persone ed enti**: le sole che hanno una scheda su Ottorighe (23 oggi), non tutti i nomi citati negli articoli. Un'assenza nel grafo non dice che una persona non compaia nelle notizie.
- **Fonti**: le testate da cui arrivano le notizie su cui si basano gli articoli.
- **Categorie**: quelle del sito (Magistratura, Politica, Mafia, Carcere, Processi e così via).
- **Collegamenti**: chi compare in un articolo (protagonista o citato), la fonte, la categoria, gli articoli correlati con il motivo del legame.

Le relazioni persone-articoli e gli articoli correlati sono valutati con l'aiuto di modelli di intelligenza artificiale. Il grafo copre l'archivio dall'aprile 2026 e cresce ogni giorno.

## Provarlo

Con la sola libreria standard di Python:

```python
import csv
from collections import Counter

archi = list(csv.DictReader(open("dati/archi.csv", encoding="utf-8")))
nodi = {r["id"]: r for r in csv.DictReader(open("dati/nodi.csv", encoding="utf-8"))}

# chi compare di più come protagonista negli articoli
conta = Counter(r["a"] for r in archi if r["tipo"] == "parla_di" and r["nota"] == "protagonista")
for id_, n in conta.most_common(5):
    print(n, nodi[id_]["etichetta"])
```

Con NetworkX (se installato): `networkx.read_graphml("dati/grafo.graphml")`. Con pandas: `pandas.read_csv("dati/archi.csv")`.

Per rigenerare i file dal sito: `python src/grafo_dataset.py`.

## Licenza

Dati e testi: [Creative Commons Attribuzione 4.0](LICENSE) (CC BY 4.0), con indicazione della fonte. Script: licenza MIT ([`LICENSE-CODICE`](LICENSE-CODICE)).

## Come citare

Ottorighe (2026). *Grafo delle notizie di giustizia di Ottorighe*. Versione 2026.10. [https://www.ottorighe.it/mappa-notizie/](https://www.ottorighe.it/mappa-notizie/)

GitHub ricava la citazione anche da [`CITATION.cff`](CITATION.cff).

## Contatti

redazione@ottorighe.it · [www.ottorighe.it](https://www.ottorighe.it/)

---

## English summary

**The Ottorighe news graph** is a dataset of the Italian justice news archive published by Ottorighe: articles (with title, URL, date, tags), the people and institutions that have a profile page on the site, the source outlets, the site categories, and the links between them (who appears in which article, which outlets the news came from, related articles). It comes as two CSV files (nodes and edges), a GraphML file and a schema.org JSON-LD file, and is rebuilt every morning at the URLs above. Relationships between people and articles and between related articles are assessed with the help of AI models. Data and text are released under CC BY 4.0; the script under the MIT licence.

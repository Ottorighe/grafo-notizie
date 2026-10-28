# Dizionario dei dati

Codifica UTF-8, senza BOM, righe terminate da `\n`, separatore virgola. I ritorni a capo dentro un campo sono sostituiti da uno spazio.

## nodi.csv

| Colonna | Significato |
|---|---|
| `id` | Identificativo stabile: `p<numero>` persone ed enti, `a<numero>` articoli, `c<numero>` categorie, `t_<dominio>` fonti. Il numero è l'identificativo del contenuto sul sito. |
| `tipo` | `persona`, `ente`, `articolo`, `fonte`, `categoria` |
| `etichetta` | Nome della persona o dell'ente, titolo dell'articolo, nome della testata, nome della categoria |
| `url` | Pagina su ottorighe.it (persone, enti, articoli, categorie) oppure indirizzo della testata (fonti) |
| `data` | Data di pubblicazione, `AAAA-MM-GG` (solo articoli) |
| `descrizione` | Ruolo (persone ed enti), dominio (fonti), descrizione (categorie) |
| `tag` | Tag dell'articolo, separati da `; ` |

## archi.csv

| Colonna | Significato |
|---|---|
| `da`, `a` | `id` dei due nodi, nella direzione indicata dal tipo |
| `tipo` | `parla_di`: articolo → persona o ente. `ha_fonte`: articolo → fonte. `in_categoria`: articolo → categoria. `correlato_a`: articolo → articolo |
| `peso` | `parla_di`: 3 = citato, 4 e 5 = protagonista (5 è il massimo). `correlato_a`: 4 o 5, più alto è più stretto il legame. `ha_fonte` e `in_categoria`: 1 |
| `nota` | `parla_di`: `citato` o `protagonista`. `correlato_a`: il motivo del collegamento, in una frase. Altrimenti vuota |

Nella copia del 28/10/2026: 609 `parla_di` (272 protagonista, 337 citato), 1.753 `ha_fonte`, 2.200 `in_categoria`, 2.749 `correlato_a`.

## grafo.graphml

Gli stessi nodi e archi, grafo orientato. Attributi dei nodi: `tipo`, `etichetta`, `url`, `data`. Attributi degli archi: `tipo`, `peso`, `nota`.

## grafo.jsonld

Un `@graph` schema.org:

- `Person` e `Organization`, identificati dall'indirizzo della loro scheda (`@id`), con `name`, `url`, `description` (ruolo).
- `NewsArticle` con `headline`, `datePublished`, `keywords` (tag), `articleSection` (categorie), `about` (persone ed enti protagonisti), `mentions` (citati), `relatedLink` (articoli correlati), `citation` (testate delle fonti) e `publisher`.

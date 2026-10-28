#!/usr/bin/env python3
"""Ricrea i file del grafo di Ottorighe: nodi.csv, archi.csv, grafo.graphml, grafo.jsonld.

Legge il JSON pubblico che disegna la mappa (https://www.ottorighe.it/wp-json/ottorighe/v1/grafo)
e scrive i quattro file nella cartella `dati` (o in quella indicata con --out).
Solo libreria standard di Python 3.8 o successivo, nessuna dipendenza.

Uso:
  python src/grafo_dataset.py                       # scarica il JSON dal sito e scrive in dati/
  python src/grafo_dataset.py --file dati.json      # da un file locale
  python src/grafo_dataset.py --confronta           # confronta anche i file con quelli serviti dal sito
"""
import argparse, csv, io, json, os, re, sys, urllib.request

sys.stdout.reconfigure(encoding="utf-8")

SORGENTE = "https://www.ottorighe.it/wp-json/ottorighe/v1/grafo"
ENDPOINT = "https://www.ottorighe.it/wp-json/ottorighe/v1/grafo-dati/"
FILES = ["nodi.csv", "archi.csv", "grafo.graphml", "grafo.jsonld"]
CARTELLA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dati")
XML_VIETATI = re.compile("[^\u0009\u000A\u000D -퟿-�\U00010000-\U0010FFFF]")


def carica(file=None):
    if file:
        return json.load(open(file, encoding="utf-8"))
    r = urllib.request.Request(SORGENTE, headers={"User-Agent": "Mozilla/5.0"})
    return json.loads(urllib.request.urlopen(r, timeout=60).read().decode("utf-8"))


def modello(d):
    base = d.get("base") or "https://www.ottorighe.it/"
    per = {x[0]: {"id": x[0], "nome": x[1], "tipo": x[2], "ruolo": x[3] or "", "slug": x[5] if len(x) > 5 else ""} for x in d["p"]}
    art = {x[0]: {"id": x[0], "titolo": x[1], "data": x[2], "slug": x[3], "tag": x[4] if len(x) > 4 and isinstance(x[4], list) else [],
                  "url": base + str(x[3]).lstrip("/")} for x in d["a"]}
    cat = {x[0]: {"id": x[0], "nome": x[1], "slug": x[2], "desc": x[3] if len(x) > 3 else ""} for x in d["k"]}
    tes = {x[0]: {"id": x[0], "nome": x[1], "dominio": x[2]} for x in d["t"]}
    for p in per.values():
        p["url"] = base + "personaggio/" + p["slug"] + "/" if p["slug"] else ""
    for c in cat.values():
        c["url"] = base + "category/" + c["slug"] + "/"
    for t in tes.values():
        t["url"] = "https://" + t["dominio"]
    return base, per, art, cat, tes


def nodi_archi(d):
    base, per, art, cat, tes = modello(d)
    nodi, archi = [], []
    for p in per.values():
        nodi.append([p["id"], "persona" if p["tipo"] == "persona" else "ente", p["nome"], p["url"], "", p["ruolo"], ""])
    for c in cat.values():
        nodi.append([c["id"], "categoria", c["nome"], c["url"], "", c["desc"], ""])
    for t in tes.values():
        nodi.append(["t_" + t["id"], "fonte", t["nome"], t["url"], "", t["dominio"], ""])
    for a in art.values():
        nodi.append([a["id"], "articolo", a["titolo"], a["url"], a["data"], "", "; ".join(a["tag"])])
    for x in d["m"]:
        if x[0] in per and x[1] in art:
            archi.append([x[1], x[0], "parla_di", int(x[2]), "protagonista" if int(x[2]) >= 4 else "citato"])
    for x in d["pub"]:
        if x[0] in art and x[1] in tes:
            archi.append([x[0], "t_" + x[1], "ha_fonte", 1, ""])
    for x in d["ap"]:
        if x[0] in art and x[1] in cat:
            archi.append([x[0], x[1], "in_categoria", 1, ""])
    for x in d["c"]:
        if x[0] in art and x[1] in art:
            archi.append([x[0], x[1], "correlato_a", int(x[2]), x[3] if len(x) > 3 else ""])
    return nodi, archi


def csv_testo(intest, righe):
    out = io.StringIO(newline="")
    w = csv.writer(out, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    w.writerow(intest)
    for r in righe:
        w.writerow([re.sub(r"\r\n|\r|\n", " ", str(v)) for v in r])
    return out.getvalue()


def xml(s):
    s = XML_VIETATI.sub("", str(s))
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def graphml(d):
    nodi, archi = nodi_archi(d)
    ids = {n[0] for n in nodi}
    o = ['<?xml version="1.0" encoding="UTF-8"?>\n',
         '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">\n',
         '<key id="tipo" for="node" attr.name="tipo" attr.type="string"/>\n',
         '<key id="etichetta" for="node" attr.name="etichetta" attr.type="string"/>\n',
         '<key id="url" for="node" attr.name="url" attr.type="string"/>\n',
         '<key id="data" for="node" attr.name="data" attr.type="string"/>\n',
         '<key id="tipo_arco" for="edge" attr.name="tipo" attr.type="string"/>\n',
         '<key id="peso" for="edge" attr.name="peso" attr.type="int"/>\n',
         '<key id="nota" for="edge" attr.name="nota" attr.type="string"/>\n',
         '<graph id="ottorighe" edgedefault="directed">\n']
    for n in nodi:
        o.append('<node id="%s"><data key="tipo">%s</data><data key="etichetta">%s</data><data key="url">%s</data><data key="data">%s</data></node>\n'
                 % (xml(n[0]), xml(n[1]), xml(n[2]), xml(n[3]), xml(n[4])))
    i = 0
    for e in archi:
        if e[0] in ids and e[1] in ids:
            o.append('<edge id="e%d" source="%s" target="%s"><data key="tipo_arco">%s</data><data key="peso">%d</data><data key="nota">%s</data></edge>\n'
                     % (i, xml(e[0]), xml(e[1]), xml(e[2]), e[3], xml(e[4])))
            i += 1
    o.append('</graph>\n</graphml>\n')
    return "".join(o)


def jsonld(d):
    base, per, art, cat, tes = modello(d)
    g = []
    for p in per.values():
        if not p["url"]:
            continue
        n = {"@type": "Person" if p["tipo"] == "persona" else "Organization", "@id": p["url"], "name": p["nome"], "url": p["url"]}
        if p["ruolo"]:
            n["description"] = p["ruolo"]
        g.append(n)
    about, ment, corr, fonti, sez = {}, {}, {}, {}, {}
    for x in d["m"]:
        if x[0] in per and x[1] in art and per[x[0]]["url"]:
            (about if int(x[2]) >= 4 else ment).setdefault(x[1], []).append({"@id": per[x[0]]["url"]})
    for x in d["c"]:
        if x[0] in art and x[1] in art:
            u = art[x[1]]["url"]
            if u not in corr.setdefault(x[0], []):
                corr[x[0]].append(u)
    for x in d["pub"]:
        if x[0] in art and x[1] in tes:
            t = tes[x[1]]
            fonti.setdefault(x[0], []).append({"@type": "CreativeWork", "publisher": {"@type": "Organization", "name": t["nome"], "url": t["url"]}})
    for x in d["ap"]:
        if x[0] in art and x[1] in cat:
            sez.setdefault(x[0], []).append(cat[x[1]]["nome"])
    for a in art.values():
        n = {"@type": "NewsArticle", "@id": a["url"], "url": a["url"], "headline": a["titolo"]}
        if a["data"]:
            n["datePublished"] = a["data"]
        if a["tag"]:
            n["keywords"] = ", ".join(a["tag"])
        if a["id"] in sez:
            n["articleSection"] = sez[a["id"]]
        if a["id"] in about:
            n["about"] = about[a["id"]]
        if a["id"] in ment:
            n["mentions"] = ment[a["id"]]
        if a["id"] in corr:
            n["relatedLink"] = corr[a["id"]]
        if a["id"] in fonti:
            n["citation"] = fonti[a["id"]]
        n["publisher"] = {"@type": "Organization", "name": "Ottorighe", "url": base}
        g.append(n)
    return json.dumps({"@context": "https://schema.org", "@graph": g}, ensure_ascii=False, separators=(",", ":"))


def tutti(d):
    nodi, archi = nodi_archi(d)
    return {"nodi.csv": csv_testo(["id", "tipo", "etichetta", "url", "data", "descrizione", "tag"], nodi),
            "archi.csv": csv_testo(["da", "a", "tipo", "peso", "nota"], archi),
            "grafo.graphml": graphml(d), "grafo.jsonld": jsonld(d)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file")
    ap.add_argument("--out", default=CARTELLA)
    ap.add_argument("--confronta", action="store_true")
    a = ap.parse_args()
    d = carica(a.file)
    attesi = tutti(d)
    os.makedirs(a.out, exist_ok=True)
    for nome, testo in attesi.items():
        with open(os.path.join(a.out, nome), "w", encoding="utf-8", newline="") as f:
            f.write(testo)
        print("scritto", nome, len(testo.encode("utf-8")) // 1024, "KB")
    nodi, archi = nodi_archi(d)
    print("nodi", len(nodi), "archi", len(archi), "| aggiornato", d.get("g"))
    if a.confronta:
        ok = True
        for nome, testo in attesi.items():
            r = urllib.request.Request(ENDPOINT + nome, headers={"User-Agent": "Mozilla/5.0"})
            try:
                live = urllib.request.urlopen(r, timeout=60).read().decode("utf-8")
            except Exception as e:
                print("SITO", nome, "ERRORE", e); ok = False; continue
            if nome.endswith(".jsonld"):
                uguale = json.loads(live) == json.loads(testo)
            else:
                uguale = live == testo
            print("SITO", nome, "uguale" if uguale else "DIVERSO")
            if not uguale:
                ok = False
                i = next((k for k in range(min(len(live), len(testo))) if live[k] != testo[k]), min(len(live), len(testo)))
                print("   prima differenza a", i, "| sito:", repr(live[max(0, i - 40):i + 60]), "| atteso:", repr(testo[max(0, i - 40):i + 60]))
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

"""Construit site/data.js à partir des fichiers bruts téléchargés par fetch.py.

    python3 scripts/build.py <dossier_brut>

Méthode des classements (reprise telle quelle par la page) :
- pour chaque indicateur, chaque pays prend sa valeur la plus récente, si elle date de moins de
  5 ans par rapport à la dernière année disponible pour l'indicateur ;
- les pays (hors moyenne UE) sont classés selon le sens « mieux » de l'indicateur ;
- score d'un pays sur un indicateur = 100 × (n − rang) / (n − 1) : 100 = meilleur du panel, 0 = dernier ;
- score de domaine = moyenne simple des scores des indicateurs orientés (better ≠ 0) du domaine,
  sans pondération ; les repères de contexte (better = 0) sont affichés mais exclus ; un pays n'a de
  score de domaine que s'il est mesuré sur au moins 60 % des indicateurs orientés du domaine.
"""
import csv
import datetime
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from indicators import (COUNTRIES, DOMAINS, INDICATORS, PISA_2022, PISA_URL,  # noqa: E402
                        SOCIAL_HOUSING)

RAW = sys.argv[1] if len(sys.argv) > 1 else "raw"
OUT = os.path.join(HERE, "..", "site", "data.js")
POLICIES = os.path.join(HERE, "policies.json")
BY_EUROSTAT = {c[3]: c[0] for c in COUNTRIES}
BY_ISO3 = {c[2]: c[0] for c in COUNTRIES}
OWID_NAMES = {"France": "FR", "Germany": "DE", "Belgium": "BE", "Luxembourg": "LU", "Switzerland": "CH", "Italy": "IT",
              "Spain": "ES", "United Kingdom": "UK", "Netherlands": "NL", "Sweden": "SE", "Denmark": "DK",
              "European Union (27)": "EU", "EU (Ember)": "EU"}
MIN_YEAR = 2005


def parse_eurostat(path, scale=1):
    d = json.load(open(path, encoding="utf-8"))
    ids, sizes = d["id"], d["size"]
    cats = {k: {i: c for c, i in v["category"]["index"].items()} for k, v in d["dimension"].items()}
    strides = [1] * len(ids)
    for i in range(len(ids) - 2, -1, -1):
        strides[i] = strides[i + 1] * sizes[i + 1]
    out = {}
    for k, v in d.get("value", {}).items():
        k = int(k)
        pos = {dim: (k // strides[i]) % sizes[i] for i, dim in enumerate(ids)}
        if any(sizes[i] > 1 and dim not in ("geo", "time") and pos[dim] != 0 for i, dim in enumerate(ids)):
            continue  # dimensions annexes : on ne garde que la première modalité
        geo = BY_EUROSTAT.get(cats["geo"][pos["geo"]])
        year = int(cats["time"][pos["time"]][:4])
        if geo and year >= MIN_YEAR and v is not None:
            out.setdefault(geo, {})[year] = v * scale
    return out


def parse_wb(path):
    d = json.load(open(path, encoding="utf-8"))
    out = {}
    for r in d[1] if len(d) > 1 and d[1] else []:
        c = BY_ISO3.get(r.get("countryiso3code") or "")
        if c and r["value"] is not None and int(r["date"]) >= MIN_YEAR:
            out.setdefault(c, {})[int(r["date"])] = r["value"]
    return out


def parse_imf(path, code):
    d = json.load(open(path, encoding="utf-8"))["values"][code]
    this_year = datetime.date.today().year
    out = {}
    for iso, series in d.items():
        c = BY_ISO3.get(iso) or ("EU" if iso in ("EU", "EUQ") else None)
        if not c:
            continue
        for y, v in series.items():
            y = int(y)
            if MIN_YEAR <= y < this_year and v is not None:  # pas de projections
                out.setdefault(c, {})[y] = v
    return out


def parse_owid(path):
    out = {}
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            c = OWID_NAMES.get(r["entity"])
            col = next(k for k in r if k not in ("entity", "code", "year"))
            if c and r[col] and int(r["year"]) >= MIN_YEAR:
                out.setdefault(c, {})[int(r["year"])] = float(r[col])
    return out


def series_for(ind):
    kind, path = ind["kind"], os.path.join(RAW, ind["id"] + (".csv" if ind["kind"] == "owid" else ".json"))
    if kind == "eurostat":
        return parse_eurostat(path, ind.get("scale", 1))
    if kind == "wb":
        return parse_wb(path)
    if kind == "imf":
        return parse_imf(path, ind["code"])
    if kind == "owid":
        return parse_owid(path)
    if kind == "static":
        sub = ind["id"].split("_")[1]
        out = parse_wb(os.path.join(RAW, f"pisa_{sub}_wb.json"))
        for c, v in PISA_2022[sub].items():
            out.setdefault(c, {})[2022] = v
        return out
    raise ValueError(kind)


def latest(series, max_year):
    pts = [(y, v) for y, v in series.items() if y >= max_year - 5]
    return max(pts) if pts else None


def main():
    peers = [c[0] for c in COUNTRIES if c[0] != "EU"]
    inds = []
    for ind in INDICATORS:
        s = series_for(ind)
        if ind.get("avg5"):  # moyenne glissante sur 5 ans
            s = {c: {y: sum(v[y - k] for k in range(5)) / 5 for y in v if all(y - k in v for k in range(5))}
                 for c, v in s.items()}
            s = {c: v for c, v in s.items() if v}
        if not s:
            print("  ⚠ aucune donnée pour", ind["id"], file=sys.stderr)
            continue
        max_year = max(y for v in s.values() for y in v)
        last = {c: latest(v, max_year) for c, v in s.items()}
        last = {c: v for c, v in last.items() if v}
        ranked = sorted([c for c in peers if c in last], key=lambda c: -last[c][1] * (ind["better"] or 1))
        n = len(ranked)
        rank = {c: i + 1 for i, c in enumerate(ranked)}
        score = {c: round(100 * (n - rank[c]) / (n - 1)) for c in ranked} if n > 1 and ind["better"] else {}
        missing = [c for c in peers if c not in last]
        rounding = 2 if max(abs(v) for vv in s.values() for v in vv.values()) < 20 else 1
        inds.append({
            **{k: ind[k] for k in ("id", "domain", "label", "unit", "better", "note", "source")},
            "series": {c: [[y, round(v, rounding)] for y, v in sorted(vv.items())] for c, vv in s.items()},
            "latestYear": max_year, "rank": rank, "score": score, "n": n, "missing": missing,
        })
        fr = last.get("FR")
        print(f"{ind['id']:15s} {max_year}  FR={fr}  rang {rank.get('FR', '-')}/{n}  manquants={missing}")
    # Scores de domaine
    dom_scores = {}
    for d, _ in DOMAINS:
        per = {}
        for i in inds:
            if i["domain"] == d and i["better"]:
                for c, sc in i["score"].items():
                    per.setdefault(c, []).append(sc)
        n_oriented = sum(1 for i in inds if i["domain"] == d and i["better"])
        # Un pays n'est classé sur un domaine que s'il est mesuré sur au moins 60 % de ses indicateurs
        dom_scores[d] = {c: round(sum(v) / len(v)) for c, v in per.items() if len(v) >= 0.6 * n_oriented}
        order = sorted(dom_scores[d], key=lambda c: -dom_scores[d][c])
        print(f"== {d}: FR {dom_scores[d].get('FR')} (rang {order.index('FR') + 1 if 'FR' in order else '-'}/{len(order)})  tête: {order[:3]}")
    policies = json.load(open(POLICIES, encoding="utf-8")) if os.path.exists(POLICIES) else []
    data = {
        "generated": datetime.date.today().isoformat(),
        "countries": [{"id": c[0], "name": c[1]} for c in COUNTRIES],
        "domains": [{"id": d, "name": n} for d, n in DOMAINS],
        "indicators": inds,
        "domainScores": dom_scores,
        "socialHousing": SOCIAL_HOUSING,
        "pisaUrl": PISA_URL,
        "policies": policies,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("window.DATA=")
        json.dump(data, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write(";")
    digest = hashlib.sha1(open(OUT, "rb").read()).hexdigest()[:10]
    page = os.path.join(os.path.dirname(OUT), "index.html")
    if os.path.exists(page):  # empreinte anti-cache
        src = open(page, encoding="utf-8").read()
        new = re.sub(r'src="data\.js(\?v=[\w-]+)?"', f'src="data.js?v={digest}"', src)
        if new != src:
            open(page, "w", encoding="utf-8").write(new)
    print(f"site/data.js : {os.path.getsize(OUT) // 1024} Ko, {len(inds)} indicateurs, {len(policies)} politiques")


if __name__ == "__main__":
    main()

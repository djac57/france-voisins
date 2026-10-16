"""Télécharge les séries des indicateurs (Eurostat, Banque mondiale, FMI, Our World in Data).

    python3 scripts/fetch.py <dossier_brut>

Un fichier brut par indicateur : <id>.json (ou .csv pour OWID). Les données PISA 2022,
non disponibles par API, sont reprises dans indicators.py.
"""
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from indicators import COUNTRIES, EUROSTAT, IMF, INDICATORS, WB  # noqa: E402

UA = "Python-urllib/3"  # le FMI refuse certains en-têtes personnalisés


BROWSER_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def get(url, dest, retries=3, ua=UA):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": ua})
            with urllib.request.urlopen(req, timeout=180) as r, open(dest, "wb") as fh:
                fh.write(r.read())
            return
        except Exception as e:
            if attempt == retries - 1:
                raise
            print(f"  nouvel essai ({e})", file=sys.stderr)
            time.sleep(5 * (attempt + 1))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "raw"
    os.makedirs(out, exist_ok=True)
    geos = "&".join(f"geo={c[3]}" for c in COUNTRIES)
    isos = ";".join(c[2] for c in COUNTRIES)
    done = set()
    for ind in INDICATORS:
        kind = ind["kind"]
        if kind == "eurostat":
            url = EUROSTAT.format(code=ind["code"], params=f"{geos}&{ind['params']}")
        elif kind == "wb":
            url = WB.format(iso=isos, code=ind["code"], extra="")
        elif kind == "imf":
            url = IMF.format(code=ind["code"])
        elif kind == "owid":
            url = ind["url"]
        else:
            continue
        ext = "csv" if kind == "owid" else "json"
        dest = os.path.join(out, f"{ind['id']}.{ext}")
        print(ind["id"], "←", url[:110])
        get(url, dest, ua=BROWSER_UA if kind == "owid" else UA)  # OWID est derrière Cloudflare
        done.add(ind["id"])
    # PISA 2006-2018 : Banque mondiale EdStats (source 12)
    for code, name in [("LO.PISA.MAT", "pisa_math_wb"), ("LO.PISA.REA", "pisa_read_wb")]:
        get(WB.format(iso=isos, code=code, extra="&source=12"), os.path.join(out, name + ".json"))
        print(name, "ok")
    print(len(done) + 2, "fichiers")


if __name__ == "__main__":
    main()

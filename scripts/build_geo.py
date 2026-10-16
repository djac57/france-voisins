"""Fond de carte Europe : world-atlas 2.0.2 (countries-50m, Natural Earth, domaine public) → site/geo.js.

    python3 scripts/build_geo.py <countries-50m.json>

Décode la TopoJSON, garde les pays d'Europe, découpe les territoires lointains (Guyane, Canaries…)
et simplifie les tracés (pas d'environ 0,05°) pour un fichier léger.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "site", "geo.js")
BBOX = (-11.5, 34.5, 32.0, 71.5)  # lon min, lat min, lon max, lat max
# Codes ISO 3166 numériques -> codes de la page (les autres pays européens servent de fond)
PANEL = {"250": "FR", "276": "DE", "056": "BE", "442": "LU", "756": "CH", "380": "IT", "724": "ES",
         "826": "UK", "528": "NL", "752": "SE", "208": "DK", "040": "AT"}
STEP = 0.05


def decode_arcs(topo):
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    arcs = []
    for arc in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)
    return arcs


def ring(indices, arcs):
    pts = []
    for i in indices:
        a = arcs[i] if i >= 0 else list(reversed(arcs[~i]))
        pts.extend(a if not pts else a[1:])
    return pts


def simplify(pts):
    out = [pts[0]]
    for p in pts[1:-1]:
        if abs(p[0] - out[-1][0]) + abs(p[1] - out[-1][1]) >= STEP:
            out.append(p)
    out.append(pts[-1])
    return [[round(x, 2), round(y, 2)] for x, y in out]


def inside(pts):
    lon = sum(p[0] for p in pts) / len(pts)
    lat = sum(p[1] for p in pts) / len(pts)
    return BBOX[0] <= lon <= BBOX[2] and BBOX[1] <= lat <= BBOX[3]


def main():
    topo = json.load(open(sys.argv[1], encoding="utf-8"))
    arcs = decode_arcs(topo)
    feats = []
    for g in topo["objects"]["countries"]["geometries"]:
        polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]] if g["type"] == "Polygon" else []
        keep = []
        for poly in polys:
            rings = [ring(r, arcs) for r in poly]
            if rings and len(rings[0]) > 3 and inside(rings[0]):
                rings = [simplify(r) for r in rings if len(r) > 3]
                if len(rings[0]) >= 4:
                    keep.append(rings)
        if keep:
            feats.append({"type": "Feature", "id": PANEL.get(g.get("id", ""), ""),
                          "properties": {"name": g["properties"]["name"]},
                          "geometry": {"type": "MultiPolygon", "coordinates": keep}})
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("window.GEO=")
        json.dump({"type": "FeatureCollection", "features": feats}, fh, separators=(",", ":"))
        fh.write(";")
    print(len(feats), "pays,", os.path.getsize(OUT) // 1024, "Ko ;", sorted(f["id"] for f in feats if f["id"]))


if __name__ == "__main__":
    main()

"""Régénère data/types.json (familles, libellés, tracés des pictogrammes) depuis scripts/pictos.py.
Lancer après toute modification d'un pictogramme : python scripts/construire_types.py"""
import json, os, sys
ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
from pictos import FAMILIES, ICONS, LABEL, F, glyph, pastille
out = {"familles": [{"k": k, "n": n, "c": c} for k, n, c in FAMILIES],
       "types": {k: {"n": LABEL[k], "f": F[k], "g": glyph(k, "currentColor", 2)} for k in ICONS}}
racine = os.path.dirname(ICI)
json.dump(out, open(os.path.join(racine, "data/types.json"), "w"), ensure_ascii=False, separators=(",", ":"))
for k in ICONS:
    open(os.path.join(racine, "marque/pictogrammes", k + ".svg"), "w").write(pastille(k))
print(len(ICONS), "types,", len(FAMILIES), "familles")

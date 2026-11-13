"""Événements découpés par département (data/dep/<code>.json), champs utiles seulement :
lus par « La semaine des cathos » (serveur commun), qui ne peut pas charger le fichier national entier."""
import json, os, glob
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ev = json.load(open(os.path.join(RACINE, "data", "evenements.json"), encoding="utf-8"))
d = os.path.join(RACINE, "data", "dep"); os.makedirs(d, exist_ok=True)
par = {}
for e in ev:
    if not e.get("z"): continue
    par.setdefault(e["z"], []).append({k: e[k] for k in ("id", "t", "type", "s", "e", "h", "hf", "lieu", "w", "z", "lat", "lon", "d", "u", "org", "img") if e.get(k) not in (None, "")})
for f in glob.glob(os.path.join(d, "*.json")):
    if os.path.basename(f)[:-5] not in par: os.remove(f)
for z, l in par.items():
    json.dump(sorted(l, key=lambda x: (x["s"], x.get("h", ""))), open(os.path.join(d, z + ".json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(len(par), "départements")

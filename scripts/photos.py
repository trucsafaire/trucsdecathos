"""Télécharge les photos par type choisies (data/photos-sources.json), recadrées en 3:2 :
photos/types/<f> (1200 px, fiches) et photos/types/min/<f> (540 px, cartes)."""
import json, io, os, urllib.request
from PIL import Image, ImageOps
os.makedirs("photos/types/min", exist_ok=True)
ok = 0
for p in json.load(open("data/photos-sources.json")):
    dst = "photos/types/" + p["f"]
    if os.path.exists(dst): ok += 1; continue
    try:
        req = urllib.request.Request(p["u"], headers={"User-Agent": "TrucsDeCathos/1.0 (contact@trucsdecathos.fr)"})
        im = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=60).read())).convert("RGB")
    except Exception as e:
        print("ÉCHEC", p["f"], e); continue
    for w, d in ((1200, dst), (540, "photos/types/min/" + p["f"])):
        ImageOps.fit(im, (w, w * 2 // 3), Image.LANCZOS).save(d, "JPEG", quality=78, optimize=True, progressive=True)
    ok += 1
print(ok, "photos prêtes")

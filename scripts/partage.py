"""Une petite page par événement des diocèses (e/<slug>.html) pour que les liens partagés
(WhatsApp, Messages, Facebook) affichent le titre, la date et la photo, puis ouvrent la fiche dans l'appli."""
import json, os, re, html, glob, datetime as dt
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://trucsdecathos.fr/"
idx = open(os.path.join(RACINE, "index.html"), encoding="utf-8").read()
PH_T = json.loads(re.search(r"const PH_T = (\{.*?\})", idx).group(1))
PH_N = json.loads(re.search(r"PH_N = (\{.*?\});", idx).group(1))
MOIS = "janvier février mars avril mai juin juillet août septembre octobre novembre décembre".split()
JOURS = "lundi mardi mercredi jeudi vendredi samedi dimanche".split()

def slug(i): return re.sub(r"[^a-z0-9-]+", "-", str(i).lower()).strip("-")[:90]
def photo(e):
    k = PH_T.get(e.get("type")); n = PH_N.get(k)
    if not n: return SITE + "marque/partage-1200x630.png"
    h = 0
    for c in str(e.get("id") or e.get("t") or ""): h = (h * 31 + ord(c)) & 0xFFFFFFFF
    return f"{SITE}photos/types/{k}-{h % n + 1}.jpg"
def quand(e):
    d = dt.date.fromisoformat(e["s"]); t = f"{JOURS[d.weekday()]} {d.day} {MOIS[d.month-1]}"
    return t + (f" · {e['h'].replace(':', ' h ')}" if e.get("h") else "")

os.makedirs(os.path.join(RACINE, "e"), exist_ok=True)
ev = json.load(open(os.path.join(RACINE, "data", "evenements.json"), encoding="utf-8"))
faits = set()
for e in ev:
    s = slug(e["id"])
    if not s or s in faits: continue
    faits.add(s)
    img = e.get("img") if str(e.get("img", "")).startswith("https://") else photo(e)
    titre = html.escape(e["t"]); desc = html.escape(f"{quand(e)} · {e.get('w') or e.get('lieu') or ''} — {e.get('d', '')}"[:200])
    cible = f"{SITE}#e={e['id']}"
    page = f'''<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><title>{titre} · Trucs de cathos</title>
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<meta property="og:type" content="article"><meta property="og:site_name" content="Trucs de cathos">
<meta property="og:title" content="{titre}"><meta property="og:description" content="{desc}">
<meta property="og:image" content="{html.escape(img)}"><meta property="og:url" content="{SITE}e/{s}.html">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{html.escape(cible)}"><meta http-equiv="refresh" content="0;url={html.escape(cible)}">
</head><body><p><a href="{html.escape(cible)}">{titre}</a></p><script>location.replace({json.dumps(cible)})</script></body></html>'''
    with open(os.path.join(RACINE, "e", s + ".html"), "w", encoding="utf-8") as f: f.write(page)
for f in glob.glob(os.path.join(RACINE, "e", "*.html")):
    if os.path.basename(f)[:-5] not in faits: os.remove(f)
print(len(faits), "pages de partage")

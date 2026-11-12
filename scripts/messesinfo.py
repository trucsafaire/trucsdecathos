"""Horaires des messes depuis Messes Info (Conférence des évêques de France), un fichier par département.

Lancer : MESSESINFO_KEY=… python scripts/messesinfo.py            (tous les départements des diocèses)
         MESSESINFO_KEY=… python scripts/messesinfo.py 03 58       (quelques-uns)
La clé (« userkey ») se demande à contact.messesinfo@cef.fr. Elle reste secrète : secret GitHub
MESSESINFO_KEY, jamais dans le dépôt ni dans le navigateur. Sans clé, le script ne fait rien.

API v2 (https://www.messes.info/api/v2, décrite dans test.messes.info/api-docs/swagger.json) :
  GET /department/{n}           → paroisses (communautés) du département
  GET /horaires/{recherche}     → horaires ; la recherche accepte « community:{id} », deux dates
                                  JJ-MM-AAAA (intervalle) et TOUTECELEBRATION (messes et autres offices)
Fenêtre : 15 jours (relevé chaque semaine, une semaine de marge).

Sortie data/messes/<dep>.json, compacte, lue par l'appli pour la commune choisie :
  {"maj": "AAAA-MM-JJ", "src": "Messes Info",
   "l": {"<lieu>": [nom, commune, code postal, lat, lon]},
   "h": [["AAAA-MM-JJ", "HH:MM", "<lieu>", "<type>", "précision"], …]}
"""
import datetime as dt, json, os, re, sys, time, unicodedata, urllib.parse, urllib.request

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.environ.get("MESSESINFO_API", "https://www.messes.info/api/v2")
CLE = os.environ.get("MESSESINFO_KEY", "").strip()
UA = "TrucsDeCathos/1.0 (+https://trucsdecathos.fr)"
JOURS = int(os.environ.get("MESSESINFO_JOURS", "15"))
AUJ = dt.date.today()

def sans_accent(s):
    return unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().lower()

_dernier = [0.0]
def api(chemin, **params):
    attente = _dernier[0] + 0.5 - time.time()
    if attente > 0: time.sleep(attente)
    params.update(format="json", userkey=CLE)
    url = BASE + chemin + "?" + urllib.parse.urlencode(params)
    for essai in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"}), timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (401, 403): raise SystemExit("Messes Info refuse la clé (HTTP %d) : vérifier le secret MESSESINFO_KEY." % e.code)
            if e.code < 500 or essai == 2: raise
        except (urllib.error.URLError, TimeoutError):
            if essai == 2: raise
        finally:
            _dernier[0] = time.time()
        time.sleep(5 * (essai + 1))

def heure(t):
    m = re.match(r"\s*(\d{1,2})\s*[h:H]\s*(\d{2})?", str(t or ""))
    return f"{int(m.group(1)):02d}:{int(m.group(2) or 0):02d}" if m else ""

def jour(d):
    d = str(d or "")
    if re.match(r"\d{4}-\d{2}-\d{2}", d): return d[:10]
    m = re.match(r"(\d{2})[-/](\d{2})[-/](\d{4})", d)
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else ""

def type_de(h, date, hh):
    """Type Messes Info → type Trucs de cathos (pictogramme de l'appli)."""
    tt = (h.get("timeType") or "").upper()
    txt = sans_accent(" ".join(str(h.get(k) or "") for k in ("celebrationName", "comment", "type", "celebration")))
    if re.search(r"vepres", txt): return "vepres"
    if re.search(r"laudes", txt): return "laudes"
    if re.search(r"complies", txt): return "complies"
    if re.search(r"adoration|saint[- ]sacrement", txt): return "adoration"
    if re.search(r"confession|reconciliation|penitent", txt): return "confession"
    if re.search(r"chapelet|rosaire", txt): return "chapelet"
    if re.search(r"chemin de croix", txt): return "chemin-de-croix"
    if re.search(r"latin|tridentin|forme extraordinaire|vetus ordo", txt): return "messe-latin"
    if re.search(r"famille|enfants|jeunes", txt) and tt in ("SUNDAYMASS", "WEEKMASS"): return "messe-familles"
    if re.search(r"rite (byzantin|maronite|syriaque|armenien|copte|ukrainien)|divine liturgie", txt): return "liturgie-orientale"
    if tt == "SUNDAYMASS" or (h.get("celebrationTimeType") or "").upper() == "MASS":
        if h.get("celebration") or (h.get("celebrationCategory") or "OTHER") != "OTHER": return "messe-solennite"
        return "messe-anticipee" if dt.date.fromisoformat(date).weekday() == 5 and hh >= "16:00" else "messe-dominicale"
    if tt == "WEEKMASS": return "messe-semaine"
    if tt == "LITURGYTIME": return "vepres" if hh >= "16:00" else "laudes"
    if re.search(r"messe", txt): return "messe-semaine"
    if re.search(r"parole|adap", txt): return "celebration-parole"
    return None

def lieu_de(loc):
    if not isinstance(loc, dict): return None, None
    lid = loc.get("id")
    try: lat, lon = float(loc.get("latitude")), float(loc.get("longitude"))
    except (TypeError, ValueError): return lid, None
    return lid, [loc.get("name") or "", loc.get("city") or "", str(loc.get("zipcode") or ""), round(lat, 5), round(lon, 5)]

def horaires(recherche):
    """Toutes les pages d'une recherche /horaires."""
    out, page = [], 0
    while page < 40:
        r = api("/horaires/" + urllib.parse.quote(recherche, safe=":/"), limit=500, page=page)
        lot = r.get("listCelebrationTime") or []
        out += lot
        if len(lot) < 500: break
        page += 1
    return out

def departement(dep, d1, d2):
    intervalle = f"{d1:%d-%m-%Y} {d2:%d-%m-%Y} TOUTECELEBRATION"
    communautes = api("/department/" + dep) or []
    vus, tout = set(), []
    for c in communautes:
        cid = c.get("id") if isinstance(c, dict) else None
        if not cid or cid in vus: continue
        vus.add(cid)
        try: tout += horaires(f"community:{cid} {intervalle}")
        except Exception as e: print(f"  {dep} : paroisse {cid} illisible ({e})", flush=True)
    return tout, len(vus)

def main():
    if not CLE:
        print("MESSESINFO_KEY absente : horaires des messes non relevés (clé à demander à contact.messesinfo@cef.fr).")
        return
    ds = json.load(open(os.path.join(RACINE, "data", "dioceses.json"), encoding="utf-8"))
    deps = sys.argv[1:] or sorted({d for x in ds for d in x["deps"]})
    d1, d2 = AUJ, AUJ + dt.timedelta(days=JOURS - 1)
    dossier = os.path.join(RACINE, "data", "messes"); os.makedirs(dossier, exist_ok=True)
    bilan = {}
    for dep in deps:
        try:
            brut, n_par = departement(dep, d1, d2)
        except SystemExit: raise
        except Exception as e:
            print(f"{dep} : en panne ({e}), ancien fichier conservé", flush=True); bilan[dep] = "panne"; continue
        lieux, hs, vus = {}, [], set()
        for h in brut:
            if h.get("active") is False: continue
            date, hh = jour(h.get("date")), heure(h.get("time"))
            if not date or not hh or not (d1.isoformat() <= date <= d2.isoformat()): continue
            lid, l = lieu_de(h.get("locality"))
            lid = lid or h.get("localityId")
            if not lid: continue
            if l: lieux.setdefault(lid, l)
            if lid not in lieux: continue
            typ = type_de(h, date, hh)
            if not typ: continue
            cle = (date, hh, lid, typ)
            if cle in vus: continue
            vus.add(cle)
            prec = re.sub(r"\s+", " ", str(h.get("comment") or h.get("celebrationName") or "")).strip()[:80]
            hs.append([date, hh, lid, typ, prec])
        hs.sort()
        if not hs and brut == []:
            print(f"{dep} : aucun horaire ({n_par} paroisses), ancien fichier conservé", flush=True); bilan[dep] = 0; continue
        json.dump({"maj": AUJ.isoformat(), "src": "Messes Info", "l": lieux, "h": hs},
                  open(os.path.join(dossier, dep + ".json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        bilan[dep] = len(hs)
        print(f"{dep} : {n_par} paroisses, {len(lieux)} lieux, {len(hs)} horaires", flush=True)
    json.dump({"maj": AUJ.isoformat(), "departements": bilan}, open(os.path.join(dossier, "bilan.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()

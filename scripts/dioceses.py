"""Récupère les agendas des diocèses et écrit data/evenements.json pour Trucs de cathos.

Lancer : python scripts/dioceses.py            (toutes les sources)
         python scripts/dioceses.py moulins    (une seule)
Bibliothèque standard uniquement. Politesse : une page par seconde, identifiant clair.

Chaque diocèse publie à sa façon ; un « adaptateur » par site :
  moulins : WordPress + Modern Events Calendar → plan du site des événements, puis chaque page
  nevers  : WordPress + Elementor, type « agenda » → API WordPress, puis chaque page (date sans année)
  autun   : Joomla + Event Booking → liste « événements à venir », puis chaque page (lieu)

Un événement n'est gardé que s'il est à venir, ouvert au public (réunions internes écartées),
classé dans un des 53 types et situé dans une commune reconnue du département.
"""
import datetime as dt, html, json, os, re, sys, time, unicodedata, urllib.request

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "TrucsDeCathos/1.0 (+https://trucsdecathos.fr ; agenda catholique, lecture polie)"
AUJ = dt.date.today()
MOIS = {"janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6, "juillet": 7, "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12,
        "jan": 1, "janv": 1, "feb": 2, "fev": 2, "fevr": 2, "mar": 3, "apr": 4, "avr": 4, "may": 5, "jun": 6, "jul": 7, "juil": 7, "aug": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12}

def sans_accent(s):
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()

_dernier = [0.0]
def lire(url, pause=1.0):
    attente = _dernier[0] + pause - time.time()
    if attente > 0: time.sleep(attente)
    if os.environ.get("DEBUG"): print("  ·", url, flush=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fr"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8", "replace")
    finally:
        _dernier[0] = time.time()

def texte(h):
    h = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<br\s*/?>|</(p|div|li|h\d|span)>", "\n", h, flags=re.I)
    return re.sub(r"[ \t\r\f\v]+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()

def lignes(h):
    return [l.strip(" |") for l in texte(h).split("\n") if l.strip(" |")]

# ---------- Communes (géolocalisation à la commune) ----------
def communes(deps):
    f = os.path.join(RACINE, "data", "communes-fr.json")
    data = json.load(open(f, encoding="utf-8")) if os.path.exists(f) else json.loads(lire("https://trucsafaire.fr/data/communes-fr.json", 0))
    out = [c for c in data if c[1] in deps]
    out.sort(key=lambda c: -len(c[0]))  # « Saint-Pourçain-sur-Sioule » avant « Sioule »
    return [(re.compile(r"(?<![a-z])" + re.escape(sans_accent(c[0]).replace("-", " ")).replace(r"\ ", r"[\s-]+") + r"(?![a-z])"), c) for c in out if len(c[0]) > 2]

MOTS_COMMUNS = {"vers", "messe", "sens", "pouilly", "marches", "foi", "joie", "paix", "saint", "jean", "port", "lieu", "bois", "pont", "val", "mont", "ville", "rue"}
def trouver_commune(cs, lieu, titre="", corps="", ville_siege=None):
    """Commune du département : d'abord dans le lieu (« 71110 Semur-en-Brionnais », « Église de Saulcet »).
    Un lieu renseigné mais hors du département (« Brioude ») = événement écarté : on ne cherche pas ailleurs.
    Lieu vide : titre puis texte, noms d'au moins 5 lettres seulement (« Vers » est une commune de Saône-et-Loire…).
    Lieu réduit à une adresse (« 43 rue de Paris ») ou à la maison diocésaine : ville du siège du diocèse."""
    def postal(t):
        m = re.search(r"\b\d{5}\s+([A-ZÉÈÂÎÔa-zéèâîô][\w'’ -]+)", t or "")
        if m:
            n = sans_accent(m.group(1))
            for rx, c in cs:
                if rx.match(n): return c
    def nom(t, court):
        n = re.sub(r"\bste?\b\.?", lambda m: "sainte" if m.group(0).startswith("ste") else "saint", sans_accent(t or "").replace("’", "'"))
        for rx, c in cs:
            x = sans_accent(c[0])
            if x in MOTS_COMMUNS or (not court and len(x) < 5): continue
            if rx.search(n): return c
    if lieu and lieu.strip():
        c = postal(lieu) or nom(lieu, True)
        if c: return c
        if ville_siege and re.search(SIEGE, sans_accent(lieu)):
            return cs_ville(cs, ville_siege)
        c = nom(titre, False)  # « Église de X » mal écrit : le titre peut encore dire la commune
        if c: return c
        # lieu générique (« Salle paroissiale, 27 place Jules Ferry », « Cinéma ») : le texte dit souvent la commune ;
        # un nom propre inconnu du département (« Brioude ») reste un lieu ailleurs
        if re.search(r"\b(salle|eglise|chapelle|cinema|rue|place|maison|abbaye|monastere|basilique|sanctuaire|centre|foyer|presbytere)\b", sans_accent(lieu)):
            return postal(corps) or nom(corps, False)
        return None
    if ville_siege and re.search(SIEGE, sans_accent(titre)): return cs_ville(cs, ville_siege)
    return postal(titre) or nom(titre, False) or postal(corps) or nom(corps, False)
SIEGE = (r"^\s*\d+\s*(bis|ter)?,?\s*(rue|place|avenue|bd|boulevard|allee|quai|chemin|impasse)\b|maison diocesaine|maison du diocese|^\s*cathedrale\s*$|"
         r"espace sainte[- ]bernadette|\beveche\b")

# ---------- Classement dans les 53 types ----------
INTERNE = re.compile(r"\b(conseil|commission|reunion|bureau|assemblee generale|equipe d.animation|eap|cpm|cpp|secretariat|rencontre des (pretres|diacres|doyens)|recollection des pretres|"
                     r"formation des (pretres|diacres)|session des pretres|journee des pretres|college des consulteurs|visite pastorale|denier|vote)\b")
REGLES = [  # premier motif trouvé dans le titre (puis le texte) = type
    ("semaine-sainte", r"rameaux|jeudi saint|vendredi saint|vigile pascale|triduum|semaine sainte|messe chrismale"),
    ("vepres", r"\bvepres\b"), ("laudes", r"\blaudes\b"), ("complies", r"\bcomplies\b"),
    ("messe-latin", r"forme extraordinaire|messe (en )?latin|tridentin"),
    ("liturgie-orientale", r"liturgie (byzantine|orientale|maronite|melkite)|divine liturgie|rite (syriaque|maronite|byzantin)"),
    ("ordination", r"ordination|profession (perpetuelle|religieuse)|voeux|consecration"),
    ("confirmation", r"confirmation|confirmands"), ("premiere-communion", r"premiere communion|profession de foi"),
    ("bapteme", r"bapteme"), ("mariage", r"mariage|fiances|couples?\b"),
    ("onction-malades", r"sacrement des malades|onction|messe des malades|pastorale de la sante"),
    ("confession", r"confession|reconciliation|pardon\b(?! breton)|misericorde"),
    ("retraite-tot", r"halte spirituelle|\bspi\b|apprendre a prier|pause au monastere"),
    ("adoration", r"adoration|saint[- ]sacrement|nuit d.adoration"),
    ("louange", r"louange|worship|soiree (de )?priere"),
    ("chapelet", r"chapelet|rosaire"), ("chemin-de-croix", r"chemin de croix"),
    ("neuvaine", r"neuvaine"), ("procession", r"procession|fete[- ]dieu"),
    ("benediction", r"benediction"),
    ("veillee", r"veillee|nuit des eglises|taize|unite des chretiens|oecumen"),
    ("pelerinage", r"pelerinage|pele\b|pardon breton|jubile|reliques"),
    ("sanctuaire-marial", r"journee mariale|notre[- ]dame de|marial|assomption"),
    ("marche", r"marche|randonnee"),
    ("retraite", r"retraite|recollection|journee de desert|desert\b|halte|pause au monastere|\bspi\b|apprendre a prier"),
    ("session", r"session|week-?end|camp\b|universite d.ete"),
    ("cine-debat", r"cine|film|projection|the chosen|serie\b"), ("conference", r"conference|colloque|table ronde|intervention de|temoignage|retour sur"),
    ("debat", r"debat|echange|interreligieu|islamo|judeo"), ("groupe-biblique", r"lectio|bible|biblique|parole de dieu"),
    ("catechese", r"catechese|catechumen|appel decisif|formation|parcours|kerygma|accompagnateurs"),
    ("parcours-decouverte", r"alpha|decouverte de la foi"),
    ("soiree-jeunes", r"jeunes|etudiants|lyceens|collegiens|aumonerie|jmj|servants d.autel"),
    ("eveil-foi", r"eveil a la foi|enfants|cm1|cm2"),
    ("scouts-camps", r"scout|guides de france|patronage"),
    ("rassemblement", r"rassemblement|fete diocesaine|journee diocesaine|congres|vie consacree|assises"),
    ("familles", r"famille|mamans|peres|grands-parents|celibataires|veuf|veuve|deuil"),
    ("concert", r"concert|orgue|chorale|chant\b|musique"),
    ("visite-eglise", r"visite (guidee|commentee|d.eglise|de l.eglise|de la cathedrale)|patrimoine"),
    ("exposition", r"exposition|expo\b"), ("creche", r"creche"),
    ("repas", r"repas|diner|dejeuner|choucroute|paella|couscous"),
    ("kermesse", r"kermesse|fete paroissiale|fete de la paroisse"),
    ("brocante", r"brocante|vide-grenier|braderie|vente"),
    ("solidarite", r"solidarite|secours catholique|maraude|migrants|diaconie|bientraitance"),
    ("mission", r"mission|evangelisation"),
    ("messe-solennite", r"solennite|toussaint|noel|paques|pentecote|ascension|fete patronale|messe solennelle|saint patron"),
    ("messe-familles", r"messe des (familles|jeunes)"),
    ("messe-anticipee", r"messe anticipee"),
    ("messe-dominicale", r"\bmesse\b|eucharistie"),
]
REGLES = [(k.replace("-tot", ""), re.compile(r)) for k, r in REGLES]

def classer(titre, corps=""):
    t = sans_accent(titre)
    if INTERNE.search(t): return None
    for k, rx in REGLES:
        if rx.search(t): return k
    c = sans_accent(corps[:600])
    for k, rx in REGLES:
        if rx.search(c): return k
    return None

# ---------- Dates et heures ----------
def heure(s):
    m = re.search(r"(\d{1,2})\s*[h:]\s*(\d{2})?", s or "")
    if not m: return ""
    h, mi = int(m.group(1)), int(m.group(2) or 0)
    return f"{h:02d}:{mi:02d}" if h < 24 and mi < 60 else ""

def heures(s):
    hs = re.findall(r"\d{1,2}\s*[h:]\s*\d{0,2}", s or "")
    return (heure(hs[0]) if hs else "", heure(hs[1]) if len(hs) > 1 else "")

def date_fr(s, annee_ref=None):
    """« 13 Nov 2026 », « le 22 novembre », « 13/11/2026 » → date (année devinée : prochaine occurrence)."""
    n = sans_accent(s or "")
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", n)
    if m: return dt.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    m = re.search(r"(\d{1,2})(?:er)?\s+([a-z]+)\.?\s*(\d{4})?", n)
    if not m or m.group(2)[:4].rstrip(".") not in MOIS and m.group(2) not in MOIS: return None
    mo = MOIS.get(m.group(2)) or MOIS.get(m.group(2)[:4]) or MOIS.get(m.group(2)[:3])
    j = int(m.group(1))
    if m.group(3): return dt.date(int(m.group(3)), mo, j)
    a = annee_ref or AUJ.year
    try:
        d = dt.date(a, mo, j)
        return d if d >= AUJ - dt.timedelta(days=60) else dt.date(a + 1, mo, j)
    except ValueError:
        return None

def evt(src, ident, titre, debut, fin, h, hf, lieu, commune, desc, url, org, typ):
    return {"id": f"dio-{src}-{ident}", "t": titre[:90], "type": typ, "s": debut.isoformat(), "e": fin.isoformat() if fin and fin != debut else "",
            "h": h, "hf": hf, "lieu": lieu[:90], "w": commune[0], "z": commune[1], "lat": commune[2], "lon": commune[3],
            "d": desc[:600], "u": url, "org": org, "src": src}

# ---------- Adaptateurs ----------
def moulins(cs, journal):
    base = "https://www.catholique-moulins.fr"
    sm = lire(base + "/mec-events-sitemap.xml")
    limite = (AUJ - dt.timedelta(days=300)).isoformat()
    urls = [u for u, lm in re.findall(r"<loc>([^<]+/events/[^<]+)</loc>\s*<lastmod>([^<]+)", sm) if lm[:10] >= limite]
    out = []
    for u in urls[-150:]:
        try: p = lire(u)
        except Exception as e: journal(f"moulins : {u} illisible ({e})"); continue
        m = re.search(r'<h1[^>]*class="[^"]*mec-single-title[^"]*"[^>]*>(.*?)</h1>', p, re.S) or re.search(r"<title>(.*?)(?: - Diocèse de Moulins)?</title>", p, re.S)
        titre = texte(m.group(1)) if m else ""
        bloc = lambda k: (re.search(r'class="' + k + r'"[^>]*>(.*?)</div>\s*</div>', p, re.S) or [None, ""])[1]
        dates = texte(bloc("mec-single-event-date")).replace("Date", "")
        hh = texte(bloc("mec-single-event-time")).replace("Heure", "")
        lieu = texte(bloc("mec-single-event-location")).replace("Lieu", "").strip().split("\n")[0]
        ds = re.findall(r"\d{1,2}\s+[A-Za-zéû]+\.?\s+\d{4}", dates)
        d0 = date_fr(ds[0]) if ds else None
        d1 = date_fr(ds[1]) if len(ds) > 1 else None
        if not d0 or (d1 or d0) < AUJ: continue
        desc = " ".join(l for l in lignes((re.search(r'class="mec-single-event-description[^"]*"[^>]*>(.*?)<div class="mec-event-', p, re.S) or [None, ""])[1]) if not re.match(r"(Date|Heure|Lieu)\b", l))[:600]
        typ = classer(titre, desc)
        if not typ: journal(f"moulins : écarté (type) « {titre} »"); continue
        c = trouver_commune(cs, lieu, titre, desc, "Moulins")
        if not c: journal(f"moulins : écarté (lieu) « {titre} » [{lieu}]"); continue
        h, hf = heures(hh)
        ident = re.search(r"/events/([^/]+)/?$", u).group(1)
        out.append(evt("moulins", ident, titre, d0, d1, h, hf, lieu, c, desc, u, "Diocèse de Moulins", typ))
    return out

def nevers(cs, journal):
    base = "https://www.nievre.catholique.fr"
    out = []
    items = json.loads(lire(base + "/wp-json/wp/v2/agenda?per_page=60&_fields=id,date,link,title,content"))
    for it in items:
        try: p = lire(it["link"])
        except Exception as e: journal(f"nevers : {it['link']} illisible ({e})"); continue
        i = p.find("elementor-location-single")
        ls = lignes(p[i:i + 30000]) if i > 0 else []
        titre = html.unescape(re.sub(r"<[^>]+>", "", it["title"]["rendered"]))
        if titre in ls: ls = ls[ls.index(titre) + 1:]
        publie = dt.date.fromisoformat(it["date"][:10])
        quand = next((l for l in ls[:4] if re.match(r"(le|du|les|à partir du)\s+\d", sans_accent(l))), "")
        if not quand: journal(f"nevers : écarté (date) « {titre} »"); continue
        ds = re.findall(r"\d{1,2}(?:er)?(?:\s+[a-zéû]+)?(?:\s+\d{4})?", quand)
        mois_fin = re.search(r"([a-zéû]+)(?:\s+\d{4})?\s*$", quand)
        d1 = date_fr(ds[-1], publie.year) if ds else None
        d0 = date_fr(ds[0] if re.search(r"[a-z]", sans_accent(ds[0])) else ds[0] + " " + (mois_fin.group(1) if mois_fin else ""), publie.year) if ds else None
        if d0 and d1 and d1 < d0: d0, d1 = d1, d0
        if not d0 or (d1 or d0) < AUJ: continue
        k = ls.index(quand)
        suite = ls[k + 1:k + 4]
        hh = suite[0] if suite and re.match(r"^(de |à |a )?\d{1,2}\s*h", sans_accent(suite[0])) else ""
        lieu = (suite[1] if hh and len(suite) > 1 else suite[0] if suite else "")
        if re.match(r"pour qui|adresse$", sans_accent(lieu)) or re.match(r"(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\b.*\d+\s*h", sans_accent(lieu)): lieu = ""
        desc = texte(it["content"]["rendered"])[:600]
        typ = classer(titre, desc)
        if not typ: journal(f"nevers : écarté (type) « {titre} »"); continue
        c = trouver_commune(cs, lieu, titre, desc, "Nevers")
        if not c: journal(f"nevers : écarté (lieu) « {titre} » [{lieu}]"); continue
        h, hf = heures(hh)
        out.append(evt("nevers", it["id"], titre, d0, d1, h, hf, lieu.split(" - ")[0], c, desc, it["link"], "Diocèse de Nevers", typ))
    return out

def autun(cs, journal):
    base = "https://autun.catholique.fr"
    p = lire(base + "/agendas/evenements-a-venir")
    out = []
    blocs = re.split(r'<h2 class="eb-event-title-container">', p)[1:]
    for b in blocs:
        m = re.search(r'href="([^"]+)">(.*?)</a>', b, re.S)
        if not m: continue
        lien, titre = base + m.group(1), texte(m.group(2))
        t = texte(b[:1500])
        ds = re.findall(r"\d{2}/\d{2}/\d{4}", t)
        hs = re.findall(r"\d{2}:\d{2}", t)
        d0 = date_fr(ds[0]) if ds else None
        d1 = date_fr(ds[1]) if len(ds) > 1 else None
        if not d0 or (d1 or d0) < AUJ: continue
        try: q = lire(lien)
        except Exception as e: journal(f"autun : {lien} illisible ({e})"); continue
        i = q.find('id="eb-event-details"')
        corps = texte(q[i:i + 12000]) if i > 0 else texte(b)
        corps = re.split(r"\n(Partager|Ajouter à mon agenda|Retour)\b", corps)[0]
        lieu = (re.search(r"Lieu\s*:\s*([^\n]+)", corps) or [None, ""])[1].strip()
        typ = classer(titre, corps)
        if not typ: journal(f"autun : écarté (type) « {titre} »"); continue
        c = trouver_commune(cs, lieu, titre, corps, "Autun")
        if not c: journal(f"autun : écarté (lieu) « {titre} » [{lieu}]"); continue
        ident = re.search(r"/evenement/(\d+)", lien).group(1)
        # une plage de plusieurs semaines (appel à voter, inscription) n'est pas un rendez-vous : on garde le début seulement si court
        if d1 and (d1 - d0).days > 10: journal(f"autun : écarté (durée) « {titre} »"); continue
        out.append(evt("autun", ident, titre, d0, d1, hs[0] if hs else "", hs[1] if len(hs) > 1 and d1 in (None, d0) else "", lieu.split(",")[0], c, corps[:600], lien, "Diocèse d’Autun", typ))
    return out

def cs_ville(cs, nom):
    return next((c for _, c in cs if c[0] == nom), None)

SOURCES = {"moulins": (moulins, ["03"]), "nevers": (nevers, ["58"]), "autun": (autun, ["71"])}

def main():
    choix = sys.argv[1:] or list(SOURCES)
    sortie = os.path.join(RACINE, "data", "evenements.json")
    anciens = json.load(open(sortie, encoding="utf-8")) if os.path.exists(sortie) else []
    journal_l = []
    journal = lambda m: (journal_l.append(m), print(m))
    tous = [e for e in anciens if e.get("src") not in choix and (e.get("e") or e["s"]) >= AUJ.isoformat()]
    bilan = {}
    for nom in choix:
        f, deps = SOURCES[nom]
        try:
            ev = f(communes(deps), journal)
        except Exception as e:  # une source en panne ne vide pas les autres ; ses anciens événements sont gardés
            journal(f"{nom} : source en panne ({e}), anciens événements conservés")
            ev = [x for x in anciens if x.get("src") == nom and (x.get("e") or x["s"]) >= AUJ.isoformat()]
        bilan[nom] = len(ev); tous += ev
    vus, final = set(), []
    for e in sorted(tous, key=lambda e: (e["s"], e["h"] or "99")):
        cle = (sans_accent(e["t"]), e["s"], e["h"], e["w"])  # même rendez-vous publié deux fois
        if e["id"] not in vus and cle not in vus: vus.update([e["id"], cle]); final.append(e)
    json.dump(final, open(sortie, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("bilan :", bilan, "· total", len(final))

if __name__ == "__main__":
    main()

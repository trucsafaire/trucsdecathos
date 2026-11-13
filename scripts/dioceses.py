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

import threading, urllib.parse
_dernier, _verrous, _vg = {}, {}, threading.Lock()
def lire(url, pause=1.0, final=False):
    """Une page par seconde et par site (plusieurs diocèses en parallèle)."""
    hote = urllib.parse.urlsplit(url).netloc
    with _vg: v = _verrous.setdefault(hote, threading.Lock())
    with v:
        attente = _dernier.get(hote, 0) + pause - time.time()
        if attente > 0: time.sleep(attente)
        if os.environ.get("DEBUG"): print("  ·", url, flush=True)
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fr"})
        for essai in (1, 2, 3):  # sites parfois lents : on réessaie avant de déclarer la source en panne
            _dernier[hote] = time.time()  # au plus une requête par seconde et par site, une à la fois
            try:
                with urllib.request.urlopen(req, timeout=45) as r:
                    t = r.read(3_000_000).decode("utf-8", "replace")
                    return (t, r.geturl()) if final else t
            except urllib.error.HTTPError:
                raise
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError):
                if essai == 3: raise
                time.sleep(5 * essai)

def texte(h):
    h = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<br\s*/?>|</(p|div|li|h\d|span)>", "\n", h, flags=re.I)
    return re.sub(r"[ \t\r\f\v]+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()

def lignes(h):
    return [l.strip(" |") for l in texte(h).split("\n") if l.strip(" |")]

# ---------- Communes (géolocalisation à la commune) ----------
_communes, _vc = [], threading.Lock()
def communes(deps):
    f = os.path.join(RACINE, "data", "communes-fr.json")
    with _vc:
        if not _communes:
            _communes.extend(json.load(open(f, encoding="utf-8")) if os.path.exists(f) else json.loads(lire("https://trucsafaire.fr/data/communes-fr.json", 0)))
    data = _communes
    out = [c for c in data if c[1] in deps]
    out.sort(key=lambda c: -len(c[0]))  # « Saint-Pourçain-sur-Sioule » avant « Sioule »
    return [(re.compile(r"(?<![a-z])" + re.escape(sans_accent(c[0]).replace("-", " ")).replace(r"\ ", r"[\s-]+") + r"(?![a-z])"), c) for c in out if len(c[0]) > 2]

MOTS_COMMUNS = {"vers", "cours", "centre", "salle", "eglise", "chapelle", "plan", "gare", "lac", "messe", "sens", "pouilly", "marches", "foi", "joie", "paix", "saint", "jean", "port", "lieu", "bois", "pont", "val", "mont", "ville", "rue"}
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
        dep = re.search(r"\((\d{2}|2[ab])\)", lieu.lower())
        if dep and cs and dep.group(1).upper() not in {c[1] for _, c in cs}:
            return None  # « Pontorson (50) » : autre département
        apres = re.search(r"\b(?:à|a)\s+([A-ZÉ][\w'’ -]+)$", lieu.strip())
        c = (nom(apres.group(1), True) if apres else None) or postal(lieu) or nom(lieu, True)
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

def evt(src, ident, titre, debut, fin, h, hf, lieu, commune, desc, url, org, typ, img=""):
    o = {"id": f"dio-{src}-{ident}", "t": titre[:90], "type": typ, "s": debut.isoformat(), "e": fin.isoformat() if fin and fin != debut else "",
            "h": h, "hf": hf if hf != h else "", "lieu": lieu[:90], "w": commune[0], "z": commune[1], "lat": commune[2], "lon": commune[3],
            "d": desc[:400], "u": url, "org": org, "src": src}
    if img: o["img"] = img
    return o

# Images : on garde les photos/affiches, pas les logos ni les icônes du site
RX_IMG_NON = re.compile(r"logo|icon|favicon|blason|armoiries|avatar|placeholder|default|sprite|pixel|\.svg|\.gif", re.I)
def image(u, base=""):
    if isinstance(u, list): u = u[0] if u else ""
    if isinstance(u, dict): u = u.get("url") or u.get("@id") or ""
    u = html.unescape(str(u or "").strip())
    if not u: return ""
    u = urllib.parse.urljoin(base, u) if base else u
    if u.startswith("http://"): u = "https://" + u[7:]
    if not u.startswith("https://") or len(u) > 500 or RX_IMG_NON.search(u) or re.search(r"[\s\"'<>]", u): return ""
    return u

# ---------- Adaptateurs ----------
def og_img(p, base):
    """Image de partage (og:image) d'une page, si ce n'est pas un logo."""
    m = re.search(r'<meta[^>]+property="og:image(?::url)?"[^>]+content="([^"]*)"', p) or re.search(r'<meta[^>]+content="([^"]*)"[^>]+property="og:image"', p)
    return image(m.group(1), base) if m else ""

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
        out.append(evt("moulins", ident, titre, d0, d1, h, hf, lieu, c, desc, u, "Diocèse de Moulins", typ, og_img(p, u)))
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
        out.append(evt("nevers", it["id"], titre, d0, d1, h, hf, lieu.split(" - ")[0], c, desc, it["link"], "Diocèse de Nevers", typ, og_img(p, it["link"])))
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
        out.append(evt("autun", ident, titre, d0, d1, hs[0] if hs else "", hs[1] if len(hs) > 1 and d1 in (None, d0) else "", lieu.split(",")[0], c, corps[:600], lien, "Diocèse d’Autun", typ, og_img(q, lien)))
    return out


# ---------- Adaptateur générique : tous les autres diocèses (data/dioceses.json) ----------
# Ordre d'essai : API « The Events Calendar » (données structurées, lieu et commune) → plans du site
# des événements (Yoast, Rank Math, WordPress) puis chaque page, lue par la première méthode qui marche :
# JSON-LD schema.org/Event, thème commun des diocèses « catholique.fr », Modern Events Calendar,
# Events Manager, puis repérage générique (bloc « date » + bloc « lieu »).
MAX_PAGES = int(os.environ.get("MAX_PAGES", "150"))
HORIZON = int(os.environ.get("HORIZON", "300"))  # jours
JOURS = r"(?:lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)"
RX_MOIS = r"(?:janv(?:ier)?|fev(?:r(?:ier)?)?|mars|avr(?:il)?|mai|juin|juil(?:let)?|aout|sept(?:embre)?|oct(?:obre)?|nov(?:embre)?|dec(?:embre)?|jan|feb|mar|apr|may|jun|jul|aug|sep|dec)\.?"
RX_DATE = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b|\b(\d{1,2})(?:er)?\s+(" + RX_MOIS + r")(?:\s+(\d{4}))?\b")

def quand(t, ref=None):
    """Texte libre → (début, fin, heure, heure de fin). « Du 20 au 22 mars 2027 », « Le 28 novembre 2026 de 9h à 16h30 »,
    « 10/12/2026 20 h 00 min - 22 h 00 min », « Le vendredi 27 novembre à 19:00 »."""
    n = sans_accent(t or "")
    n = re.sub(r"\b(\d{1,2})(?:er)?\s+(?:au|-|et)\s+(\d{1,2})(?:er)?\s+(" + RX_MOIS + r")", r"\1 \3 au \2 \3", n)
    ds, annee = [], None
    for m in RX_DATE.finditer(n):
        if m.group(1): ds.append((int(m.group(3)), int(m.group(2)), int(m.group(1)))); continue
        mo = m.group(5).rstrip(".")
        mo = MOIS.get(mo) or MOIS.get(mo[:4]) or MOIS.get(mo[:3])
        if mo: ds.append((int(m.group(6)) if m.group(6) else None, mo, int(m.group(4))))
        if len(ds) >= 2: break
    if not ds: return None, None, "", ""
    annee = next((a for a, _, _ in reversed(ds) if a), None)
    out = []
    for i, (a, mo, j) in enumerate(ds):
        try:
            if a: out.append(dt.date(a, mo, j)); continue
            if annee:
                d = dt.date(annee, mo, j)
                if i == 0 and len(ds) > 1 and ds[1][0] and (ds[1][1], ds[1][2]) < (mo, j): d = dt.date(annee - 1, mo, j)
                out.append(d)
            else: out.append(date_fr(f"{j} {[k for k, v in MOIS.items() if v == mo][0]}", ref))
        except (ValueError, IndexError): return None, None, "", ""
    d0, d1 = out[0], out[1] if len(out) > 1 else None
    if d0 and d1 and d1 < d0: d1 = None
    reste = RX_DATE.sub(" ", n)
    hs = re.findall(r"(?<![\d/])(\d{1,2})\s*(?:h|:)\s*(\d{2})?(?:\s*min)?(?!\d)", reste)
    hs = [f"{int(h):02d}:{int(mi or 0):02d}" for h, mi in hs if int(h) < 24 and int(mi or 0) < 60]
    return d0, d1, hs[0] if hs else "", hs[1] if len(hs) > 1 else ""

def _jsonld(p):
    for bloc in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', p, re.S | re.I):
        try: j = json.loads(bloc.strip())
        except Exception: continue
        pile = j if isinstance(j, list) else [j]
        while pile:
            o = pile.pop()
            if isinstance(o, list): pile += o; continue
            if not isinstance(o, dict): continue
            if "@graph" in o: pile += o["@graph"] if isinstance(o["@graph"], list) else [o["@graph"]]
            ty = o.get("@type"); ty = ty if isinstance(ty, list) else [ty]
            if any(isinstance(x, str) and x.endswith("Event") for x in ty) and o.get("startDate"): return o
    return None

def _iso(s):
    s = s or ""
    d = dt.date.fromisoformat(s[:10]) if re.match(r"\d{4}-\d{2}-\d{2}", s) else None
    h = s[11:16] if re.match(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}", s) else ""
    return d, ("" if h == "00:00" else h)

def _lieu_ld(loc):
    loc = loc[0] if isinstance(loc, list) and loc else loc
    if isinstance(loc, str): return loc
    if not isinstance(loc, dict): return ""
    a = loc.get("address") or {}
    if isinstance(a, str): a = {"streetAddress": a}
    morceaux = [loc.get("name") or "", a.get("streetAddress") or "", " ".join(x for x in (a.get("postalCode") or "", a.get("addressLocality") or "") if x)]
    return html.unescape(", ".join(x.strip() for x in morceaux if x and x.strip()))

def _bloc(p, motif, n=900):
    m = re.search(r'class="[^"]*(?:' + motif + r')[^"]*"[^>]*>(.{0,' + str(n) + r'})', p, re.S | re.I)
    if not m: return ""
    t = texte(re.sub(r"<[^>]*$", "", m.group(1)))  # bloc coupé au milieu d'une balise
    ls = [l.strip() for l in t.split("\n") if l.strip() and not re.match(r"(chargement de la carte|voir la carte|itin[ée]raire)", l.strip(), re.I)]
    return "\n".join(ls)

def lire_page(p, u):
    """Page d'événement → dict brut (titre, début, fin, heures, lieu, texte) ou None."""
    ld = _jsonld(p)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", p, re.S)
    og = re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"', p)
    tt = re.search(r"<title[^>]*>(.*?)</title>", p, re.S)
    h2 = re.search(r"<h2[^>]*>(.*?)</h2>", p[p.find("<h1"):] if "<h1" in p else p, re.S)
    nom_site = re.compile(r"^(agenda( du dioc[eè]se)?|accueil|[ée]v[éeè]nements?|archives\b.*)$|^(archi)?dioc[eè]se\b|^[ée]glise catholique\b", re.I)
    titre = ""
    for brut in (h1 and h1.group(1), og and og.group(1), tt and tt.group(1), h2 and h2.group(1)):
        t = re.sub(r"\s+", " ", html.unescape(texte(brut or ""))).strip()
        t = re.split(r"\s+[-–|]\s+(?=[^-–|]*(?:dioc[eè]se|catholique)[^-–|]*$)", t, flags=re.I)[0].strip()  # « Titre – Diocèse de X »
        t = re.sub(r"^agenda de (l.[ée]v[êe]que|mgr [^:]+)\s*:\s*", "", t, flags=re.I)
        if 3 < len(t) <= 160 and not nom_site.search(t): titre = t; break
    ogi = re.search(r'<meta[^>]+property="og:image(?::url)?"[^>]+content="([^"]*)"', p) or re.search(r'<meta[^>]+content="([^"]*)"[^>]+property="og:image"', p)
    img = image(ogi.group(1), u) if ogi else ""
    i = p.find("<h1")
    corps = texte(p[i:i + 40000]) if i > 0 else texte(p)[:20000]
    corps = re.sub(r"\s+", " ", corps)
    if ld:
        d0, h = _iso(ld.get("startDate")); d1, hf = _iso(ld.get("endDate"))
        titre = html.unescape(ld.get("name") or titre)
        desc = texte(html.unescape(ld.get("description") or "")) or corps
        return dict(t=titre, d0=d0, d1=d1, h=h, hf=hf, lieu=_lieu_ld(ld.get("location")), corps=desc, img=image(ld.get("image"), u) or img)
    lieu = ""
    for motif_d, motif_l in (("single-event-date", "single-event-place"), ("mec-single-event-date", "mec-single-event-location"),
                             ("em-event-when", "em-event-location"), ("tribe-events-schedule", "tribe-venue")):
        dt_txt = _bloc(p, motif_d, 600)
        if dt_txt:
            if motif_d.startswith("mec"): dt_txt += " " + _bloc(p, "mec-single-event-time", 400)
            lieu = _bloc(p, motif_l, 400).split("\n")[0]
            break
    else:
        dt_txt = ""
        for m in re.finditer(r'class="([^"]*\b(?:date|dates|when|eventdate|event-date|date-event|date_evenement|event_date|agenda-item-date|event-dates|inner-event-dates)\b[^"]*)"[^>]*>(.{0,700})', p, re.S | re.I):
            if "publication" in m.group(1) or "entry-date" in m.group(1): continue
            t = texte(m.group(2))
            if RX_DATE.search(sans_accent(t)): dt_txt = t; break
        lieu = _bloc(p, r"\blieu\b|lieu-event|\blocation\b|event-location|\bvenue\b|venue__name|agenda-item-location|EventPerso-Lieu|\badresse\b", 400).split("\n")[0]
        if not dt_txt: dt_txt = corps[:400]
    dt_txt = re.sub(r"^(date|quand)\s*:?\s*", "", dt_txt.strip(), flags=re.I)[:300]
    lieu = re.sub(r"^(lieu|o[uù])\s*:?\s*", "", lieu.strip(), flags=re.I)
    lieu = re.split(r"\s+(?:Le|Du)\s+\d|\s+Type d", lieu)[0][:120]
    d0, d1, h, hf = quand(dt_txt)
    return dict(t=titre, d0=d0, d1=d1, h=h, hf=hf, lieu=lieu, corps=corps[:1500], img=img)

def _plans(base, journal, nom):
    """Plans du site consacrés aux événements → [(url, lastmod)]."""
    motif = re.compile(r"(event|evenement|agenda|calendrier|mc-events|ajde_events|tribe_events)[^/]*\.xml", re.I)
    exclu = re.compile(r"categor|type|tag|venue|organi|location|lieu|tax|sitemap-posts-(post|page)\b", re.I)
    vus, sms = set(), []
    for idx in ("/sitemap_index.xml", "/wp-sitemap.xml", "/sitemap.xml"):
        try: x = lire(base + idx)
        except Exception: continue
        for loc in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", x):
            loc = html.unescape(loc)
            if loc.endswith(".xml") and motif.search(loc.rsplit("/", 1)[-1]) and not exclu.search(loc.rsplit("/", 1)[-1]) and loc not in vus:
                vus.add(loc); sms.append(loc)
        if sms: break
    paires = []
    for sm in sms[:6]:
        try: x = lire(sm)
        except Exception as e: journal(f"{nom} : plan {sm} illisible ({e})"); continue
        for bloc in re.findall(r"<url>(.*?)</url>", x, re.S):
            l = re.search(r"<loc>\s*([^<\s]+)", bloc)
            m = re.search(r"<lastmod>\s*([^<\s]+)", bloc)
            if l: paires.append((html.unescape(l.group(1)), m.group(1)[:10] if m else ""))
    return paires

def _tribe(base):
    """API REST de The Events Calendar : événements à venir, lieu et commune déjà structurés."""
    out, page = [], 1
    while page <= 6:
        x = json.loads(lire(f"{base}/wp-json/tribe/events/v1/events?per_page=50&page={page}&start_date={AUJ.isoformat()}"))
        for e in x.get("events", []):
            v = e.get("venue") or {}
            v = v if isinstance(v, dict) else {}
            lieu = ", ".join(t for t in (v.get("venue") or "", v.get("address") or "", " ".join(t for t in (v.get("zip") or "", v.get("city") or "") if t)) if t)
            d0, h = _iso(e.get("start_date")); d1, hf = _iso(e.get("end_date"))
            if e.get("all_day"): h = hf = ""
            out.append((e.get("url") or "", dict(t=html.unescape(e.get("title") or ""), d0=d0, d1=d1, h=h, hf=hf, lieu=html.unescape(lieu), corps=texte(e.get("description") or "")[:1500], img=image(e.get("image") or ""))))
        if not x.get("next_rest_url"): break
        page += 1
    return out

# Cache des pages lues (hors dépôt, conservé d'une semaine à l'autre par actions/cache) :
# une page dont la date de modification n'a pas changé n'est pas relue.
CACHE_F = os.environ.get("DIOCESES_CACHE", os.path.join(RACINE, ".cache", "dioceses-pages.json"))
try: CACHE = json.load(open(CACHE_F, encoding="utf-8"))
except Exception: CACHE = {}
CACHE_NEUF = {}
def _vers_cache(r):
    if not r: return None
    return {k: (v.isoformat() if isinstance(v, dt.date) else v) for k, v in r.items() if k != "corps"} | {"corps": (r.get("corps") or "")[:700]}
def _du_cache(c):
    if not c: return None
    return {k: (dt.date.fromisoformat(v) if k in ("d0", "d1") and v else v) for k, v in c.items()}
def cache_ecrire(partiel=False):
    os.makedirs(os.path.dirname(CACHE_F), exist_ok=True)
    json.dump({**CACHE, **CACHE_NEUF} if partiel else CACHE_NEUF, open(CACHE_F, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))

CHEMINS_AGENDA = ("/agenda", "/agenda/", "/agenda/tout-lagenda", "/evenements/", "/evenements", "/events/", "/agenda-du-diocese/", "/agendas/", "/agenda.html")
def _liens_agenda(base, d):
    """Dernier recours : page « agenda » du site, puis les liens vers les pages d'événements qu'elle contient."""
    chemins = ([d["agenda"]] if d.get("agenda") else []) + [base + c for c in CHEMINS_AGENDA]
    for a in chemins:
        try: p, fin = lire(a, final=True)
        except Exception: continue
        hote = urllib.parse.urlsplit(fin).netloc  # l'agenda peut être sur un autre site (agenda.catholique-savoie.fr)
        racine = urllib.parse.urlsplit(fin).path.rstrip("/")
        liens = []
        for h in re.findall(r'href="([^"#]+)"', p):
            u = urllib.parse.urljoin(fin, html.unescape(h)); sp = urllib.parse.urlsplit(u)
            if sp.netloc.replace("www.", "") != hote.replace("www.", "") or sp.query and "ical" in sp.query: continue
            chemin = sp.path.rstrip("/")
            if re.search(r"\.(pdf|jpe?g|png|ics|xml)$|/(page|feed|categor\w*|tag|type|lieu|auteur|author)/|[?&](page|paged)=", u, re.I): continue
            if (racine and chemin.startswith(racine + "/") and chemin.count("/") > racine.count("/")) or re.search(r"/(evenements?|events?|agenda|dates)/(\d{4}/)?[^/]*[a-z][^/]*-[^/]+|share-AGENDA\w+\.html$", chemin):
                if u not in liens: liens.append(u.split("#")[0])
        if len(liens) >= 2: return liens
    return []

def _ics(texte_ics):
    """Fichier iCalendar → [(url, dict brut)]."""
    t = re.sub(r"\r?\n[ \t]", "", texte_ics)  # lignes repliées
    out = []
    for v in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", t, re.S):
        champ = lambda k: (re.search(r"^" + k + r"(?:;[^:\n]*)?:(.*)$", v, re.M) or [None, ""])[1].strip()
        dec = lambda x: x.replace("\\n", "\n").replace("\\,", ",").replace("\\;", ";")
        def jour(x):
            m = re.match(r"(\d{4})(\d{2})(\d{2})(?:T(\d{2})(\d{2}))?", x)
            if not m: return None, ""
            if not m[4]: return dt.date(int(m[1]), int(m[2]), int(m[3])), ""
            t0 = dt.datetime(int(m[1]), int(m[2]), int(m[3]), int(m[4]), int(m[5]))
            if x.endswith("Z"): t0 += dt.timedelta(hours=2 if 4 <= t0.month <= 10 else 1)  # UTC → heure de Paris (à l'heure près)
            return t0.date(), (t0.strftime("%H:%M") if t0.hour >= 6 else "")  # minuit, 1 h : journée entière
        d0, h = jour(champ("DTSTART")); d1, hf = jour(champ("DTEND"))
        if d1 and not hf and d0 and d1 > d0: d1 = d1 - dt.timedelta(days=1)  # fin exclusive des journées entières
        out.append((champ("URL"), dict(t=dec(champ("SUMMARY")), d0=d0, d1=d1 if d1 != d0 else None, h=h, hf=hf,
                                       lieu=dec(champ("LOCATION")).split("\n")[0], corps=texte(dec(champ("DESCRIPTION")))[:1500],
                                       img=next((image(a) for a in re.findall(r"^ATTACH[^:\n]*:(\S+)$", v, re.M) if re.search(r"\.(jpe?g|png|webp)(\?|$)", a, re.I)), ""))))
    return out

def _liste(page, conf, base):
    """Page agenda qui affiche tout : un bloc par rendez-vous (motif conf['bloc']), lu sans ouvrir chaque page.
    Gère aussi les microdonnées schema.org/Event (startDate, name, location)."""
    blocs = re.split(conf.get("bloc") or r'(?=<[^>]+itemtype="https?://schema\.org/Event")', page)[1:]
    out = []
    for b in blocs:
        if conf.get("sans"): b = re.sub(conf["sans"], " ", b, flags=re.S)
        lien = re.search(r'(?:href|itemid)="([^"#]+)"', b)
        lien = urllib.parse.urljoin(base, html.unescape(lien.group(1))) if lien else ""
        nom = ((re.search(conf["titre"], b, re.S) if conf.get("titre") else None) or re.search(r'itemprop="name"[^>]*>(.*?)</', b, re.S) or re.search(r'<(h[1-4]|strong)[^>]*>(?:\s*<a[^>]*>)?(.*?)</', b, re.S)
               or re.search(r'class="[^"]*(?:heading|title|titre)[^"]*"[^>]*>(.*?)</', b, re.S))
        titre = texte(nom.groups()[-1]).strip() if nom else ""
        corps = re.sub(r"\s+", " ", texte(b)).strip()
        sd = re.search(r'itemprop="startDate"[^>]*(?:content|datetime)="([^"]+)"|(?:content|datetime)="([^"]+)"[^>]*itemprop="startDate"', b)
        ed = re.search(r'itemprop="endDate"[^>]*(?:content|datetime)="([^"]+)"', b)
        if sd:
            d0, h = _iso((sd.group(1) or sd.group(2)).replace(" ", "T")); d1, hf = _iso(ed.group(1).replace(" ", "T")) if ed else (None, "")
            _, _, h2, hf2 = quand(corps)
            if not h or h == "12:00": h, hf = h2, hf2  # « midi » mis par défaut quand l'heure n'est pas connue
        else:
            d0, d1, h, hf = quand(corps)
        lieu = ""
        adr = re.search(r'itemprop="address"[^>]*content="([^"]+)"', b)  # Simple Calendar (Google Agenda) : adresse en métadonnée
        m = re.search(r'itemprop="location"[^>]*>(.*?)</div>', b, re.S) or \
            re.search(r'class="[^"]*\b(?:lieu|location|adresse|place)\b[^"]*"[^>]*>(.*?)</', b, re.S)
        if adr: lieu = html.unescape(adr.group(1)).strip()
        elif m: lieu = re.sub(r"\s+", " ", texte(m.group(1))).strip(" >")
        elif conf.get("lieu"):
            m = re.search(conf["lieu"], b, re.S)
            if m: lieu = re.sub(r"\s+", " ", texte(m.group(1))).strip()
        if RX_DATE.search(sans_accent(lieu)) and len(lieu) < 40: lieu = ""  # une date prise pour un lieu
        im = next((image(x, base) for x in re.findall(r'<img[^>]+?(?:data-src|data-lazy-src|src)="([^"]+)"', b) if image(x, base)), "")
        if titre and d0: out.append((lien, dict(t=titre, d0=d0, d1=d1 if d1 != d0 else None, h=h, hf=hf if hf != h else "", lieu=lieu[:120], corps=corps[:1500], img=im)))
    return out

def generique(d, cs, journal):
    nom = d["id"]
    try: _, base = lire(d["url"], final=True)
    except Exception as e: raise RuntimeError(f"site injoignable ({e})")
    sp = urllib.parse.urlsplit(base); base = f"{sp.scheme}://{sp.netloc}"
    bruts, methode = [], ""
    if d.get("ics"):  # calendrier iCalendar publié par le site (Pontoise)
        try: bruts = _ics(lire(d["ics"])); methode = "ics"
        except Exception as e: journal(f"{nom} : calendrier illisible ({e})")
    if not bruts and d.get("liste"):  # page agenda qui affiche tout (Cahors, Chambéry, Cambrai…)
        try:
            p, fin = lire(d["liste"]["url"], final=True); bruts = _liste(p, d["liste"], fin); methode = "liste"
        except Exception as e: journal(f"{nom} : page agenda illisible ({e})")
    if not bruts and d.get("wpjson"):  # type d'événement WordPress (Langres : Sugar Calendar) → chaque page
        try:
            for x in json.loads(lire(d["wpjson"])):
                u = x.get("link")
                if u: bruts.append((u, lire_page(lire(u), u)))
            methode = "wp-json"
        except Exception as e: journal(f"{nom} : API WordPress illisible ({e})")
    if not bruts:
        try:
            bruts = _tribe(base); methode = "tribe"
        except Exception:
            bruts = []
    if not bruts:
        paires = _plans(base, journal, nom) if not d.get("rss") else []
        if d.get("rss"):  # flux RSS de l'agenda (Grenoble) : liens des prochains rendez-vous
            try:
                vus_rss, paires = set(), []
                for u in re.findall(r"<link>\s*(?:<!\[CDATA\[)?\s*([^<\]\s]+)", lire(d["rss"]))[1:]:
                    cle = (re.search(r"([A-Za-z0-9]{8,})\.html$", u) or re.search(r"(.*)", u)).group(1)  # même rendez-vous sous deux adresses
                    if cle not in vus_rss: vus_rss.add(cle); paires.append((html.unescape(u), ""))
                paires = paires[::-1]
            except Exception as e: journal(f"{nom} : flux RSS illisible ({e})")
        if not paires:
            paires = [(u, "") for u in _liens_agenda(base, d)][::-1]  # remis dans l'ordre de la page plus bas
            if not paires: journal(f"{nom} : aucun agenda lisible automatiquement ({base})"); return []
        limite = (AUJ - dt.timedelta(days=400)).isoformat()
        if any(lm for _, lm in paires):
            paires = sorted([pr for pr in paires if pr[1] >= limite], key=lambda pr: pr[1], reverse=True)
        else: paires = paires[::-1]
        methode, repris = "plan", 0
        for u, lm in paires[:MAX_PAGES]:
            if u.rstrip("/") == base or re.search(r"/(events|agenda|evenements?)/?$", u): continue
            c = CACHE.get(u)
            if lm and c and c.get("lm") == lm and "img" in (c.get("r") or {}):
                r = _du_cache(c.get("r")); repris += 1
            else:
                try: r = lire_page(lire(u), u)
                except Exception as e: journal(f"{nom} : {u} illisible ({e})"); continue
            CACHE_NEUF[u] = {"lm": lm, "r": _vers_cache(r)}
            bruts.append((u, r))
        methode += f" ({repris} en cache)"
    freq = {}
    for _, r in bruts:
        if r and r.get("img"): freq[r["img"]] = freq.get(r["img"], 0) + 1
    commune_img = {i for i, n in freq.items() if n >= 3 and n >= len(bruts) * 0.3}
    out = []
    for u, r in bruts:
        if not r or not r["d0"] or not r["t"] or (r["d1"] or r["d0"]) < AUJ: continue
        if r["d1"] and (r["d1"] - r["d0"]).days > 10: journal(f"{nom} : écarté (durée) « {r['t']} »"); continue
        if r["d0"] > AUJ + dt.timedelta(days=HORIZON): continue  # répétitions lointaines (« chaque premier lundi » jusqu'en 2028)
        typ = classer(r["t"], r["corps"])
        if not typ: journal(f"{nom} : écarté (type) « {r['t']} »"); continue
        c = trouver_commune(cs, r["lieu"], r["t"], r["corps"], d.get("siege"))
        if not c and not r["lieu"] and d.get("liste", {}).get("defaut"): c = cs_ville(cs, d["liste"]["defaut"])  # agenda sans lieu (Le Havre)
        if not c: journal(f"{nom} : écarté (lieu) « {r['t']} » [{r['lieu']}]"); continue
        ident = re.sub(r"[^a-z0-9]+", "-", sans_accent(urllib.parse.urlsplit(u).path).strip("/"))[-60:] or str(abs(hash(r["t"])))
        if methode == "tribe": ident += "-" + r["d0"].isoformat()
        lieu = re.split(r",\s*\d{5}\b", r["lieu"])[0]
        out.append(evt(nom, ident, r["t"], r["d0"], r["d1"], r["h"], r["hf"], lieu, c, r["corps"], u, d["nom"], typ, "" if r.get("img") in commune_img else r.get("img", "")))
    journal(f"{nom} : {methode}, {len(bruts)} pages lues, {len(out)} gardés, {sum(1 for e in out if e.get('img'))} avec image")
    return out

def cs_ville(cs, nom):
    return next((c for _, c in cs if c[0] == nom), None)

def paris(cs, journal):
    """Diocèse de Paris (SPIP) : la page agenda liste tout (titre, jour, heure, lieu avec code postal)."""
    base = "https://dioceseparis.fr/"
    out, vus = [], set()
    for debut in (0, 76, 152):
        try: p = lire(base + "-agenda-.html" + (f"?debut5970={debut}" if debut else ""))
        except Exception as e: journal(f"paris : page {debut} illisible ({e})"); break
        blocs = re.findall(r'<div class="block-event">(.*?)(?=<div class="block-event">|<a id=\'pagination|$)', p, re.S)
        if not blocs: break
        for b in blocs:
            m = re.search(r'href="([^"]+)"', b); t = re.search(r'<h4[^>]*>(.*?)</h4>', b, re.S)
            if not m or not t: continue
            lien = urllib.parse.urljoin(base, html.unescape(m.group(1)))
            if lien in vus: continue
            vus.add(lien)
            titre = texte(t.group(1))
            spans = re.findall(r'<span class="date">(.*?)</span>\s*(?:</span>)?', b, re.S)
            dp = re.search(r'block-event-date">(.*?)</p>', b, re.S)
            bloc_date = texte(dp.group(1)) if dp else ""
            lignes = [l.strip() for l in bloc_date.split("\n") if l.strip()]
            lieu = next((l for l in lignes if re.search(r"\(\d{5}\)|\b75\d{3}\b", l)), "")
            quand_txt = " ".join(l for l in lignes if l != lieu)
            d0, d1, h, hf = quand(quand_txt)
            desc = texte(b[b.find("</p>") + 4:])[:400] if "</p>" in b else ""
            if not d0 or (d1 or d0) < AUJ or d0 > AUJ + dt.timedelta(days=HORIZON): continue
            if d1 and (d1 - d0).days > 10: continue
            typ = classer(titre, desc)
            if not typ: journal(f"paris : écarté (type) « {titre} »"); continue
            autre = re.search(r"\((\d{5})\)", lieu)
            c = None if autre and not autre.group(1).startswith("75") else (trouver_commune(cs, lieu, titre, desc, "Paris") or cs_ville(cs, "Paris"))
            if not c: journal(f"paris : écarté (lieu) « {titre} » [{lieu}]"); continue
            ident = re.sub(r"[^a-z0-9]+", "-", lien.rsplit("/", 1)[-1].replace(".html", ""))[:60]
            out.append(evt("paris", ident, titre, d0, d1, h, hf, re.sub(r"\s*\(\d{5}\)", "", lieu), c, desc, lien, "Diocèse de Paris", typ,
                           next((image(x, base) for x in re.findall(r'<img[^>]+?(?:data-src|src)="([^"]+)"', b) if image(x, base)), "")))
    journal(f"paris : {len(vus)} rendez-vous lus, {len(out)} gardés")
    return out

DEDIES = {"moulins": moulins, "nevers": nevers, "autun": autun, "paris": paris}  # adaptateurs écrits à la main, plus précis

def sources():
    """Tous les diocèses de data/dioceses.json : adaptateur dédié s'il existe, sinon générique."""
    ds = json.load(open(os.path.join(RACINE, "data", "dioceses.json"), encoding="utf-8"))
    f = os.path.join(RACINE, "data", "communautes.json")  # communautés et sanctuaires : même mécanique que les diocèses
    if os.path.exists(f): ds += json.load(open(f, encoding="utf-8"))
    return {d["id"]: (d, DEDIES.get(d["id"])) for d in ds}

def main():
    tout = sources()
    choix = [a for a in sys.argv[1:] if a in tout] or list(tout)
    sortie = os.path.join(RACINE, "data", "evenements.json")
    anciens = json.load(open(sortie, encoding="utf-8")) if os.path.exists(sortie) else []
    verrou = threading.Lock()
    def journal(m):
        with verrou: print(m, flush=True)
    tous = [e for e in anciens if e.get("src") not in choix and (e.get("e") or e["s"]) >= AUJ.isoformat()]
    bilan = {}
    def un(nom):
        d, f = tout[nom]
        try:
            cs = communes(d["deps"])
            return nom, (f(cs, journal) if f else generique(d, cs, journal))
        except Exception as e:  # une source en panne ne vide pas les autres ; ses anciens événements sont gardés
            journal(f"{nom} : source en panne ({e}), anciens événements conservés")
            return nom, [x for x in anciens if x.get("src") == nom and (x.get("e") or x["s"]) >= AUJ.isoformat()]
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(int(os.environ.get("FILS", "24"))) as ex:  # sites différents en parallèle
        for nom, ev in ex.map(un, choix):
            bilan[nom] = len(ev); tous += ev
    vus, final = set(), []
    for e in sorted(tous, key=lambda e: (e["s"], e["h"] or "99")):
        cle = (sans_accent(e["t"]), e["s"], e["h"], e["w"])  # même rendez-vous publié deux fois
        if e["id"] not in vus and cle not in vus: vus.update([e["id"], cle]); final.append(e)
    json.dump(final, open(sortie, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    cache_ecrire(partiel=len(choix) < len(tout))
    json.dump({"date": AUJ.isoformat(), "dioceses": bilan, "total": len(final)},
              open(os.path.join(RACINE, "data", "dioceses-bilan.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    couverts = sum(1 for v in bilan.values() if v)
    print(f"bilan : {couverts}/{len(bilan)} diocèses avec des événements · total {len(final)}")

if __name__ == "__main__":
    main()

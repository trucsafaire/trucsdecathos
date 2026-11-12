import math

def star(cx, cy, r, ri=None, n=5):
    ri = ri or r * 0.45
    pts = []
    for i in range(n * 2):
        a = -math.pi / 2 + i * math.pi / n
        rr = r if i % 2 == 0 else ri
        pts.append(f"{cx + rr*math.cos(a):.2f} {cy + rr*math.sin(a):.2f}")
    return "M" + "L".join(pts) + "Z"

def heart(cx, cy, s):
    # heart centred at cx,cy, width ~ 2s
    return (f"M{cx} {cy+s*0.85}C{cx-s*0.2} {cy+s*0.65} {cx-s} {cy+s*0.1} {cx-s} {cy-s*0.35}"
            f"a{s*0.5} {s*0.5} 0 0 1 {s} -{s*0.1}a{s*0.5} {s*0.5} 0 0 1 {s} {s*0.1}"
            f"C{cx+s} {cy+s*0.1} {cx+s*0.2} {cy+s*0.65} {cx} {cy+s*0.85}Z")

def rays(cx, cy, r1, r2, angles):
    out = []
    for a in angles:
        t = math.radians(a)
        out.append(f"M{cx+r1*math.cos(t):.2f} {cy+r1*math.sin(t):.2f}L{cx+r2*math.cos(t):.2f} {cy+r2*math.sin(t):.2f}")
    return "".join(out)

CHAL = "M7 9h10c0 3.3-2.2 5.5-5 5.5S7 12.3 7 9Z M12 14.5V19 M8.5 19.5h7"
CHAL_L = "M4.5 10h9c0 3-2 5-4.5 5S4.5 13 4.5 10Z M9 15v4 M6 19.5h6"

def dots(points, r=1.05):
    return [("dot", x, y, r) for x, y in points]

# Each icon: list of path strings, or ("dot", x, y, r) filled circles, or ("dash", path)
ICONS = {}
F = {}  # family per icon
LABEL = {}

def add(fam, key, label, *parts):
    ICONS[key] = list(parts); F[key] = fam; LABEL[key] = label

# ---- Messes & offices
add("messes", "messe-dominicale", "Messe dominicale", CHAL, "M12 3a2 2 0 1 1 0 4a2 2 0 1 1 0-4Z", "M5.4 5h2 M16.6 5h2 M7.2 1.4l1.2 1.2 M16.8 1.4l-1.2 1.2")
add("messes", "messe-semaine", "Messe en semaine", CHAL, "M12 3a2.2 2.2 0 1 1 0 4.4a2.2 2.2 0 1 1 0-4.4Z")
add("messes", "messe-anticipee", "Messe anticipée (samedi soir)", CHAL_L, "M19.5 2.8a4 4 0 1 0 2.2 7.2a3.2 3.2 0 0 1-2.2-7.2Z")
add("messes", "messe-solennite", "Messe de fête / solennité", CHAL, star(12, 4.4, 2.9))
add("messes", "messe-familles", "Messe des familles / des jeunes", CHAL, heart(12, 4.6, 2.4))
add("messes", "messe-latin", "Messe en latin", "M5 21V11.5C5 7.5 8 4.5 12 3c4 1.5 7 4.5 7 8.5V21", "M9 11.5h6c0 2-1.3 3.4-3 3.4s-3-1.4-3-3.4Z M12 14.9V18 M10 18.6h4", "M3.5 21h17")
add("messes", "laudes", "Laudes (prière du matin)", "M3 19h18", "M7 19a5 5 0 0 1 10 0", rays(12, 19, 6.8, 8.6, [-160, -125, -55, -20]), "M12 3v5 M10 5l2-2 2 2")
add("messes", "vepres", "Vêpres (prière du soir)", "M3 19h18", "M7 19a5 5 0 0 1 10 0", rays(12, 19, 6.8, 8.6, [-160, -125, -55, -20]), "M12 3v5 M10 6l2 2 2-2")
add("messes", "complies", "Complies (prière de la nuit)", "M14 4a7.5 7.5 0 1 0 6 11.5A6 6 0 0 1 14 4Z", star(19.6, 4.2, 1.9), star(20.4, 10.2, 1.1))
add("messes", "celebration-parole", "Célébration de la Parole", "M4 6c3-1 6-1 8 1 2-2 5-2 8-1v8.5c-3-1-6-1-8 1-2-2-5-2-8-1Z M12 7v8.5", "M12 15.5V21 M9 21h6")
add("messes", "semaine-sainte", "Semaine sainte, Rameaux", "M5 21C9 15.5 13 10 19 3",
    *[f"M{x:.1f} {y:.1f}l{-3.2:.1f} {-0.6:.1f} M{x:.1f} {y:.1f}l{0.9:.1f} {3.1:.1f}" for x, y in [(8.5, 16.4), (11.4, 12.4), (14.4, 8.6), (17.2, 5.2)]])
add("messes", "liturgie-orientale", "Liturgie orientale", "M12 2.5v19 M9 5.5h6 M6.5 9.5h11 M9 17l6-2.2")

# ---- Sacrements
add("sacrements", "confession", "Confession, réconciliation", "M8 4.5a3.5 3.5 0 1 1 0 7a3.5 3.5 0 1 1 0-7Z", "M10.5 10.5L19.5 19.5 M15.6 15.6l2.1-2.1 M18 18l2.1-2.1")
add("sacrements", "bapteme", "Baptême", "M12 2.5c2.6 3.5 4.5 6 4.5 8.6a4.5 4.5 0 0 1-9 0c0-2.6 1.9-5.1 4.5-8.6Z", "M3 19.5c1.5-1 3-1 4.5 0s3 1 4.5 0 3-1 4.5 0 3 1 4.5 0")
add("sacrements", "confirmation", "Confirmation", "M12 21c-3.6 0-6-2.4-6-5.6 0-3.4 3-5.4 4-9.6 2.5 2 3 4 3 5.6 1-.6 1.6-1.7 1.8-3 1.9 1.8 3.2 4.3 3.2 7 0 3.2-2.4 5.6-6 5.6Z", "M12 18.2c-1.3 0-2.2-.9-2.2-2 0-1.3.9-2 1.6-3.3 1.3 1.1 2.8 2 2.8 3.3 0 1.1-.9 2-2.2 2Z")
add("sacrements", "premiere-communion", "Première communion", "M12 4.5a6.5 6.5 0 1 1 0 13a6.5 6.5 0 1 1 0-13Z", "M12 7.5v7 M9.2 10.3h5.6", "M9 21h6")
add("sacrements", "mariage", "Mariage, préparation au mariage", "M9 9.5a5 5 0 1 1 0 10a5 5 0 1 1 0-10Z", "M15 9.5a5 5 0 1 1 0 10a5 5 0 1 1 0-10Z", "M13.4 6.4l1.6-2 1.6 2-1.6 1.8Z")
add("sacrements", "ordination", "Ordination, vœux religieux", "M8 3c0 6-.7 12-2 18 M16 3c0 6 .7 12 2 18 M8 3c1.3 1.5 2.6 2.2 4 2.2S14.7 4.5 16 3", "M7.3 13.5v3.4 M5.6 15.2h3.4 M16.7 13.5v3.4 M15 15.2h3.4")
add("sacrements", "onction-malades", "Sacrement des malades", "M10 3h4 M10.5 3v3.5L7 11v8.5A1.5 1.5 0 0 0 8.5 21h7a1.5 1.5 0 0 0 1.5-1.5V11l-3.5-4.5V3", "M12 12.5v5 M9.8 14.7h4.4")

# ---- Prière & adoration
add("priere", "adoration", "Adoration eucharistique", "M12 6a3 3 0 1 1 0 6a3 3 0 1 1 0-6Z", rays(12, 9, 4.6, 7, [-90, -45, 0, 45, 135, 180, -135]), "M12 16.5V20 M8.5 20.5h7")
add("priere", "louange", "Soirée de louange", "M9 17.5V6l10-2v11.5", "M7 15.5a2 2 0 1 1 0 4a2 2 0 1 1 0-4Z", "M17 13.5a2 2 0 1 1 0 4a2 2 0 1 1 0-4Z", "M9 9.5l10-2")
_beads = [(12 + 5.6*math.cos(math.radians(a)), 9.5 + 5.6*math.sin(math.radians(a))) for a in range(-90 + 36, 270, 36) if a % 360 != 90]
add("priere", "chapelet", "Chapelet, rosaire", *dots(_beads, 1.15), "M12 15.1v1.4", "M12 17.2v4.6 M10.2 19h3.6", ("dot", 12, 3.9, 1.15))
add("priere", "chemin-de-croix", "Chemin de croix", "M15.5 3v12 M12 6.5h7", ("dash", "M3.5 21c2.5-3.2 5.5-4.5 9.5-4.5"))
add("priere", "veillee", "Veillée de prière", "M9 10.5h6v10.5H9Z", "M12 3c1.5 1.7 2.2 3 2.2 4.2a2.2 2.2 0 0 1-4.4 0c0-1.2.7-2.5 2.2-4.2Z", "M5 9.5l1.6.8 M19 9.5l-1.6.8 M5.5 4.5l1.4 1.2 M18.5 4.5l-1.4 1.2")
add("priere", "neuvaine", "Neuvaine", "M5 5.5h14a1.5 1.5 0 0 1 1.5 1.5v12a1.5 1.5 0 0 1-1.5 1.5H5A1.5 1.5 0 0 1 3.5 19V7A1.5 1.5 0 0 1 5 5.5Z M8 3v4 M16 3v4",
    *dots([(x, y) for y in (10.5, 13.5, 16.8) for x in (8, 12, 16)], 0.95))
add("priere", "procession", "Procession", "M7 2.5v19", "M7 4h11v10l-5.5-2.5L7 14", "M12.5 6v4 M11 7.5h3")
add("priere", "benediction", "Bénédiction", "M4.5 20l7.5-7.5", "M14.5 7a3 3 0 1 1 0 6a3 3 0 1 1 0-6Z", *dots([(20, 5.5), (20.5, 10.5), (17, 3)], 0.95))

# ---- Pèlerinages & retraites
add("pelerinages", "pelerinage", "Pèlerinage", "M12 20L4.4 10.2a8.5 8.5 0 0 1 15.2 0Z", "M12 20L8.4 6.2 M12 20V5 M12 20l3.6-13.8", "M10 21.3h4")
add("pelerinages", "marche", "Marche, randonnée spirituelle", "M2.5 20l6.5-11 4 6 2.5-3.5 6 8.5Z", "M17.5 3.5a2 2 0 1 1 0 4a2 2 0 1 1 0-4Z")
add("pelerinages", "sanctuaire-marial", "Sanctuaire, journée mariale", "M6.5 9.5l1.5-4 2.5 2.5L12 4l1.5 4L16 5.5l1.5 4Z", "M7 20.5V13l5 4.2 5-4.2v7.5")
add("pelerinages", "retraite", "Retraite, récollection", "M4.5 21V11l7.5-6 7.5 6v10", "M10 21v-4a2 2 0 0 1 4 0v4", "M12 1v3 M10.8 2.2h2.4", "M3 21h18")
add("pelerinages", "session", "Session, camp spirituel", "M2.5 20h19 M12 4L4 20 M12 4l8 16 M12 13l-3 7 M12 13l3 7")

# ---- Formation & partage
add("formation", "conference", "Conférence", "M6.5 11h11l-1.5 10h-8Z", "M12 11V8", "M10.6 2.6h2.8a.8.8 0 0 1 .8.8v2.8a2.2 2.2 0 0 1-4.4 0V3.4a.8.8 0 0 1 .8-.8Z")
add("formation", "debat", "Débat, table ronde", "M3.5 4.5h10v7.5H8.5l-3 2.5V12h-2Z", "M16.5 9.5h4v8h-1.5V20l-3-2.5h-5.5V15")
add("formation", "groupe-biblique", "Groupe biblique, lectio divina", "M3 6c3-1.3 6-1.3 9 .8 3-2.1 6-2.1 9-.8v13c-3-1.3-6-1.3-9 .8-3-2.1-6-2.1-9-.8Z M12 6.8v13", "M16.5 9v5 M14.8 10.8h3.4")
add("formation", "catechese", "Catéchèse, catéchuménat", "M4 4h16v12H10l-4 4v-4H4Z", "M12 6.5v7 M9.5 9h5")
add("formation", "cine-debat", "Ciné-débat", "M3.5 9h17v11h-17Z", "M3.5 9l1.6-4.5h15.4L19 9 M9.6 4.5L8 9 M14.8 4.5L13.2 9")
add("formation", "lecture", "Lecture, librairie", "M4 15.5h16v5H4Z", "M6 10.5h13v5H6Z", "M5 5.5h11v5H5Z")
add("formation", "parcours-decouverte", "Parcours découverte (Alpha…)", "M12 3.5a8.5 8.5 0 1 1 0 17a8.5 8.5 0 1 1 0-17Z", "M15.2 8.8l-1.8 4.6-4.6 1.8 1.8-4.6Z")

# ---- Jeunes & familles
add("jeunes", "soiree-jeunes", "Soirée jeunes, aumônerie", "M8 6a2.5 2.5 0 1 1 0 5a2.5 2.5 0 1 1 0-5Z", "M16 6a2.5 2.5 0 1 1 0 5a2.5 2.5 0 1 1 0-5Z", "M3.5 20c0-3.2 2-5.5 4.5-5.5s4.5 2.3 4.5 5.5 M11.5 20c0-3.2 2-5.5 4.5-5.5s4.5 2.3 4.5 5.5", "M12 1.5v2.6 M10.7 2.8h2.6")
add("jeunes", "eveil-foi", "Éveil à la foi, enfants", "M9 3.5a2.8 2.8 0 1 1 0 5.6a2.8 2.8 0 1 1 0-5.6Z", "M4 20.5c0-4 2.2-8 5-8s5 4 5 8", "M17.5 10a2 2 0 1 1 0 4a2 2 0 1 1 0-4Z", "M14.5 20.5c0-2.8 1.3-4.6 3-4.6s3 1.8 3 4.6")
add("jeunes", "familles", "Familles", "M4 20.5V10l8-6.5 8 6.5v10.5Z", heart(12, 13.4, 3.2))
add("jeunes", "rassemblement", "Grand rassemblement, JMJ", "M12 4a2.6 2.6 0 1 1 0 5.2a2.6 2.6 0 1 1 0-5.2Z", "M5.5 7.5a2.1 2.1 0 1 1 0 4.2a2.1 2.1 0 1 1 0-4.2Z", "M18.5 7.5a2.1 2.1 0 1 1 0 4.2a2.1 2.1 0 1 1 0-4.2Z", "M7.5 20c0-4 2-7 4.5-7s4.5 3 4.5 7 M2 19c0-2.8 1.5-4.8 3.5-4.8 M22 19c0-2.8-1.5-4.8-3.5-4.8")
add("jeunes", "scouts-camps", "Scouts, camps", "M4.5 20.5l15-3.5 M4.5 17l15 3.5", "M12 4c2 2.4 3.4 4.4 3.4 6.4a3.4 3.4 0 0 1-6.8 0c0-1.2.5-2.2 1.3-3.2.3 1 .8 1.6 1.4 1.8 0-1.6.2-3.2.7-5Z")

# ---- Culture & patrimoine
add("culture", "concert", "Concert sacré, orgue", "M5 20.5V11 M8.5 20.5V7 M12 20.5V4 M15.5 20.5V7 M19 20.5V11 M3.5 20.5h17", "M4 13.5l1-1 1 1 M7.5 9.5l1-1 1 1 M11 6.5l1-1 1 1 M14.5 9.5l1-1 1 1 M18 13.5l1-1 1 1")
add("culture", "visite-eglise", "Visite d'église, patrimoine", "M8 21V9.5l4-3.5 4 3.5V21", "M12 1.8v3 M10.8 3h2.4", "M10.5 21v-3.2a1.5 1.5 0 0 1 3 0V21", "M4 21v-7l4-2.5 M20 21v-7l-4-2.5 M2.5 21h19")
add("culture", "exposition", "Exposition", "M3.5 4.5h17v12.5h-17Z", "M6 15l4-4.5 3 3 2-2 3.2 3.5", "M8 21l1.5-4 M16 21l-1.5-4")
add("culture", "creche", "Crèche de Noël", star(12, 3.2, 2.1), "M3 12.5l9-5.5 9 5.5 M5 11.3V20.5h14v-9.2", "M8.8 20.5l1.6-3.8h3.2l1.6 3.8")

# ---- Fraternité & solidarité
add("fraternite", "repas", "Repas, fête paroissiale", "M12 7a5 5 0 1 1 0 10a5 5 0 1 1 0-10Z", "M3.5 4v4.5a1.5 1.5 0 0 0 3 0V4 M5 9v11", "M20.5 20V4c-1.6 1-2.5 3-2.5 5.5V13h2.5")
add("fraternite", "kermesse", "Kermesse, fête", "M2.5 5c6 3.5 13 3.5 19 0", "M4.6 6.4L6.3 12L9.4 7.8Z M10.3 8.1L12 13.4L13.7 8.1Z M14.6 7.8L17.7 12L19.4 6.4Z")
add("fraternite", "brocante", "Brocante, vide-grenier", "M3.5 12.5L11.5 4.5h8v8L11.5 20.5Z", "M15.5 7.1a1.4 1.4 0 1 1 0 2.8a1.4 1.4 0 1 1 0-2.8Z")
add("fraternite", "solidarite", "Solidarité, maraude", heart(12, 8.2, 3.6), "M3 15.5c3 0 4.5 4.5 9 4.5s6-4.5 9-4.5")
add("fraternite", "mission", "Mission, évangélisation", "M4 9.5v5h3l8.5 4.5v-14L7 9.5Z", "M18.5 9a4 4 0 0 1 0 6", "M7.5 14.5l1 5h2.5l-1-5")

FAMILIES = [
    ("messes", "Messes & offices", "#2F6DB5"),
    ("sacrements", "Sacrements", "#6B4A9E"),
    ("priere", "Prière & adoration", "#A87B1E"),
    ("pelerinages", "Pèlerinages & retraites", "#2F7D57"),
    ("formation", "Formation & partage", "#B4532F"),
    ("jeunes", "Jeunes & familles", "#B83E6E"),
    ("culture", "Culture & patrimoine", "#4F5B6E"),
    ("fraternite", "Fraternité & solidarité", "#1F7A80"),
]
FAMCOL = {k: c for k, _, c in FAMILIES}

def glyph(key, color, sw=2):
    out = []
    for p in ICONS[key]:
        if isinstance(p, tuple) and p[0] == "dot":
            out.append(f'<circle cx="{p[1]:.2f}" cy="{p[2]:.2f}" r="{p[3]}" fill="{color}"/>')
        elif isinstance(p, tuple) and p[0] == "dash":
            out.append(f'<path d="{p[1]}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-dasharray="0.1 3.4"/>')
        else:
            out.append(f'<path d="{p}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')
    return "".join(out)

SQ = "M32 0C52.5 0 64 4.6 64 32S52.5 64 32 64 0 59.4 0 32 11.5 0 32 0Z"

def pastille(key, size=None, aria=True):
    col = FAMCOL[F[key]]
    a = f'role="img" aria-label="{LABEL[key]}"' if aria else 'aria-hidden="true"'
    sz = f' width="{size}" height="{size}"' if size else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"{sz} {a}><path d="{SQ}" fill="{col}"/>'
            f'<g transform="translate(14 14) scale(1.5)">{glyph(key, "#FFFFFF", 2.1)}</g></svg>')

def trait(key, color="#141A33", size=None, aria=True):
    a = f'role="img" aria-label="{LABEL[key]}"' if aria else 'aria-hidden="true"'
    sz = f' width="{size}" height="{size}"' if size else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"{sz} {a}>{glyph(key, color, 1.9)}</svg>'

LOGO_ICON = ('<path d="' + SQ + '" fill="#2F6DB5"/>'
             '<path d="M29.5 13.5V38c0 7.5 4.2 12 11.6 12h2.4" fill="none" stroke="#FFFFFF" stroke-width="6.4" stroke-linecap="round" stroke-linejoin="round"/>'
             '<path d="M17.5 27.6 24.6 34C31.5 26.9 38 22.2 46.4 18.6" fill="none" stroke="#FFFFFF" stroke-width="6.4" stroke-linecap="round" stroke-linejoin="round"/>'
             '<circle cx="48.6" cy="46.4" r="4.3" fill="#E8BE55"/>')

"""Pictogrammes de Trucs de cathos : icônes Tabler Icons (MIT, © Paweł Kuna, tabler.io/icons), une par type d'activité.
Les tracés ci-dessous sont copiés tels quels depuis le paquet @tabler/icons 3 (dossier outline) ; TABLER donne le nom d'origine.
Pour changer une icône : choisir un autre nom sur tabler.io/icons, recopier son tracé ici, puis python scripts/construire_types.py."""

FAMILIES = [('messes', 'Messes & offices', '#2F6DB5'),
    ('sacrements', 'Sacrements', '#6B4A9E'),
    ('priere', 'Prière & adoration', '#A87B1E'),
    ('pelerinages', 'Pèlerinages & retraites', '#2F7D57'),
    ('formation', 'Formation & partage', '#B4532F'),
    ('jeunes', 'Jeunes & familles', '#B83E6E'),
    ('culture', 'Culture & patrimoine', '#4F5B6E'),
    ('fraternite', 'Fraternité & solidarité', '#1F7A80')]
FAMCOL = {k: c for k, _, c in FAMILIES}

# clé : (famille, libellé, nom Tabler, tracé)
ICONES = {
    'messe-dominicale': ('messes', 'Messe dominicale', 'building-church', '<path d="M3 21l18 0" /> <path d="M10 21v-4a2 2 0 0 1 4 0v4" /> <path d="M10 5l4 0" /> <path d="M12 3l0 5" /> <path d="M6 21v-7m-2 2l8 -8l8 8m-2 -2v7" />'),
    'messe-semaine': ('messes', 'Messe en semaine', 'glass-full', '<path d="M8 21l8 0" /> <path d="M12 15l0 6" /> <path d="M17 3l1 7c0 3.012 -2.686 5 -6 5s-6 -1.988 -6 -5l1 -7h10" /> <path d="M6 10a5 5 0 0 1 6 0a5 5 0 0 0 6 0" />'),
    'messe-anticipee': ('messes', 'Messe anticipée (samedi soir)', 'moon', '<path d="M12 3c.132 0 .263 0 .393 0a7.5 7.5 0 0 0 7.92 12.446a9 9 0 1 1 -8.313 -12.454l0 .008" />'),
    'messe-solennite': ('messes', 'Messe de fête / solennité', 'star', '<path d="M12 17.75l-6.172 3.245l1.179 -6.873l-5 -4.867l6.9 -1l3.086 -6.253l3.086 6.253l6.9 1l-5 4.867l1.179 6.873l-6.158 -3.245" />'),
    'messe-familles': ('messes', 'Messe des familles / des jeunes', 'friends', '<path d="M5 5a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" /> <path d="M5 22v-5l-1 -1v-4a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v4l-1 1v5" /> <path d="M15 5a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" /> <path d="M15 22v-4h-2l2 -6a1 1 0 0 1 1 -1h2a1 1 0 0 1 1 1l2 6h-2v4" />'),
    'messe-latin': ('messes', 'Messe en latin', 'language', '<path d="M9 6.371c0 4.418 -2.239 6.629 -5 6.629" /> <path d="M4 6.371h7" /> <path d="M5 9c0 2.144 2.252 3.908 6 4" /> <path d="M12 20l4 -9l4 9" /> <path d="M19.1 18h-6.2" /> <path d="M6.694 3l.793 .582" />'),
    'laudes': ('messes', 'Laudes (prière du matin)', 'sunrise', '<path d="M3 17h1m16 0h1m-15.4 -6.4l.7 .7m12.1 -.7l-.7 .7m-9.7 5.7a4 4 0 0 1 8 0" /> <path d="M3 21l18 0" /> <path d="M12 9v-6l3 3m-6 0l3 -3" />'),
    'vepres': ('messes', 'Vêpres (prière du soir)', 'sunset', '<path d="M3 17h1m16 0h1m-15.4 -6.4l.7 .7m12.1 -.7l-.7 .7m-9.7 5.7a4 4 0 0 1 8 0" /> <path d="M3 21l18 0" /> <path d="M12 3v6l3 -3m-6 0l3 3" />'),
    'complies': ('messes', 'Complies (prière de la nuit)', 'moon-stars', '<path d="M12 3c.132 0 .263 0 .393 0a7.5 7.5 0 0 0 7.92 12.446a9 9 0 1 1 -8.313 -12.454l0 .008" /> <path d="M17 4a2 2 0 0 0 2 2a2 2 0 0 0 -2 2a2 2 0 0 0 -2 -2a2 2 0 0 0 2 -2" /> <path d="M19 11h2m-1 -1v2" />'),
    'celebration-parole': ('messes', 'Célébration de la Parole', 'bible', '<path d="M19 4v16h-12a2 2 0 0 1 -2 -2v-12a2 2 0 0 1 2 -2h12" /> <path d="M19 16h-12a2 2 0 0 0 -2 2" /> <path d="M12 7v6" /> <path d="M10 9h4" />'),
    'semaine-sainte': ('messes', 'Semaine sainte, Rameaux', 'leaf', '<path d="M5 21c.5 -4.5 2.5 -8 7 -10" /> <path d="M9 18c6.218 0 10.5 -3.288 11 -12v-2h-4.014c-9 0 -11.986 4 -12 9c0 1 0 3 2 5h3l.014 0" />'),
    'liturgie-orientale': ('messes', 'Liturgie orientale', 'building-arch', '<path d="M3 21l18 0" /> <path d="M4 21v-15a2 2 0 0 1 2 -2h12a2 2 0 0 1 2 2v15" /> <path d="M9 21v-8a3 3 0 0 1 6 0v8" />'),
    'confession': ('sacrements', 'Confession, réconciliation', 'key', '<path d="M16.555 3.843l3.602 3.602a2.877 2.877 0 0 1 0 4.069l-2.643 2.643a2.877 2.877 0 0 1 -4.069 0l-.301 -.301l-6.558 6.558a2 2 0 0 1 -1.239 .578l-.175 .008h-1.172a1 1 0 0 1 -.993 -.883l-.007 -.117v-1.172a2 2 0 0 1 .467 -1.284l.119 -.13l.414 -.414h2v-2h2v-2l2.144 -2.144l-.301 -.301a2.877 2.877 0 0 1 0 -4.069l2.643 -2.643a2.877 2.877 0 0 1 4.069 0" /> <path d="M15 9h.01" />'),
    'bapteme': ('sacrements', 'Baptême', 'droplet', '<path d="M7.502 19.423c2.602 2.105 6.395 2.105 8.996 0c2.602 -2.105 3.262 -5.708 1.566 -8.546l-4.89 -7.26c-.42 -.625 -1.287 -.803 -1.936 -.397a1.376 1.376 0 0 0 -.41 .397l-4.893 7.26c-1.695 2.838 -1.035 6.441 1.567 8.546" />'),
    'confirmation': ('sacrements', 'Confirmation', 'flame', '<path d="M12 10.941c2.333 -3.308 .167 -7.823 -1 -8.941c0 3.395 -2.235 5.299 -3.667 6.706c-1.43 1.408 -2.333 3.294 -2.333 5.588c0 3.704 3.134 6.706 7 6.706c3.866 0 7 -3.002 7 -6.706c0 -1.712 -1.232 -4.403 -2.333 -5.588c-2.084 3.353 -3.257 3.353 -4.667 2.235" />'),
    'premiere-communion': ('sacrements', 'Première communion', 'bread', '<path d="M18 4a3 3 0 0 1 2 5.235v8.765a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2v-8.764a3 3 0 0 1 1.824 -5.231h12.176v-.005" />'),
    'mariage': ('sacrements', 'Mariage, préparation au mariage', 'hearts', '<path d="M14.017 18l-2.017 2l-7.5 -7.428a5 5 0 1 1 7.5 -6.566a5 5 0 0 1 8.153 5.784" /> <path d="M15.99 20l4.197 -4.223a2.81 2.81 0 0 0 0 -3.948a2.747 2.747 0 0 0 -3.91 -.007l-.28 .282l-.279 -.283a2.747 2.747 0 0 0 -3.91 -.007a2.81 2.81 0 0 0 -.007 3.948l4.182 4.238l.007 0" />'),
    'ordination': ('sacrements', 'Ordination, vœux religieux', 'user-check', '<path d="M8 7a4 4 0 1 0 8 0a4 4 0 0 0 -8 0" /> <path d="M6 21v-2a4 4 0 0 1 4 -4h4" /> <path d="M15 19l2 2l4 -4" />'),
    'onction-malades': ('sacrements', 'Sacrement des malades', 'bottle', '<path d="M10 5h4v-2a1 1 0 0 0 -1 -1h-2a1 1 0 0 0 -1 1v2" /> <path d="M14 3.5c0 1.626 .507 3.212 1.45 4.537l.05 .07a8.093 8.093 0 0 1 1.5 4.694v6.199a2 2 0 0 1 -2 2h-6a2 2 0 0 1 -2 -2v-6.2c0 -1.682 .524 -3.322 1.5 -4.693l.05 -.07a7.823 7.823 0 0 0 1.45 -4.537" /> <path d="M7 14.803a2.4 2.4 0 0 0 1 -.803a2.4 2.4 0 0 1 2 -1a2.4 2.4 0 0 1 2 1a2.4 2.4 0 0 0 2 1a2.4 2.4 0 0 0 2 -1a2.4 2.4 0 0 1 1 -.805" />'),
    'adoration': ('priere', 'Adoration eucharistique', 'sun', '<path d="M8 12a4 4 0 1 0 8 0a4 4 0 1 0 -8 0" /> <path d="M3 12h1m8 -9v1m8 8h1m-9 8v1m-6.4 -15.4l.7 .7m12.1 -.7l-.7 .7m0 11.4l.7 .7m-12.1 -.7l-.7 .7" />'),
    'louange': ('priere', 'Soirée de louange', 'pray', '<path d="M11 5a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" /> <path d="M7 20h8l-4 -4v-7l4 3l2 -2" />'),
    'chapelet': ('priere', 'Chapelet, rosaire', 'circle-dashed', '<path d="M8.56 3.69a9 9 0 0 0 -2.92 1.95" /> <path d="M3.69 8.56a9 9 0 0 0 -.69 3.44" /> <path d="M3.69 15.44a9 9 0 0 0 1.95 2.92" /> <path d="M8.56 20.31a9 9 0 0 0 3.44 .69" /> <path d="M15.44 20.31a9 9 0 0 0 2.92 -1.95" /> <path d="M20.31 15.44a9 9 0 0 0 .69 -3.44" /> <path d="M20.31 8.56a9 9 0 0 0 -1.95 -2.92" /> <path d="M15.44 3.69a9 9 0 0 0 -3.44 -.69" />'),
    'chemin-de-croix': ('priere', 'Chemin de croix', 'cross', '<path d="M10 21h4v-9h5v-4h-5v-5h-4v5h-5v4h5l0 9" />'),
    'veillee': ('priere', 'Veillée de prière', 'candle', '<path d="M9 21h6v-10a1 1 0 0 0 -1 -1h-4a1 1 0 0 0 -1 1l0 10" /> <path d="M12 2l1.465 1.638a2 2 0 1 1 -3.015 .099l1.55 -1.737" />'),
    'neuvaine': ('priere', 'Neuvaine', 'calendar-week', '<path d="M4 7a2 2 0 0 1 2 -2h12a2 2 0 0 1 2 2v12a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2v-12" /> <path d="M16 3v4" /> <path d="M8 3v4" /> <path d="M4 11h16" /> <path d="M7 14h.013" /> <path d="M10.01 14h.005" /> <path d="M13.01 14h.005" /> <path d="M16.015 14h.005" /> <path d="M13.015 17h.005" /> <path d="M7.01 17h.005" /> <path d="M10.01 17h.005" />'),
    'procession': ('priere', 'Procession', 'flag', '<path d="M5 5a5 5 0 0 1 7 0a5 5 0 0 0 7 0v9a5 5 0 0 1 -7 0a5 5 0 0 0 -7 0v-9" /> <path d="M5 21v-7" />'),
    'benediction': ('priere', 'Bénédiction', 'sparkles', '<path d="M16 18a2 2 0 0 1 2 2a2 2 0 0 1 2 -2a2 2 0 0 1 -2 -2a2 2 0 0 1 -2 2m0 -12a2 2 0 0 1 2 2a2 2 0 0 1 2 -2a2 2 0 0 1 -2 -2a2 2 0 0 1 -2 2m-7 12a6 6 0 0 1 6 -6a6 6 0 0 1 -6 -6a6 6 0 0 1 -6 6a6 6 0 0 1 6 6" />'),
    'pelerinage': ('pelerinages', 'Pèlerinage', 'trekking', '<path d="M11 4a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" /> <path d="M7 21l2 -4" /> <path d="M13 21v-4l-3 -3l1 -6l3 4l3 2" /> <path d="M10 14l-1.827 -1.218a2 2 0 0 1 -.831 -2.15l.28 -1.117a2 2 0 0 1 1.939 -1.515h1.439l4 1l3 -2" /> <path d="M17 12v9" /> <path d="M16 20h2" />'),
    'marche': ('pelerinages', 'Marche, randonnée spirituelle', 'mountain', '<path d="M3 20h18l-6.921 -14.612a2.3 2.3 0 0 0 -4.158 0l-6.921 14.612" /> <path d="M7.5 11l2 2.5l2.5 -2.5l2 3l2.5 -2" />'),
    'sanctuaire-marial': ('pelerinages', 'Sanctuaire, journée mariale', 'crown', '<path d="M12 6l4 6l5 -4l-2 10h-14l-2 -10l5 4l4 -6" />'),
    'retraite': ('pelerinages', 'Retraite, récollection', 'building-cottage', '<path d="M3 21l18 0" /> <path d="M4 21v-11l2.5 -4.5l5.5 -2.5l5.5 2.5l2.5 4.5v11" /> <path d="M10 9a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" /> <path d="M9 21v-5a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v5" />'),
    'session': ('pelerinages', 'Session, camp spirituel', 'tent', '<path d="M11 14l4 6h6l-9 -16l-9 16h6l4 -6" />'),
    'conference': ('formation', 'Conférence', 'presentation', '<path d="M3 4l18 0" /> <path d="M4 4v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2 -2v-10" /> <path d="M12 16l0 4" /> <path d="M9 20l6 0" /> <path d="M8 12l3 -3l2 2l3 -3" />'),
    'debat': ('formation', 'Débat, table ronde', 'messages', '<path d="M21 14l-3 -3h-7a1 1 0 0 1 -1 -1v-6a1 1 0 0 1 1 -1h9a1 1 0 0 1 1 1v10" /> <path d="M14 15v2a1 1 0 0 1 -1 1h-7l-3 3v-10a1 1 0 0 1 1 -1h2" />'),
    'groupe-biblique': ('formation', 'Groupe biblique, lectio divina', 'book', '<path d="M3 19a9 9 0 0 1 9 0a9 9 0 0 1 9 0" /> <path d="M3 6a9 9 0 0 1 9 0a9 9 0 0 1 9 0" /> <path d="M3 6l0 13" /> <path d="M12 6l0 13" /> <path d="M21 6l0 13" />'),
    'catechese': ('formation', 'Catéchèse, catéchuménat', 'school', '<path d="M22 9l-10 -4l-10 4l10 4l10 -4v6" /> <path d="M6 10.6v5.4a6 3 0 0 0 12 0v-5.4" />'),
    'cine-debat': ('formation', 'Ciné-débat', 'movie', '<path d="M4 6a2 2 0 0 1 2 -2h12a2 2 0 0 1 2 2v12a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2l0 -12" /> <path d="M8 4l0 16" /> <path d="M16 4l0 16" /> <path d="M4 8l4 0" /> <path d="M4 16l4 0" /> <path d="M4 12l16 0" /> <path d="M16 8l4 0" /> <path d="M16 16l4 0" />'),
    'lecture': ('formation', 'Lecture, librairie', 'books', '<path d="M5 5a1 1 0 0 1 1 -1h2a1 1 0 0 1 1 1v14a1 1 0 0 1 -1 1h-2a1 1 0 0 1 -1 -1l0 -14" /> <path d="M9 5a1 1 0 0 1 1 -1h2a1 1 0 0 1 1 1v14a1 1 0 0 1 -1 1h-2a1 1 0 0 1 -1 -1l0 -14" /> <path d="M5 8h4" /> <path d="M9 16h4" /> <path d="M13.803 4.56l2.184 -.53c.562 -.135 1.133 .19 1.282 .732l3.695 13.418a1.02 1.02 0 0 1 -.634 1.219l-.133 .041l-2.184 .53c-.562 .135 -1.133 -.19 -1.282 -.732l-3.695 -13.418a1.02 1.02 0 0 1 .634 -1.219l.133 -.041" /> <path d="M14 9l4 -1" /> <path d="M16 16l3.923 -.98" />'),
    'parcours-decouverte': ('formation', 'Parcours découverte (Alpha…)', 'compass', '<path d="M8 16l2 -6l6 -2l-2 6l-6 2" /> <path d="M3 12a9 9 0 1 0 18 0a9 9 0 1 0 -18 0" /> <path d="M12 3l0 2" /> <path d="M12 19l0 2" /> <path d="M3 12l2 0" /> <path d="M19 12l2 0" />'),
    'soiree-jeunes': ('jeunes', 'Soirée jeunes, aumônerie', 'users', '<path d="M5 7a4 4 0 1 0 8 0a4 4 0 1 0 -8 0" /> <path d="M3 21v-2a4 4 0 0 1 4 -4h4a4 4 0 0 1 4 4v2" /> <path d="M16 3.13a4 4 0 0 1 0 7.75" /> <path d="M21 21v-2a4 4 0 0 0 -3 -3.85" />'),
    'eveil-foi': ('jeunes', 'Éveil à la foi, enfants', 'mood-kid', '<path d="M3 12a9 9 0 1 0 18 0a9 9 0 1 0 -18 0" /> <path d="M9 10l.01 0" /> <path d="M15 10l.01 0" /> <path d="M9.5 15a3.5 3.5 0 0 0 5 0" /> <path d="M12 3a2 2 0 0 0 0 4" />'),
    'familles': ('jeunes', 'Familles', 'home-heart', '<path d="M21 12l-9 -9l-9 9h2v7a2 2 0 0 0 2 2h6" /> <path d="M9 21v-6a2 2 0 0 1 2 -2h2c.39 0 .754 .112 1.061 .304" /> <path d="M19 21.5l2.518 -2.58a1.74 1.74 0 0 0 0 -2.413a1.627 1.627 0 0 0 -2.346 0l-.168 .172l-.168 -.172a1.627 1.627 0 0 0 -2.346 0a1.74 1.74 0 0 0 0 2.412l2.51 2.59l0 -.009" />'),
    'rassemblement': ('jeunes', 'Grand rassemblement, JMJ', 'users-group', '<path d="M10 13a2 2 0 1 0 4 0a2 2 0 0 0 -4 0" /> <path d="M8 21v-1a2 2 0 0 1 2 -2h4a2 2 0 0 1 2 2v1" /> <path d="M15 5a2 2 0 1 0 4 0a2 2 0 0 0 -4 0" /> <path d="M17 10h2a2 2 0 0 1 2 2v1" /> <path d="M5 5a2 2 0 1 0 4 0a2 2 0 0 0 -4 0" /> <path d="M3 13v-1a2 2 0 0 1 2 -2h2" />'),
    'scouts-camps': ('jeunes', 'Scouts, camps', 'campfire', '<path d="M4 21l16 -4" /> <path d="M20 21l-16 -4" /> <path d="M12 15a4 4 0 0 0 4 -4c0 -3 -2 -3 -2 -8c-4 2 -6 5 -6 8a4 4 0 0 0 4 4" />'),
    'concert': ('culture', 'Concert sacré, orgue', 'music', '<path d="M3 17a3 3 0 1 0 6 0a3 3 0 0 0 -6 0" /> <path d="M13 17a3 3 0 1 0 6 0a3 3 0 0 0 -6 0" /> <path d="M9 17v-13h10v13" /> <path d="M9 8h10" />'),
    'visite-eglise': ('culture', "Visite d'église, patrimoine", 'building-monument', '<path d="M8 18l2 -13l2 -2l2 2l2 13" /> <path d="M5 21v-3h14v3" /> <path d="M3 21l18 0" />'),
    'exposition': ('culture', 'Exposition', 'photo', '<path d="M15 8h.01" /> <path d="M3 6a3 3 0 0 1 3 -3h12a3 3 0 0 1 3 3v12a3 3 0 0 1 -3 3h-12a3 3 0 0 1 -3 -3v-12" /> <path d="M3 16l5 -5c.928 -.893 2.072 -.893 3 0l5 5" /> <path d="M14 14l1 -1c.928 -.893 2.072 -.893 3 0l3 3" />'),
    'creche': ('culture', 'Crèche de Noël', 'christmas-tree', '<path d="M12 3l4 4l-2 1l4 4l-3 1l4 4h-14l4 -4l-3 -1l4 -4l-2 -1l4 -4" /> <path d="M14 17v3a1 1 0 0 1 -1 1h-2a1 1 0 0 1 -1 -1v-3" />'),
    'repas': ('fraternite', 'Repas, fête paroissiale', 'tools-kitchen-2', '<path d="M19 3v12h-5c-.023 -3.681 .184 -7.406 5 -12m0 12v6h-1v-3m-10 -14v17m-3 -17v3a3 3 0 1 0 6 0v-3" />'),
    'kermesse': ('fraternite', 'Kermesse, fête', 'confetti', '<path d="M4 5h2" /> <path d="M5 4v2" /> <path d="M11.5 4l-.5 2" /> <path d="M18 5h2" /> <path d="M19 4v2" /> <path d="M15 9l-1 1" /> <path d="M18 13l2 -.5" /> <path d="M18 19h2" /> <path d="M19 18v2" /> <path d="M14 16.518l-6.518 -6.518l-4.39 9.58a1 1 0 0 0 1.329 1.329l9.579 -4.39" />'),
    'brocante': ('fraternite', 'Brocante, vide-grenier', 'tag', '<path d="M6.5 7.5a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" /> <path d="M3 6v5.172a2 2 0 0 0 .586 1.414l7.71 7.71a2.41 2.41 0 0 0 3.408 0l5.592 -5.592a2.41 2.41 0 0 0 0 -3.408l-7.71 -7.71a2 2 0 0 0 -1.414 -.586h-5.172a3 3 0 0 0 -3 3" />'),
    'solidarite': ('fraternite', 'Solidarité, maraude', 'heart-handshake', '<path d="M19.5 12.572l-7.5 7.428l-7.5 -7.428a5 5 0 1 1 7.5 -6.566a5 5 0 1 1 7.5 6.572" /> <path d="M12 6l-3.293 3.293a1 1 0 0 0 0 1.414l.543 .543c.69 .69 1.81 .69 2.5 0l1 -1a3.182 3.182 0 0 1 4.5 0l2.25 2.25" /> <path d="M12.5 15.5l2 2" /> <path d="M15 13l2 2" />'),
    'mission': ('fraternite', 'Mission, évangélisation', 'speakerphone', '<path d="M18 8a3 3 0 0 1 0 6" /> <path d="M10 8v11a1 1 0 0 1 -1 1h-1a1 1 0 0 1 -1 -1v-5" /> <path d="M12 8l4.524 -3.77a.9 .9 0 0 1 1.476 .692v12.156a.9 .9 0 0 1 -1.476 .692l-4.524 -3.77h-8a1 1 0 0 1 -1 -1v-4a1 1 0 0 1 1 -1h8" />'),
}
ICONS = list(ICONES)
F = {k: v[0] for k, v in ICONES.items()}
LABEL = {k: v[1] for k, v in ICONES.items()}
TABLER = {k: v[2] for k, v in ICONES.items()}

def glyph(key, color, sw=2):
    return (f'<g fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">'
            + ICONES[key][3] + "</g>")

SQ = "M32 0C52.5 0 64 4.6 64 32S52.5 64 32 64 0 59.4 0 32 11.5 0 32 0Z"

def pastille(key, size=None, aria=True):
    col = FAMCOL[F[key]]
    a = f'role="img" aria-label="{LABEL[key]}"' if aria else 'aria-hidden="true"'
    sz = f' width="{size}" height="{size}"' if size else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"{sz} {a}><path d="{SQ}" fill="{col}"/>'
            f'<g transform="translate(14 14) scale(1.5)">{glyph(key, "#FFFFFF", 2)}</g></svg>')

def trait(key, color="#141A33", size=None, aria=True):
    a = f'role="img" aria-label="{LABEL[key]}"' if aria else 'aria-hidden="true"'
    sz = f' width="{size}" height="{size}"' if size else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"{sz} {a}>{glyph(key, color, 2)}</svg>'

LOGO_ICON = '<defs><linearGradient id="tdc-or" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E2B94E"/><stop offset="1" stop-color="#B8862B"/></linearGradient></defs><path d="M32 0C52.5 0 64 4.6 64 32S52.5 64 32 64 0 59.4 0 32 11.5 0 32 0Z" fill="url(#tdc-or)"/><path d="M29.5 13.5V38c0 7.5 4.2 12 11.6 12h2.4" fill="none" stroke="#FFFFFF" stroke-width="6.4" stroke-linecap="round" stroke-linejoin="round"/><path d="M17.5 27.6 24.6 34C31.5 26.9 38 22.2 46.4 18.6" fill="none" stroke="#FFFFFF" stroke-width="6.4" stroke-linecap="round" stroke-linejoin="round"/><circle cx="48.6" cy="46.4" r="5.6" fill="#FFFFFF"/><circle cx="48.6" cy="46.4" r="4.3" fill="#2F6DB5"/>'  # fond or (dégradé), t coché blanc, point bleu marial cerclé de blanc

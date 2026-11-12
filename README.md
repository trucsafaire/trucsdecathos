# Trucs de cathos

Messes, veillées, pèlerinages, conférences, soirées jeunes : les événements catholiques près de chez vous, sur liste et sur carte.
Déclinaison catholique de [Trucs à faire](https://trucsafaire.fr/), même éditeur (Saryn Digital), **même compte**.
Charte graphique : bleu marial #2F6DB5, blanc ivoire, or #E8BE55 ; polices Outfit et DM Sans ; 53 pictogrammes en 8 familles.

## Organisation

```
index.html             l'appli (liste, carte, détail, favoris, compte, proposer un événement)
admin.html             espace éditeur : valider, corriger, refuser, retirer (code éditeur de Trucs à faire)
config.js              adresse du serveur commun (api.trucsafaire.fr)
data/types.json        familles et pictogrammes   ← python scripts/construire_types.py
data/evenements.json   événements des agendas diocésains   ← python scripts/dioceses.py (chaque lundi, GitHub Actions)
data/dioceses.json     les 98 diocèses (métropole, outre-mer, Armées) : site, siège, départements
data/messes/<dep>.json horaires des messes Messes Info      ← python scripts/messesinfo.py (chaque lundi, clé secrète)
data/communes-fr.json  communes (copie de Trucs à faire)
marque/                logos et pictogrammes (pastilles SVG)
scripts/pictos.py      dessin des pictogrammes (source unique)
vendor/                MapLibre 4.7.1 (hébergé avec le site)
```

## Fonctionnement

- **Compte commun** : la connexion envoie `site: "cathos"` au serveur de Trucs à faire ; le lien arrive sur trucsdecathos.fr.
  Un compte Trucs à faire marche ici, et inversement. Préférences et favoris de chaque site restent séparés.
  Une case à cocher recueille l'accord exprès (donnée sensible, art. 9 RGPD) avant toute connexion.
- **Événements** : `GET /cathos/agenda` (publiés après relecture) + `data/evenements.json`.
- **Horaires des messes** : relevés chaque semaine sur Messes Info (`data/messes/<département>.json`). L'appli montre les prochaines messes
  autour de la commune choisie, et toutes les messes et offices avec le filtre « Messes & offices ». Lien « Tous les horaires » vers Messes Info.
- **Démonstration** : `#demo` à la fin de l'adresse affiche des événements fictifs, marqués « Exemple ».

## Agendas des diocèses

`scripts/dioceses.py` lit chaque semaine les agendas publics de **tous les diocèses** listés dans `data/dioceses.json`
(bibliothèque standard Python ; une page à la fois et au plus une par seconde pour chaque site ; plusieurs sites en parallèle).

- **Adaptateurs écrits à la main** (plus précis) : Moulins (Modern Events Calendar), Nevers (API WordPress « agenda »), Autun (Event Booking).
- **Adaptateur générique** pour les autres, dans cet ordre :
  1. API REST de *The Events Calendar* (`/wp-json/tribe/events/v1/events`) : dates, lieu, commune déjà structurés ;
  2. sinon les plans du site consacrés aux événements (Yoast, Rank Math, WordPress), pages les plus récemment modifiées d'abord
     (`MAX_PAGES`, 150 par défaut), puis chaque page lue par : JSON-LD schema.org/Event, thème commun des sites « catholique.fr »,
     Modern Events Calendar, Events Manager, puis repérage générique d'un bloc « date » et d'un bloc « lieu ».
- Une page déjà lue dont la date de modification n'a pas changé n'est pas relue (`.cache/`, conservé par `actions/cache`, hors dépôt).

Un événement n'est gardé que s'il est à venir, ouvert au public (conseils, commissions, réunions internes écartés), classé dans un des 53 types
par mots-clés, et placé dans une commune des départements du diocèse (« Maison du diocèse », « Cathédrale » : ville du siège ;
un lieu hors du diocèse, « Lourdes », « Pontorson (50) », est écarté). Le journal de chaque passage dit ce qui a été écarté et pourquoi ;
`data/dioceses-bilan.json` donne le nombre d'événements par diocèse. Une source en panne garde ses anciens événements.
Les sites sans agenda lisible automatiquement (pas de plan du site, agenda en image ou dans un autre outil) restent à 0 :
un adaptateur dédié peut leur être ajouté dans `DEDIES`. `scripts/sonder.py` refait l'inventaire technique des sites.

## Horaires des messes (Messes Info)

`scripts/messesinfo.py` relève chaque semaine, département par département, les horaires des 15 jours à venir sur l'API v2 de Messes Info
(Conférence des évêques de France) : paroisses du département (`/department/{n}`), puis leurs horaires (`/horaires/community:{id} …`).
La clé d'API (« userkey ») se demande à **contact.messesinfo@cef.fr** ; elle se range dans le secret GitHub `MESSESINFO_KEY`
(Settings → Secrets and variables → Actions) et n'apparaît jamais dans le dépôt ni dans le navigateur. Sans clé, l'étape ne fait rien
et l'appli garde le lien vers Messes Info. Les horaires restent ceux saisis par les paroisses : la source est citée sous la liste.

## Mise en ligne

1. Appliquer le correctif serveur dans le dépôt Trucs à faire (`0001-Compte-commun…patch`), pousser : le Worker se redéploie seul.
2. Créer le dépôt `trucsafaire/trucsdecathos`, y pousser ce dossier, activer GitHub Pages (branche `main`, racine).
3. Acheter `trucsdecathos.fr`, le brancher sur Cloudflare, puis DNS vers GitHub Pages (le fichier `CNAME` est déjà là).
4. Adresses (Cloudflare → Email → Email Routing, gratuit, comme pour trucsafaire.fr) : `contact@trucsdecathos.fr` (affichée dans les
   mentions légales et la confidentialité) redirigée vers la boîte personnelle, `bonjour@` redirigée vers `contact@`.
   Pour **écrire** depuis `contact@` (demande de clé Messes Info…) : dans la messagerie, ajouter l'adresse d'envoi
   `contact@trucsdecathos.fr` avec le serveur SMTP de Brevo (domaine vérifié chez Brevo, enregistrements SPF/DKIM ajoutés dans Cloudflare).
5. Facultatif : ajouter `MAIL_FROM_CATHOS = "bonjour@trucsdecathos.fr"` dans `wrangler.toml` pour les liens de connexion.

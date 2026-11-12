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
- **Horaires des messes** : lien vers Messes Info (recherche par position), qui reste la référence tenue par les paroisses.
- **Démonstration** : `#demo` à la fin de l'adresse affiche des événements fictifs, marqués « Exemple ».

## Agendas des diocèses

`scripts/dioceses.py` lit chaque semaine les agendas publics des diocèses (bibliothèque standard Python, une page par seconde) :

| Diocèse | Site | Méthode |
|---|---|---|
| Moulins (03) | catholique-moulins.fr | plan du site des événements (Modern Events Calendar), puis chaque page |
| Nevers (58) | nievre.catholique.fr | API WordPress du type « agenda », puis chaque page (date sans année : prochaine occurrence) |
| Autun (71) | autun.catholique.fr | liste « événements à venir » (Event Booking), puis chaque page pour le lieu |

Un événement n'est gardé que s'il est à venir, ouvert au public (conseils, commissions, réunions internes écartés), classé dans un des 53 types
par mots-clés, et placé dans une commune du département (« Maison du diocèse », « Cathédrale » : ville du siège). Le journal de chaque passage
dit ce qui a été écarté et pourquoi. Une source en panne garde ses anciens événements. Ajouter un diocèse = écrire un adaptateur et l'ajouter à `SOURCES`.

## Mise en ligne

1. Appliquer le correctif serveur dans le dépôt Trucs à faire (`0001-Compte-commun…patch`), pousser : le Worker se redéploie seul.
2. Créer le dépôt `trucsafaire/trucsdecathos`, y pousser ce dossier, activer GitHub Pages (branche `main`, racine).
3. Acheter `trucsdecathos.fr`, le brancher sur Cloudflare, puis DNS vers GitHub Pages (le fichier `CNAME` est déjà là).
4. Facultatif : vérifier `trucsdecathos.fr` chez Brevo et ajouter `MAIL_FROM_CATHOS = "bonjour@trucsdecathos.fr"` dans `wrangler.toml`.

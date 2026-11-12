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
data/evenements.json   événements fixes (vide pour l'instant ; les scripts des agendas diocésains écriront ici)
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
- **Temps liturgique** : calculé dans la page (date de Pâques, Avent, Carême…), affiché en signet.
- **Démonstration** : `#demo` à la fin de l'adresse affiche des événements fictifs, marqués « Exemple ».

## Mise en ligne

1. Appliquer le correctif serveur dans le dépôt Trucs à faire (`0001-Compte-commun…patch`), pousser : le Worker se redéploie seul.
2. Créer le dépôt `trucsafaire/trucsdecathos`, y pousser ce dossier, activer GitHub Pages (branche `main`, racine).
3. Acheter `trucsdecathos.fr`, le brancher sur Cloudflare, puis DNS vers GitHub Pages (le fichier `CNAME` est déjà là).
4. Facultatif : vérifier `trucsdecathos.fr` chez Brevo et ajouter `MAIL_FROM_CATHOS = "bonjour@trucsdecathos.fr"` dans `wrangler.toml`.

/* Réglages du site Trucs de cathos.
   apiUrl : le serveur commun à Trucs à faire (comptes, agenda catholique, propositions).
   Les comptes sont partagés : un compte Trucs à faire fonctionne ici, et inversement. */
window.TDC_CONFIG = Object.assign({
  apiUrl: "https://api.trucsafaire.fr",
  /* Adresse de Trucs à faire (lien « Mes autres trucs ») */
  tafUrl: "https://trucsafaire.fr/"
}, window.TDC_CONFIG || {});

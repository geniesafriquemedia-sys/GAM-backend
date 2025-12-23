# User Stories – GAM (Génies Afrique Médias)

**Version :** V1 (MVP)  
**Format :** Markdown (.md)  
**Objectif :** Définir clairement le backlog fonctionnel de la version 1 de la plateforme GAM.

---

## EPIC 1 – Gestion Éditoriale (Back-Office / Wagtail)

**Cibles :** Administrateur, Rédacteur en chef, Rédacteur

---

### US-01 – Gestion des taxonomies (Auteurs & Catégories)

**En tant que** Administrateur  
**Je veux** créer, modifier et supprimer des auteurs et des catégories  
**Afin de** structurer les contenus et attribuer correctement les articles.

**Critères d’acceptation :**
- Ajout d’une photo et d’une biographie pour chaque auteur
- Définition d’une couleur (code hexadécimal) pour chaque catégorie
- Gestion via le système de *Snippets* de Wagtail

---

### US-02 – Rédaction d’un article riche (StreamField)

**En tant que** Rédacteur  
**Je veux** composer un article à l’aide de blocs dynamiques  
**Afin de** créer une mise en page riche sans utiliser le HTML.

**Critères d’acceptation :**
- Insertion de blocs : texte, image, citation, vidéo, tweet
- Possibilité de prévisualiser l’article
- Calcul automatique du temps de lecture

---

### US-03 – Gestion des vidéos (Web TV)

**En tant que** Rédacteur  
**Je veux** publier une vidéo via une URL YouTube  
**Afin de** diffuser facilement du contenu vidéo sur GAM.

**Critères d’acceptation :**
- Champ acceptant une URL YouTube valide
- Récupération automatique de la miniature
- Titre et description personnalisables
- Possibilité de marquer une vidéo comme « En vedette »

---

### US-04 – Workflow de publication

**En tant que** Rédacteur en chef  
**Je veux** gérer le statut des contenus  
**Afin de** contrôler leur publication.

**Critères d’acceptation :**
- Statuts : Brouillon / Publié
- Un contenu brouillon n’est pas visible publiquement
- Possibilité de planifier une date de publication future

---

## EPIC 2 – Expérience Lecteur (Front-Office / Next.js)

**Cible :** Visiteur (Desktop & Mobile)

---

### US-05 – Page d’accueil dynamique

**En tant que** Visiteur  
**Je veux** voir immédiatement les contenus importants  
**Afin de** comprendre les sujets majeurs du moment.

**Critères d’acceptation :**
- Section « À la Une » avec 1 à 3 articles majeurs
- Fil d’actualité récent
- Blocs thématiques par catégorie
- Chargement rapide via SSR (Next.js)

---

### US-06 – Lecture d’un article

**En tant que** Visiteur  
**Je veux** lire un article dans un confort optimal  
**Afin de** rester concentré sur le contenu.

**Critères d’acceptation :**
- Affichage de l’auteur et du temps de lecture
- Design totalement responsive
- Images optimisées en WebP
- Section « Articles recommandés » en bas de page

---

### US-07 – Consultation Web TV

**En tant que** Visiteur  
**Je veux** regarder les vidéos directement sur GAM  
**Afin de** ne pas être redirigé vers YouTube.

**Critères d’acceptation :**
- Lecteur vidéo intégré proprement
- Filtrage des vidéos par catégories (Émissions, Reportages)

---

### US-08 – Recherche de contenu

**En tant que** Visiteur  
**Je veux** rechercher un contenu par mot-clé  
**Afin de** retrouver rapidement une information.

**Critères d’acceptation :**
- Recherche dans titres, descriptions et contenus
- Résultats paginés

---

## EPIC 3 – Engagement & Social

**Cible :** Visiteur

---

### US-09 – Partage social

**En tant que** Visiteur  
**Je veux** partager un article sur les réseaux sociaux  
**Afin de** le diffuser à mon réseau.

**Critères d’acceptation :**
- Boutons de partage (WhatsApp, LinkedIn, X)
- Métadonnées OpenGraph correctes (image, titre)

---

### US-10 – Inscription à la newsletter

**En tant que** Visiteur  
**Je veux** m’inscrire à la newsletter  
**Afin de** recevoir les actualités de GAM.

**Critères d’acceptation :**
- Validation du format email
- Envoi vers Mailchimp ou Brevo via API
- Message de confirmation sans rechargement

---

## EPIC 4 – Performance & SEO (Non fonctionnel)

**Cible :** Système / Moteurs de recherche

---

### US-11 – SEO technique

**En tant que** Moteur de recherche (Google)  
**Je veux** accéder au HTML complet dès le chargement  
**Afin de** indexer correctement les pages.

**Critères d’acceptation :**
- Server Side Rendering (Next.js)
- Sitemap.xml généré automatiquement
- Balises Title et Meta Description uniques

---

### US-12 – Performance mobile

**En tant que** Visiteur avec connexion mobile  
**Je veux** que le site se charge rapidement  
**Afin de** ne pas perdre de temps ni de données.

**Critères d’acceptation :**
- Temps de chargement < 3 secondes
- Score Lighthouse Performance > 80
- Mise en cache via Redis

---

📌 **Conclusion**  
Ce fichier Markdown constitue le **backlog officiel de la version 1 (MVP) de GAM**. Il est directement exploitable pour Jira, GitHub Projects, Trello ou toute organisation
# CAHIER DES CHARGES TECHNIQUE & FONCTIONNEL

**Projet :** GAM – Génies Afrique Médias  
**Date :** 18 décembre 2025  
**Version :** 2.0 (Révisée pour production)

---

## 1. Présentation du projet

### 1.1 Contexte
AFRITECK INSTITUT lance **GAM (Génies Afrique Médias)**, un média digital indépendant.  
Le projet consiste à développer une plateforme web performante, capable de diffuser des articles de presse et des contenus vidéo, tout en assurant une expérience utilisateur fluide, notamment sur mobile.

### 1.2 Vision du projet
GAM se positionne comme une **Web TV et un média numérique de référence en Afrique**, mettant en avant les talents, l’innovation et les initiatives à impact positif.

Le site ne sera pas un simple site vitrine, mais une **Application Web Progressive (PWA)** reposant sur une architecture moderne *Headless* :

- **Backend robuste** : gestion éditoriale structurée et sécurisée.
- **Frontend réactif** : navigation fluide, proche d’une application mobile.

---

## 2. Identité et ligne éditoriale de GAM

### 2.1 Identité du média
- **Nom du site :** GAM – Génies Afrique Médias
- **Slogan officiel :** *« Révéler les talents, informer l’Afrique »*

### 2.2 Mission
Valoriser l’innovation, l’éducation, la culture et les talents africains à travers des articles de fond, des interviews et des reportages vidéo.

### 2.3 Vision éditoriale
GAM ambitionne de devenir un média crédible, moderne et inspirant, capable de :
- Donner la parole aux acteurs du changement en Afrique
- Informer avec rigueur et pédagogie
- Inspirer la jeunesse africaine

### 2.4 Charte éditoriale

**Types de contenus :**
- Articles d’actualité et d’analyse
- Portraits et interviews
- Reportages vidéo / Web TV
- Dossiers thématiques (Tech, Culture, Société, Éducation)

**Ton éditorial :**
- Professionnel et accessible
- Inspirant et positif
- Engagé mais neutre et factuel

**Valeurs :**
- Authenticité
- Crédibilité
- Innovation
- Excellence africaine

---

## 3. Périmètre du projet (Scope V1)

Cette version V1 se concentre sur le socle fondamental du média.

### Inclus dans la V1
- Développement d’un CMS sur mesure (articles, auteurs, catégories)
- Interface publique responsive et optimisée SEO
- Lecteur vidéo intégré (sources externes)
- Moteur de recherche interne

### Exclus de la V1
- Hébergement et streaming vidéo en direct (YouTube Live recommandé)
- Système de paiement ou d’abonnement
- Applications mobiles natives (iOS / Android)

---

## 4. Architecture technique

### Stack retenue

**Backend (API & Administration)**
- Django + Wagtail CMS
- Interface d’administration avancée pour journalistes

**Frontend (Interface utilisateur)**
- React.js via Next.js
- Server Side Rendering (SSR) pour Google News et SEO

**Base de données**
- PostgreSQL

**Hébergement vidéo**
- YouTube (chaîne officielle GAM)

---

## 5. Fonctionnalités détaillées

### 5.1 Back-office (Gestion éditoriale)
- Tableau de bord
- Éditeur riche (StreamField)
- Gestion avancée des médias
- Workflow de validation (Brouillon → Modération → Publié)

### 5.2 Front-office (Expérience lecteur)

**Page d’accueil**
- À la Une
- Fil d’actualité
- Blocs thématiques

**Page article**
- Temps de lecture estimé
- Partage social (WhatsApp, Facebook, LinkedIn, X)
- Articles recommandés

**Web TV / Vidéo**
- Intégration YouTube optimisée
- Organisation par playlists

### 5.3 Fonctionnalités transverses
- Newsletter (Mailchimp ou Brevo)
- Recherche instantanée
- SEO avancé (Sitemap, OpenGraph, Schema.org)

---

## 6. Exigences de performance et sécurité

### Performance
- Images optimisées (WebP)
- Cache serveur (Redis)

### Sécurité
- HTTPS obligatoire
- Protection XSS / CSRF
- Accès back-office sécurisé

---

## 7. Planning prévisionnel

Durée estimée : **8 semaines**

1. Semaines 1–2 : Setup serveur & backend
2. Semaines 3–4 : Frontend & design
3. Semaines 5–6 : Connexion API & vidéos
4. Semaine 7 : SEO, tests et recette
5. Semaine 8 : Formation & mise en ligne

---

## 8. Budget estimatif

### Option A – Pack « Lancement Média »
- Django monolithique
- Budget : **450 000 – 600 000 FCFA**

### Option B – Pack « Digital Experience » (recommandé)
- Architecture Headless (Django + React)
- Budget : **900 000 – 1 500 000 FCFA**

---

## 9. Maintenance et hébergement

- Hébergement : à la charge du client (10 000 – 30 000 FCFA / mois)
- Maintenance : optionnelle (sécurité, sauvegardes, mises à jour)

---

*Document officiel – GAM (Génies Afrique Médias)*


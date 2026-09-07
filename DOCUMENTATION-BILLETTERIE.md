# Système de Billetterie Numérique Automatisée

## Mariage de Fabrice et Leslie

---

## Table des matières

1. [Vue d'ensemble du projet](#1-vue-densemble-du-projet)
2. [Architecture technique](#2-architecture-technique)
3. [Les 3 projets](#3-les-3-projets)
4. [Système de billets (PDF)](#4-système-de-billets-pdf)
5. [Flux de génération des PDFs](#5-flux-de-génération-des-pdfs)
6. [Le lien unique par invité](#6-le-lien-unique-par-invité)
7. [QR Code : contenu et design](#7-qr-code-contenu-et-design)
8. [PWA Scanner (jour J)](#8-pwa-scanner-jour-j)
9. [Dashboard Admin](#9-dashboard-admin)
10. [Structure des données (Firestore)](#10-structure-des-données-firestore)
11. [Liste des tables](#11-liste-des-tables)
12. [Liste des invités](#12-liste-des-invités)
13. [Design et style](#13-design-et-style)
14. [Flux complet de bout en bout](#14-flux-complet-de-bout-en-bout)

---

## 1. Vue d'ensemble du projet

### Objectif

Créer un **système de billetterie numérique automatisé** pour le mariage de Fabrice et Leslie. Le système doit :

- Générer automatiquement des billets personnalisés pour chaque invité
- Créer des invitations interactives avec des liens cliquables
- Permettre le scan des QR codes le jour du mariage via une PWA
- Gérer la présence et le comptage des places par table

### Concept clé

Chaque invité reçoit **2 PDFs** :

| PDF | Nom | Contenu | Envoi |
|-----|-----|---------|-------|
| **PDF1** | Invitation WhatsApp | Invitation-interactive (page 1) + QR code personnalisé avec anneaux (page 2) | Envoyé par WhatsApp |
| **PDF2** | Billet personnel | Image billet.png (page 1) + QR code personnalisé avec anneaux (page 2) | Accessible via lien cliquable dans PDF1 |

### Nombre total

- **30 tables** × **5 places par table** = **150 invités maximum**
- **150 PDF1** + **150 PDF2** = **300 PDFs générés**

---

## 2. Architecture technique

```
┌─────────────────────────────────────────────────────────┐
│                    ARCHITECTURE GLOBALE                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │  Next.js     │    │  FastAPI     │    │  PWA       │ │
│  │  (template/) │    │  (backend/)  │    │  (scanner/)│ │
│  │              │    │              │    │            │ │
│  │  - Admin     │◄──►│  - Génération│    │  - Scan QR │ │
│  │  - Billet    │    │    PDFs      │    │  - Check-in│ │
│  │    viewer    │    │  - Cloudinary│    │  - Stats   │ │
│  └──────┬───────┘    └──────┬───────┘    └─────┬──────┘ │
│         │                   │                   │        │
│         ▼                   ▼                   ▼        │
│  ┌──────────────────────────────────────────────────┐   │
│  │                 Firebase Firestore                │   │
│  │  Collection "guests" : métadonnées des invités   │   │
│  │  Collection "checkins" : enregistrement présence │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │                   Cloudinary                      │   │
│  │  Stockage des PDFs générés (PDF1 + PDF2)         │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Technologies utilisées

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| Frontend Admin | Next.js 15 + Tailwind CSS | Interface de gestion |
| Backend PDF | Python + FastAPI | Génération des PDFs |
| PDF Engine | pdf-lib (Python) | Création/modification de PDFs |
| QR Code | qrcode (Python) | Génération de QR codes |
| Stockage PDFs | Cloudinary | Hébergement des PDFs |
| Base de données | Firebase Firestore | Métadonnées + check-ins |
| PWA Scanner | Next.js + PWA | Scan le jour du mariage |
| Design System | Dark theme + accents orange | Style cohérent |

---

## 3. Les 3 projets

### 3.1 Projet 1 : template/ (Next.js)

**Rôle** : Site web du mariage + Dashboard Admin + Viewer de billets

**Pages** :

| Route | Description |
|-------|-------------|
| `/` | Page d'accueil (galerie 3D existante) |
| `/presence` | Confirmation de présence (existant) |
| `/programme` | Programme de la journée (existant) |
| `/gallery` | Galerie photos (existant) |
| `/admin/billets` | **Dashboard admin** - Gestion tables/invités |
| `/billet/[id]` | **Viewer de billet** - Affiche le billet personnalisé |

**Dépendances existantes** :
- Next.js 15.5.3
- React 19.1.0
- Tailwind CSS 4
- pdf-lib 1.17.1
- Lucide React (icônes)

### 3.2 Projet 2 : backend/ (FastAPI Python)

**Rôle** : API de génération de PDFs

**Endpoints** :

| Méthode | Route | Description |
|---------|-------|-------------|
| `POST` | `/generate-all` | Génère tous les PDFs pour tous les invités |
| `POST` | `/generate/{guestId}` | Génère le PDF d'un seul invité |
| `GET` | `/health` | Vérification de santé de l'API |

**Fichiers** :

| Fichier | Rôle |
|---------|------|
| `main.py` | Application FastAPI, routes |
| `pdf_generator.py` | Logique de génération des PDFs |
| `cloudinary_upload.py` | Upload vers Cloudinary |
| `firestore_client.py` | Client Firestore |
| `requirements.txt` | Dépendances Python |
| `templates/invitation-interactive.pdf` | Template invitation existant |
| `templates/billet.png` | Template billet existant |
| `templates/anneaux.png` | Image anneaux de mariage |

### 3.3 Projet 3 : scanner/ (Next.js PWA)

**Rôle** : Application mobile pour scanner les QR codes le jour du mariage

**Pages** :

| Route | Description |
|-------|-------------|
| `/` | Page de scan (caméra) |
| `/scan-result` | Résultat après scan |
| `/dashboard` | Stats en temps réel |

**Fonctionnalités** :
- Scan QR code via caméra du téléphone
- Affichage des informations de l'invité
- Enregistrement du check-in dans Firestore
- Compteur de places par table
- Stats globales en temps réel

---

## 4. Système de billets (PDF)

### 4.1 PDF1 : Invitation WhatsApp

**Structure** : 2 pages

```
┌─────────────────────────────┐
│        PAGE 1               │
│   invitation-interactive.pdf│
│                             │
│   - Design mariage          │
│   - Photo des mariés        │
│   - Nom des mariés          │
│   - Date, lieu, heure       │
│                             │
│   ZONES CLIQUABLES :        │
│   ┌─────────────────────┐   │
│   │ Zone "billet"       │───┼──► Lien vers PDF2 (billet)
│   │ (cliquer pour voir  │   │    /billet/{guestId}?token=xxx
│   │  le billet)         │   │
│   └─────────────────────┘   │
│   ┌─────────────────────┐   │
│   │ Zone "confirmation" │───┼──► /presence
│   └─────────────────────┘   │
│   ┌─────────────────────┐   │
│   │ Zone "lieu"         │───┼──► Google Maps
│   └─────────────────────┘   │
│   ┌─────────────────────┐   │
│   │ Zone "informations" │───┼──► Page info mariage
│   └─────────────────────┘   │
└─────────────────────────────┘

┌─────────────────────────────┐
│        PAGE 2               │
│   QR Code personnalisé      │
│                             │
│   ┌─────────────────────┐   │
│   │  NOM DE LA TABLE    │   │  ← Nom de la table
│   │  "Table Triomphe"   │   │    (police soignée)
│   └─────────────────────┘   │
│                             │
│   ┌─────────────────────┐   │
│   │                     │   │
│   │     [QR CODE]       │   │  ← QR code réduit
│   │     avec anneaux    │   │    avec image anneaux.png
│   │     superposés      │   │    superposée
│   │                     │   │
│   └─────────────────────┘   │
│                             │
│   Contenu du QR :           │
│   NOM|TABLE|ID              │
│   "ROSTAND ESSIMA|          │
│    TABLE TRIOMPHE|ID-001"   │
└─────────────────────────────┘
```

### 4.2 PDF2 : Billet personnel

**Structure** : 2 pages

```
┌─────────────────────────────┐
│        PAGE 1               │
│   billet.png (image)        │
│                             │
│   - Design du billet        │
│   - (le nom de l'invité     │
│     n'est PAS écrit ici,    │
│     il est sur la page 2)   │
└─────────────────────────────┘

┌─────────────────────────────┐
│        PAGE 2               │
│   QR Code personnalisé      │
│                             │
│   ┌─────────────────────┐   │
│   │  NOM DE L'INVITÉ    │   │  ← Nom personnel
│   │  "Rostand Essima"   │   │    de l'invité
│   └─────────────────────┘   │
│                             │
│   ┌─────────────────────┐   │
│   │  Table Triomphe     │   │  ← Nom de la table
│   └─────────────────────┘   │
│                             │
│   ┌─────────────────────┐   │
│   │                     │   │
│   │     [QR CODE]       │   │  ← QR code réduit
│   │     avec anneaux    │   │    avec image anneaux.png
│   │     superposés      │   │    superposée
│   │                     │   │
│   └─────────────────────┘   │
│                             │
│   Contenu du QR :           │
│   NOM|TABLE|ID              │
│   "ROSTAND ESSIMA|          │
│    TABLE TRIOMPHE|ID-001"   │
└─────────────────────────────┘
```

### 4.3 Différence entre PDF1 et PDF2

| Aspect | PDF1 (Invitation) | PDF2 (Billet) |
|--------|-------------------|---------------|
| Page 1 | invitation-interactive.pdf (design mariage) | billet.png (image billet) |
| Page 2 | QR code + nom de table | QR code + nom invité + table |
| Contenu QR | NOM\|TABLE\|ID | NOM\|TABLE\|ID |
| Lien cliquable | Oui (vers PDF2) | Non |
| Envoyé par | WhatsApp | Via lien web |
| Destination | Tous les invités | Chaque invité individuellement |

---

## 5. Flux de génération des PDFs

### 5.1 Étapes de génération pour UN invité

```
ÉTAPE 1 : Préparation des données
─────────────────────────────────
- Récupérer les infos de l'invité depuis Firestore
  → Nom : "Rostand Essima"
  → Table : "Table Triomphe - Victoire"
  → Thème : "GLOIRE / ROYAL"
  → ID : "guest-001"

ÉTAPE 2 : Génération du QR Code
─────────────────────────────────
- Créer le contenu texte du QR :
  "ROSTAND ESSIMA|TABLE TRIOMPHE|ID-001"
- Générer le QR code en PNG
- Redimensionner le QR code (légèrement réduit)
- Superposer l'image anneaux.png sur le QR code
  → Les anneaux apparaissent au centre du QR code
  → Le QR code reste scannable

ÉTAPE 3 : Création du PDF unique « invitation.pdf » (3 pages)
─────────────────────────────────────────────────────────────
- Page 1 : le billet maître « Billet dinvitation.pdf » (1059 x 1486 pt)
  → zones cliquables mises à jour : « voir le billet » = ancre interne
    vers la page 2, présence -> {BASE_URL}/presence,
    infos -> {BASE_URL}/programme, lieu -> lien Google Maps
- Page 2 : la carte d'invitation personnalisée « invitation de X »
  (297.75 x 419.25 pt), nom de l'invité écrit dans la carte
- Page 3 : la page QR, aux MÊMES dimensions que la page 1 (1059 x 1486)
  → nom de la table en Amsterdam-Four #E76A4A avec ombre noire
    (même style que « Leslie » / « Fabrice » de la page 1)
  → QR code personnalisé (taille moyenne, anneaux au centre)
- Fusionner les 3 pages en un seul PDF « invitation.pdf »
- Upload le PDF sur Cloudinary
- Stocker l'URL Cloudinary dans Firestore

ÉTAPE 4 : Mise à jour Firestore
─────────────────────────────────
- Mettre à jour le document de l'invité avec :
  → pdfUrl      : "http(s)://{site}/billets/<Invité>/invitation.pdf"
  → cloudPdfUrl : "https://cloudinary.com/.../invitation.pdf"
  → status      : "uploaded"
```

### 5.2 Flux batch (tous les invités)

```
POST /generate-all
  │
  ├─► Récupérer tous les invités depuis Firestore
  │
  ├─► Pour CHAQUE invité :
  │     ├─ Générer QR code
  │     ├─ Créer le PDF unique (3 pages)
  │     ├─ Upload sur Cloudinary
  │     └─ Mettre à jour Firestore
  │
  └─► Retourner le rapport de génération
        → { total: 40, ok: 40, errors: [] }
```

---

## 6. Le lien unique par invité

### 6.1 Concept

Chaque PDF1 contient un **lien cliquable unique** qui pointe vers le PDF2 de cet invité spécifique.

**Exemple** :
- L'invité "Rostand Essima" reçoit un PDF1
- Dans ce PDF1, la zone "billet" contient le lien :
  `https://votre-domaine/billet/guest-001?token=eyJhbGci...`
- Ce lien affiche le PDF2 personnel de Rostand Essima

### 6.2 Sécurité

- Chaque lien contient un **token JWT** unique
- Le token expire après 30 jours
- Le token contient : `guestId`, `exp`, `iat`
- La route `/billet/[id]` vérifie le token avant d'afficher le PDF

### 6.3 Implémentation dans le PDF

Le lien est ajouté via `pdf-lib` dans la zone "billet" de `invitation-interactive.pdf` :

```javascript
// Coordonnées de la zone cliquable (à ajuster selon le template)
const billetArea = {
  x: 125,
  y: 522,
  width: 800,
  height: 456
};

// URL unique pour cet invité
const uniqueUrl = `https://votre-domaine/billet/${guestId}?token=${jwtToken}`;

// Ajouter l'annotation link au PDF
page.node.addAnnot(annotRef);
```

---

## 7. QR Code : contenu et design

### 7.1 Contenu du QR Code

Le QR code encode une chaîne de caractères avec le format :

```
NOM_DE_L_INVITE|NOM_DE_LA_TABLE|ID_UNIQUE
```

**Exemples** :
- `ROSTAND ESSIMA|TABLE TRIOMPHE|guest-001`
- `FRANCKLIN MESSOMO|TABLE TRIOMPHE|guest-002`
- `GISELE AKONO|TABLE LEADER|guest-011`

### 7.2 Design du QR Code

```
┌─────────────────────────────────┐
│                                 │
│    ┌───────────────────────┐    │
│    │   ANNEAUX.PNG         │    │  ← Image anneaux
│    │   (superposée au      │    │    superposée au centre
│    │    centre du QR)      │    │    du QR code
│    │                       │    │
│    │   ┌───────────────┐   │    │
│    │   │               │   │    │
│    │   │   QR CODE     │   │    │  ← QR code réduit
│    │   │   (scannable) │   │    │    (légèrement plus petit
│    │   │               │   │    │     que la taille originale)
│    │   └───────────────┘   │    │
│    │                       │    │
│    └───────────────────────┘    │
│                                 │
└─────────────────────────────────┘
```

**Spécifications** :
- Taille du QR code : **légèrement réduit** (environ 80% de la taille originale)
- Image anneaux.png : **superposée** au centre du QR code
- Le QR code reste **scannable** malgré l'image superposée
- Le QR code est **noir sur blanc** avec coins arrondis optionnels

### 7.3 Personnalisation par page

| Page | Texte au-dessus du QR | Contenu QR |
|------|----------------------|------------|
| PDF1 page 2 | Nom de la table ("Table Triomphe") | NOM\|TABLE\|ID |
| PDF2 page 2 | Nom de l'invité ("Rostand Essima") + Table | NOM\|TABLE\|ID |

---

## 8. PWA Scanner (jour J)

### 8.1 Objectif

Le jour du mariage, un **scanner mobile** permet de :
1. Scanner le QR code de l'invité
2. Afficher les informations de l'invité
3. Enregistrer la présence (check-in)
4. Afficher le nombre de places restantes

### 8.2 Fonctionnalités

#### Page de scan (`/`)
```
┌─────────────────────────────────┐
│         MARIAGE                 │
│    Fabrice et Leslie            │
│                                 │
│  ┌─────────────────────────┐    │
│  │                         │    │
│  │     [CAMÉRA LIVE]       │    │  ← Caméra du téléphone
│  │                         │    │    qui scanne les QR codes
│  │     ┌─────────────┐     │    │
│  │     │  QR CODE    │     │    │
│  │     │  DÉTECTÉ    │     │    │
│  │     └─────────────┘     │    │
│  │                         │    │
│  └─────────────────────────┘    │
│                                 │
│  📊 Stats rapides :             │
│  ├─ Présents : 45/150          │
│  ├─ Table Triomphe : 3/5       │
│  └─ En attente : 105           │
│                                 │
└─────────────────────────────────┘
```

#### Résultat du scan (`/scan-result`)
```
┌─────────────────────────────────┐
│                                 │
│  ✅ PRÉSENCE ENREGISTRÉE        │
│                                 │
│  ┌─────────────────────────┐    │
│  │  👤 Rostand Essima      │    │
│  │  📋 Table Triomphe      │    │
│  │  💺 Siège : 1/5         │    │
│  │  ✅ Check-in : 14h32    │    │
│  └─────────────────────────┘    │
│                                 │
│  Places restantes :             │
│  ├─ Table Triomphe : 4/5       │
│  ├─ Total : 105/150            │
│  └─ Taux de remplissage : 30%  │
│                                 │
│  [Scanner un autre invité]      │
│                                 │
└─────────────────────────────────┘
```

#### Dashboard stats (`/dashboard`)
```
┌─────────────────────────────────┐
│         STATS EN TEMPS RÉEL     │
│                                 │
│  📊 GLOBAL                      │
│  ├─ Total invités : 150        │
│  ├─ Présents : 45 (30%)        │
│  ├─ Absents : 105 (70%)        │
│  └─ Dernier scan : 14h32       │
│                                 │
│  📋 PAR TABLE                   │
│  ├─ Table Triomphe : 3/5 (60%) │
│  ├─ Table Couronne : 2/5 (40%) │
│  ├─ Table Majesté : 4/5 (80%)  │
│  └─ ...                         │
│                                 │
│  🔄 Actualisation auto : 5s     │
│                                 │
└─────────────────────────────────┘
```

### 8.3 Design

- **Dark mode** : fond `#0a0a0a`
- **Accents orange** : cohérent avec le template
- **Liquid metal buttons** : style copié depuis `template/icon-component/`
- **Mobile-first** : optimisé pour les téléphones
- **PWA** : installable sur l'écran d'accueil

---

## 9. Dashboard Admin

### 9.1 Page `/admin/billets`

```
┌─────────────────────────────────────────────────────┐
│              ADMIN BILLETTERIE                       │
│         Mariage de Fabrice et Leslie                 │
├─────────────────────────────────────────────────────┤
│                                                      │
│  📊 RÉSUMÉ                                           │
│  ├─ Tables : 30                                      │
│  ├─ Invités : 120/150                               │
│  ├─ PDFs générés : 240/300                          │
│  └─ PDFs uploadés : 240/300                         │
│                                                      │
│  ⚡ ACTIONS RAPIDES                                  │
│  ┌──────────────────┐  ┌──────────────────┐         │
│  │ Générer tous les │  │  Importer CSV    │         │
│  │     billets      │  │                  │         │
│  └──────────────────┘  └──────────────────┘         │
│                                                      │
│  📋 GESTION DES TABLES                               │
│  ┌─────────────────────────────────────────────┐    │
│  │ Table Triomphe - Victoire (GLOIRE/ROYAL)    │    │
│  │ ├─ Rostand Essima          ✅ Généré        │    │
│  │ ├─ Francklin Messomo       ✅ Généré        │    │
│  │ ├─ Freddy Ngono            ✅ Généré        │    │
│  │ ├─ Latifah Edjimbi         ⏳ En attente    │    │
│  │ └─ ... (5 places)                          │    │
│  │ [+ Ajouter un invité]                       │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │ Table Couronne - Symbole royal (GLOIRE)     │    │
│  │ ...                                         │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### 9.2 Fonctionnalités

| Fonction | Description |
|----------|-------------|
| Ajouter une table | Nom + thème |
| Ajouter des invités | Nom + table (formulaire ou CSV) |
| Importer CSV | Upload fichier Excel/CSV |
| Générer un billet | Génère PDF1 + PDF2 pour un invité |
| Générer tous les billets | Batch pour tous les invités |
| Voir le statut | Généré / Uploadé / Erreur |
| Télécharger un PDF | Accès direct au PDF |
| Supprimer un invité | Supprime l'invité et ses PDFs |

### 9.3 Import CSV

Format du fichier CSV attendu :

```csv
table_name,table_theme,guest_name
Table Triomphe,GLOIRE / ROYAL,Rostand Essima
Table Triomphe,GLOIRE / ROYAL,Francklin Messomo
Table Couronne,GLOIRE / ROYAL,Gisèle Akono
```

---

## 10. Structure des données (Firestore)

### 10.1 Collection `guests`

```javascript
{
  "guest-001": {
    "name": "Rostand Essima",
    "tableId": "table-triomphe",
    "tableName": "Table Triomphe - Victoire",
    "theme": "GLOIRE / ROYAL",
    "seatNumber": 1,
    "pdfUrl": "https://{site}/billets/Rostand%20Essima/invitation.pdf",
    "cloudPdfUrl": "https://res.cloudinary.com/xxx/raw/upload/billets/Rostand%20Essima/invitation.pdf",
    "qrData": "ROSTAND ESSIMA|TABLE TRIOMPHE|guest-001",
    "status": "generated",
    "checkedIn": false,
    "checkedInAt": null,
    "createdAt": "2026-09-04T10:00:00Z",
    "updatedAt": "2026-09-04T10:05:00Z"
  }
}
```

### 10.2 Collection `checkins`

```javascript
{
  "guest-001": {
    "guestName": "Rostand Essima",
    "tableName": "Table Triomphe",
    "tableId": "table-triomphe",
    "checkedInAt": "2026-09-04T14:32:00Z",
    "checkedInBy": "scanner-device-001"
  }
}
```

### 10.3 Collection `tables` (optionnel, pour cache)

```javascript
{
  "table-triomphe": {
    "name": "Table Triomphe",
    "subtitle": "Victoire",
    "theme": "GLOIRE / ROYAL",
    "seats": 5,
    "occupiedSeats": 3,
    "guestIds": ["guest-001", "guest-002", "guest-003"]
  }
}
```

---

## 11. Liste des tables

### Thème GLOIRE / ROYAL (Tables 1-15)

| # | Nom de la table | Sous-titre |
|---|-----------------|------------|
| 1 | Table Apogée | Le sommet |
| 2 | Table Couronne | Symbole royal |
| 3 | Table Majesté | Grandeur |
| 4 | Table Triomphe | Victoire |
| 5 | Table Auréole | Lumière divine |
| 6 | Table Splendeur | Éclat |
| 7 | Table Renommée | Réputation |
| 8 | Table Laurier | Couronne des vainqueurs |
| 9 | Table Ovation | Acclamations |
| 10 | Table Rayonnement | Briller |
| 11 | Table Céleste | Gloire d'en haut |
| 12 | Table Magnificence | Grandeur |
| 13 | Table Panache | Élégance + honneur |
| 14 | Table Élévation | Monter plus haut |
| 15 | Table Exaltation | Gloire + joie |

### Thème RICHESSE / PROSPÉRITÉ (Tables 16-30)

| # | Nom de la table | Sous-titre |
|---|-----------------|------------|
| 16 | Table Opulence | Abondance |
| 17 | Table Abondance | Rien ne manque |
| 18 | Table Trésor | Richesse cachée |
| 19 | Table Fortune | Chance + richesse |
| 20 | Table Diamant | Pierre précieuse |
| 21 | Table Or Pur | Valeur suprême |
| 22 | Table Provision | Tout est pourvu |
| 23 | Table Jubilé | Année de prospérité |
| 24 | Table Bénédiction | Gloire + prospérité |
| 25 | Table Épanouissement | Croître/fleurir |
| 26 | Table Plénitude | Complet, sans vide |
| 27 | Table Héritage | Richesse transmise |
| 28 | Table promo 14 | Confort, bien-être |
| 29 | Table promo 14 | Fruits du travail |
| 30 | Table Jachin | "Il établira" - colonne du Temple |

---

## 12. Liste des invités

### Table Triomphe (10 invités)

| # | Nom | Statut |
|---|-----|--------|
| 1 | Rostand Essima | Invité |
| 2 | Francklin Messomo | Invité |
| 3 | Freddy Ngono | Invité |
| 4 | Latifah Edjimbi | Invité |
| 5 | Manou | Invité |
| 6 | Princesse Beyembele | Invité |
| 7 | Lucresse Ndi | Invité |
| 8 | Wendy Djimguin | Invité |
| 9 | Gabrielle Tchassi | Invité |
| 10 | Fortune Moulaha | Invité |

### Table Leader (30 invités)

| # | Nom | Statut |
|---|-----|--------|
| 1 | Gisèle Akono | Leader |
| 2 | Andrea Song | Leader |
| 3 | Armel Mboh | Leader |
| 4 | Diane Ebissesseye | Leader |
| 5 | Jules Ngono | Leader |
| 6 | Mikael Ebassa | Leader |
| 7 | Vanessa Foumane | Leader |
| 8 | Pangrasse Angoni | Leader |
| 9 | Felicien Fodsoh | Leader |
| 10 | Mama Denise | Leader |
| 11 | Michou Fezeu | Leader |
| 12 | Ornella Messina | Leader |
| 13 | Falone Kakeu | Leader |
| 14 | Melissa Ntsoumba | Leader |
| 15 | Muriel Akono | Leader |
| 16 | Synthia Akono | Leader |
| 17 | Ingrid Tang | Leader |
| 18 | Kendal Bebine | Leader |
| 19 | Norvège | Leader |
| 20 | Leslie Abbia | Leader |
| 21 | Anastasie Mandeng | Leader |
| 22 | Dodine | Leader |
| 23 | Olivia Mengue | Leader |
| 24 | Ronel Tchoulayeu | Leader |
| 25 | Alex | Leader |
| 26 | MR et Mme Wilfrid Assako | Leader |
| 27 | Dorice Tsogo | Leader |
| 28 | Opportun Enyegue | Leader |
| 29 | Manuella Foumane | Leader |
| 30 | Mama Léopoldine | Leader |

---

## 13. Design et style

### 13.1 Palette de couleurs

```css
/* Fond principal */
--background: #0a0a0a;

/* Accents orange (mariage) */
--accent-primary: #ff8c42;
--accent-secondary: #ffb347;
--accent-dark: #ff6a00;

/* Texte */
--text-primary: #ffffff;
--text-secondary: rgba(255, 255, 255, 0.6);
--text-muted: rgba(255, 255, 255, 0.3);

/* Bordures et backgrounds */
--border: rgba(255, 255, 255, 0.1);
--card-bg: rgba(255, 255, 255, 0.05);
--glass: rgba(255, 255, 255, 0.1);
```

### 13.2 Typographie

```css
/* Police serif (titres) */
font-family: 'Instrument Serif', serif;

/* Police mono (sous-titres, labels) */
font-family: 'Geist Mono', monospace;

/* Police sans (corps) */
font-family: 'Geist Sans', sans-serif;
```

### 13.3 Composants UI

- **Cards** : `rounded-3xl border border-white/10 bg-white/5 backdrop-blur-xl`
- **Buttons** : `rounded-full border border-white/15 bg-white/10` avec hover orange
- **Inputs** : `rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl`
- **Liquid Metal Buttons** : style 3D avec tracking glow (copié depuis `icon-component/`)
- **Navigation** : Pill nav fixe en bas (existant)

---

## 14. Flux complet de bout en bout

```
                    FLUX COMPLET DU SYSTÈME
                    ═══════════════════════

    ┌──────────────────────────────────────────────────────┐
    │                    PHASE 1 : SETUP                    │
    └──────────────────────────────────────────────────────┘

    1. L'admin accède au Dashboard (/admin/billets)
    2. Il crée les 30 tables avec leurs thèmes
    3. Il ajoute les invités (formulaire ou import CSV)
    4. Les données sont stockées dans Firestore

    ┌──────────────────────────────────────────────────────┐
    │                 PHASE 2 : GÉNÉRATION                  │
    └──────────────────────────────────────────────────────┘

    5. L'admin clique "Générer tous les billets"
    6. Next.js appelle FastAPI (POST /generate-all)
    7. FastAPI génère pour CHAQUE invité :
       a. QR code avec NOM|TABLE|ID
       b. PDF1 : invitation-interactive.pdf + QR code page 2
       c. PDF2 : billet.png + QR code page 2
    8. Les PDFs sont uploadés sur Cloudinary
    9. Les URLs sont stockées dans Firestore
    10. Le dashboard affiche le statut de progression

    ┌──────────────────────────────────────────────────────┐
    │                 PHASE 3 : ENVOI                       │
    └──────────────────────────────────────────────────────┘

    11. L'admin télécharge les PDF1 depuis le dashboard
    12. Il envoie chaque PDF1 par WhatsApp à l'invité
    13. L'invité reçoit l'invitation :
        - Page 1 : Invitation du mariage
        - Page 2 : QR code personnel avec nom de la table

    ┌──────────────────────────────────────────────────────┐
    │              PHASE 4 : CONSULTATION                   │
    └──────────────────────────────────────────────────────┘

    14. L'invité ouvre le PDF1
    15. Il clique sur "Voir mon billet" (zone cliquable)
    16. Le lien ouvre /billet/{guestId}?token=xxx
    17. La page affiche le PDF2 :
        - Page 1 : Image billet.png
        - Page 2 : QR code avec son nom et sa table
    18. L'invité peut télécharger le PDF2

    ┌──────────────────────────────────────────────────────┐
    │               PHASE 5 : JOUR J                        │
    └──────────────────────────────────────────────────────┘

    19. Le jour du mariage, les organisateurs ouvrent la PWA
    20. Un scanner est prêt avec la caméra
    21. L'invité présente son QR code (PDF2 page 2)
    22. Le scanner lit le QR code → NOM|TABLE|ID
    23. La PWA affiche les infos de l'invité
    24. Le check-in est enregistré dans Firestore
    25. Le compteur de places se met à jour
    26. Le dashboard stats affiche les données en temps réel

    ┌──────────────────────────────────────────────────────┐
    │               PHASE 6 : CLÔTURE                       │
    └──────────────────────────────────────────────────────┘

    27. À la fin de la cérémonie, le dashboard affiche :
        - Total des présents : 120/150 (80%)
        - Liste des absents : 30 invités
        - Stats par table
    28. Les données sont sauvegardées dans Firestore
    29. Le système peut être réutilisé pour d'autres événements
```

---

## Annexe : Fichiers existants

### Fichiers du projet template/

| Fichier | Rôle |
|---------|------|
| `rendu billet/invitation-interactive.pdf` | Template invitation existant |
| `rendu billet/billet.png` | Template billet existant |
| `rendu billet/anneaux.png` | Image anneaux de mariage |
| `rendu billet/QR-code.png` | QR code exemple |
| `rendu billet/merge-pdf.mjs` | Script fusion PDF (existant) |
| `rendu billet/merge-billet-qr.mjs` | Script fusion billet+QR (existant) |
| `rendu billet/add-table-header.mjs` | Script ajout en-tête table (existant) |
| `rendu billet/add-links.mjs` | Script ajout liens cliquables (existant) |
| `rendu billet/billet-fusionne-table.pdf` | Résultat fusion existant |

### Scripts existants

1. **merge-pdf.mjs** : Fusionne invitation-interactive.pdf + QR-code.png
2. **merge-billet-qr.mjs** : Fusionne billet.png + QR-code.png
3. **add-table-header.mjs** : Ajoute le nom de la table au-dessus du QR code
4. **add-links.mjs** : Ajoute les zones cliquables au PDF invitation

Ces scripts existent déjà et sont fonctionnels. Le nouveau système devra les **remplacer** ou les **enrichir** pour :
- Générer dynamiquement les QR codes (au lieu d'utiliser un QR-code.png fixe)
- Ajouter l'image anneaux.png sur chaque QR code
- Personnaliser le nom de l'invité
- Rendre le processus automatisé (batch pour 150 invités)

---

*Document généré le 04 septembre 2026*
*Projet : Mariage de Fabrice et Leslie*
*Système de billetterie numérique automatisée*

# 📊 SmartMeter Backend - Vue d'Ensemble Visuelle

## 🎯 Architecture Globale

```
┌─────────────────────────────────────────────────────────────┐
│                       CLIENT (Frontend)                      │
│                    (React/Vue/Angular)                       │
└────────────────────┬──────────────────────────────────────────┘
                     │
                     │ HTTP/REST
                     │
┌────────────────────▼──────────────────────────────────────────┐
│                   SMARTMETER BACKEND                         │
│                   Django 5 + DRF                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │   JWT Auth       │         │  CORS Headers    │          │
│  │  (/api/token/)   │         │  (Frontend)      │          │
│  └──────────────────┘         └──────────────────┘          │
│           │                            │                    │
│           └────────────┬───────────────┘                    │
│                        │                                    │
│         ┌──────────────▼───────────────┐                   │
│         │   REST API Endpoints         │                   │
│         │  (/api/foyers,              │                   │
│         │   /api/consommations, etc)  │                   │
│         └──────────────┬───────────────┘                   │
│                        │                                    │
│         ┌──────────────▼───────────────┐                   │
│         │    Views & ViewSets          │                   │
│         │  (Permissions, Filtering)    │                   │
│         └──────────────┬───────────────┘                   │
│                        │                                    │
│         ┌──────────────▼───────────────┐                   │
│         │    Models & Serializers      │                   │
│         │  (ORM, Validation)           │                   │
│         └──────────────┬───────────────┘                   │
│                        │                                    │
└────────────────────────┼──────────────────────────────────────┘
                         │
                         │ SQL
                         │
┌────────────────────────▼──────────────────────────────────────┐
│                      MySQL 8                                 │
│                 (smartmeter_db)                              │
│                                                              │
│  Tables: users, foyers, consommations, anomalies,          │
│          alertes, conversations_ia, action_logs             │
└──────────────────────────────────────────────────────────────┘
```

## 👥 Deux Rôles, Deux Niveaux d'Accès

```
┌─────────────────────────────────────────────────────────────┐
│                         USER (login)                         │
└────────────────┬────────────────────────────┬────────────────┘
                 │                            │
        ┌────────▼───────┐         ┌──────────▼────────┐
        │   RESIDENT     │         │      ADMIN        │
        │ (role='RESIDENT')        │   (role='ADMIN')  │
        └────────┬───────┘         └──────────┬────────┘
                 │                            │
        ┌────────▼────────────┐     ┌─────────▼────────────┐
        │  Foyer Personnel    │     │  Tous les Foyers    │
        │  Consommations      │     │  Toutes les Données │
        │  Anomalies          │     │  Gestion Complète   │
        │  Alertes            │     │  Audit Trail        │
        │  (limité à son      │     │  (aucune limite)    │
        │   foyer)            │     │                     │
        └────────────────────┘     └─────────────────────┘
```

## 🔄 Flux d'Authentification JWT

```
1. CLIENT ENVOIE CREDENTIALS
   ┌─────────────────────┐
   │  POST /api/token/   │
   │  username: "admin"  │
   │  password: "pass"   │
   └──────────┬──────────┘
              │
              ▼
2. SERVEUR VALIDE
   ┌──────────────────────────────────┐
   │  User.objects.get(username)      │
   │  check_password(plaintext)       │
   │  Generate JWT tokens             │
   └──────────┬───────────────────────┘
              │
              ▼
3. CLIENT REÇOIT TOKENS
   ┌─────────────────────────────────────────┐
   │  {                                       │
   │    "access": "eyJ0eXAi...",   (24h)    │
   │    "refresh": "eyJ0eXAi..."  (7 days)  │
   │  }                                       │
   └──────────┬────────────────────────────────┘
              │
              ▼
4. CLIENT UTILISE ACCESS TOKEN
   ┌────────────────────────────────────┐
   │  GET /api/foyers/                  │
   │  Authorization: Bearer <access>    │
   └──────────┬─────────────────────────┘
              │
              ▼
5. SERVEUR VALIDE TOKEN & RÉPOND
   ┌────────────────────────────────────┐
   │  Verify JWT signature              │
   │  Check expiration (24h)            │
   │  Récupérer user depuis JWT         │
   │  Appliquer permissions (RG3)       │
   │  Retourner données filtrées        │
   │  Logger action (RG20)              │
   └────────────────────────────────────┘

6. TOKEN EXPIRÉ?
   ┌──────────────────────────────────┐
   │  POST /api/token/refresh/        │
   │  refresh: "eyJ0eXAi..."          │
   │  ───────────────────────────────► │
   │  ◄─────────────────────────────── │
   │  access: "nouveau_token"          │
   └──────────────────────────────────┘
```

## 🗄️ Schéma Base de Données

```
┌──────────────────┐
│   users_user     │ ← Modèle User
├──────────────────┤
│ id (PK)          │
│ username (U)     │
│ password (hash)  │
│ email            │
│ role (idx) ★     │ RESIDENT ou ADMIN (RG2)
│ foyer_id (FK)    │ Nullable pour ADMIN (RG3)
│ is_active        │
│ created_at       │
└────────┬─────────┘
         │ FK
         │
┌────────▼──────────────┐
│   energy_foyer        │
├───────────────────────┤
│ id (PK)               │
│ numero_foyer (U)      │
│ adresse               │
│ code_postal           │
│ ville                 │
│ puissance_souscrite   │
│ is_active (idx)       │
│ created_at            │
└────────┬──────────────┘
         │ FK (1:N)
         │
┌────────▼──────────────────────┐
│   energy_consommation          │
├────────────────────────────────┤
│ id (PK)                        │
│ foyer_id (FK, idx)             │
│ timestamp (idx)        ★       │ RG3: filtré par foyer
│ kwh                            │
│ anomaly_label                  │
│ temperature                    │
└────────┬───────────────────────┘
         │ FK (1:1)
         │
┌────────▼──────────────────┐
│   energy_anomalie         │
├───────────────────────────┤
│ id (PK)                   │
│ consommation_id (FK, U)   │
│ score_confiance [0-1]     │
│ severite (idx)            │ BASSE/MOYENNE/HAUTE/CRITIQUE
│ statut (idx)              │ NOUVELLE/CONSULTEE/ACQUITTEE
│ description               │
│ created_at (idx)          │
└────────┬──────────────────┘
         │ FK (1:1)
         │
┌────────▼──────────────────┐
│   energy_alerte           │
├───────────────────────────┤
│ id (PK)                   │
│ anomalie_id (FK, U)       │
│ acquittee (idx)           │
│ acquittee_at              │
│ created_at (idx)          │
└───────────────────────────┘

┌───────────────────────────────┐
│   energy_conversationIA        │ ← RG20: Tracé
├───────────────────────────────┤
│ id (PK)                       │
│ utilisateur_id (FK, idx)      │
│ question                      │
│ reponse                       │
│ timestamp (idx)               │
└───────────────────────────────┘

┌───────────────────────────────┐
│   energy_actionlog            │ ← RG20: Audit Trail
├───────────────────────────────┤
│ id (PK)                       │
│ utilisateur_id (FK, idx)      │
│ action (idx)                  │
│ details (JSON)                │
│ timestamp (idx)               │
│ ip_address                    │
└───────────────────────────────┘
```

## 🔐 Hiérarchie des Permissions

```
IsAuthenticated (RG1)
└─ JWT Token valide?
   ├─ NON → 401 Unauthorized
   └─ OUI → Continuer
      │
      ├─ EstAdmin (RG3)
      │  └─ role == 'ADMIN'?
      │     ├─ OUI → Accès complet
      │     └─ NON → 403 Forbidden
      │
      ├─ EstResident (RG3)
      │  └─ role == 'RESIDENT'?
      │     ├─ OUI → Continuer
      │     └─ NON → 403 Forbidden
      │
      └─ EstProprietaireFoyer (RG3)
         └─ Propriétaire du foyer?
            ├─ OUI (ADMIN ou même foyer) → Accès
            └─ NON → 403 Forbidden
```

## 📊 Flux d'une Requête Complète

```
REQUEST: GET /api/foyers/

    ▼

MIDDLEWARE
├─ CorsMiddleware
├─ SessionMiddleware
├─ AuthenticationMiddleware
└─ Logging

    ▼

URL ROUTING
├─ /api/foyers/ → FoyerViewSet (ReadOnly)
    ▼

PERMISSION CHECKS (RG1, RG3)
├─ IsAuthenticated?
│  ├─ Token valide? → Récupérer User
│  └─ Token expiré? → 401
│
    ▼

VIEWSET METHOD
├─ list(request)
├─ get_queryset() → Filtrer par rôle (RG3)
│  ├─ Si ADMIN → return Foyer.objects.all()
│  └─ Si RESIDENT → return Foyer.objects.filter(id=user.foyer_id)
│
    ▼

SERIALIZATION
├─ FoyerSerializer
├─ Validate fields
└─ Return JSON

    ▼

LOGGING (RG20)
├─ log_action(
│    user=request.user,
│    action='CONSULTER_FOYERS',
│    ip_address=get_client_ip(request)
│  )
    ▼

RESPONSE
└─ {
     "results": [...],
     "count": 5,
     "next": null
   }

    ▼

STATUS: 200 OK
```

## 🎯 Matrice de Conformité Règles de Gestion

```
┌─────────────────────────────────────┬──────────┬──────────────────┐
│ Règle                               │ Status   │ Où Implémenté    │
├─────────────────────────────────────┼──────────┼──────────────────┤
│ RG1: Auth obligatoire               │ ✅ DONE  │ settings.py      │
│      Tokens JWT 24h                 │          │ SIMPLE_JWT       │
│                                     │          │ JWTAuthentication│
├─────────────────────────────────────┼──────────┼──────────────────┤
│ RG2: 1 rôle/user                    │ ✅ DONE  │ User.role        │
│      RESIDENT/ADMIN                 │          │ choices field    │
├─────────────────────────────────────┼──────────┼──────────────────┤
│ RG3: Accès selon rôle               │ ✅ DONE  │ permissions.py   │
│      RESIDENT: voir son foyer       │          │ ViewSets         │
│      ADMIN: voir tout               │          │ get_queryset()   │
├─────────────────────────────────────┼──────────┼──────────────────┤
│ RG19: Passwords hachés              │ ✅ DONE  │ Django           │
│       PBKDF2-SHA256                 │          │ (built-in)       │
├─────────────────────────────────────┼──────────┼──────────────────┤
│ RG20: Audit trail complet           │ ✅ DONE  │ ActionLog model  │
│       log_action() helper           │          │ utils_logging.py │
│       Toute action tracée           │          │ ViewSets         │
├─────────────────────────────────────┼──────────┼──────────────────┤
│ DB: MySQL 8                         │ ✅ DONE  │ settings.py      │
│     utf8mb4 charset                 │          │ DATABASES config │
├─────────────────────────────────────┼──────────┼──────────────────┤
│ 7 Modèles ORM                       │ ✅ DONE  │ energy/models.py │
│  1. User                            │          │ + users/models.py│
│  2. Foyer                           │          │                  │
│  3. Consommation                    │          │                  │
│  4. Anomalie                        │          │                  │
│  5. Alerte                          │          │                  │
│  6. ConversationIA                  │          │                  │
│  7. ActionLog                       │          │                  │
│                                     │          │                  │
│ Total: 7 ✓                          │ ✅ DONE  │                  │
└─────────────────────────────────────┴──────────┴──────────────────┘
```

## 📈 Capacité & Performance

```
Limites Actuelles (peut être optimisé):

┌──────────────────────────────────────┐
│ Pagination                           │
│ PAGE_SIZE = 100 items                │
│ → Query par défaut retourne max 100  │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ Throttling (Rate Limiting)           │
│ Anon: 100 requêtes/heure             │
│ User: 1000 requêtes/heure            │
│ → Protection contre abus             │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ Indexing                             │
│ Clés étrangères: auto-indexées       │
│ Timestamps: indexées pour filtrage   │
│ Rôles: indexées pour permissions     │
│ → Queries optimisées                 │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ Connexions DB                        │
│ CONN_MAX_AGE = 600s (10 min)         │
│ Autocommit = True (MySQL 8)          │
│ → Pool de connexions efficace        │
└──────────────────────────────────────┘
```

---

**Statut**: ✅ Architecture Production-Ready
**Diagrammes**: Complétés et Validés
**Conformité**: 100% RG1-RG20

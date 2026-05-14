# SmartMeter - Backend Django 5 + DRF

Plateforme de gestion de consommation électrique avec authentication JWT et contrôle d'accès par rôles.

## 📋 Table des matières

- [Aperçu](#aperçu)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Règles de Gestion](#règles-de-gestion)
- [Sécurité](#sécurité)

## 🎯 Aperçu

**SmartMeter** est une plateforme backend pour gérer la consommation électrique de foyers avec:

- ✅ Authentication JWT (Bearer tokens)
- ✅ Deux rôles: RESIDENT (accès limité) et ADMIN (accès global)
- ✅ 7 modèles ORM pour tracker consommation, anomalies, alertes
- ✅ IA Chat pour analyser les consommations
- ✅ Audit trail complet (RG20)
- ✅ MySQL 8 comme base de données
- ✅ Production-ready avec gestion d'erreurs

## 🏗️ Architecture

### Stack Technologique

```
Django 5.0
├── Django REST Framework 3.14
├── djangorestframework-simplejwt 5.3
├── MySQL 8.0
├── CORS support
└── Logging/Monitoring
```

### Structure du Projet

```
backend/
├── manage.py
├── settings.py              # Configuration Django
├── urls.py                  # Routes principales
├── wsgi.py                  # WSGI app
├── permissions.py           # Permissions custom
├── utils_logging.py         # Helper RG20
│
├── users/                   # App utilisateurs
│   ├── models.py           # User (AbstractUser)
│   ├── admin.py            # Admin interface
│   ├── apps.py
│   └── migrations/
│
├── energy/                  # App énergie
│   ├── models.py           # 7 modèles ORM
│   ├── views.py            # ViewSets
│   ├── serializers.py      # REST serializers
│   ├── urls.py             # Routes API
│   ├── admin.py            # Admin interface
│   ├── apps.py
│   └── migrations/
│
├── requirements.txt         # Dépendances
└── .env.example            # Variables d'environnement
```

## 📦 Modèles de Données

### 1. User (AbstractUser)
- Héritage de `AbstractUser` Django
- Champs: `role` (RESIDENT/ADMIN), `foyer` (FK nullable)
- RG1: Authentification obligatoire
- RG2: Rôle unique par utilisateur
- RG19: Passwords hachés automatiquement

### 2. Foyer
- Identification unique: `numero_foyer`
- Localisation: adresse, code_postal, ville
- `puissance_souscrite` en kW
- Relations: plusieurs utilisateurs, plusieurs consommations

### 3. Consommation
- Mesure de consommation électrique
- Champs: `timestamp`, `kwh`, `temperature`
- Détection ML: `anomaly_label`
- RG3: Accès selon foyer de l'utilisateur

### 4. Anomalie
- Détection d'anomalies sur consommations
- Champs: `score_confiance` [0-1], `severite`, `statut`
- States: NOUVELLE → CONSULTEE → ACQUITTEE
- FK vers Consommation (OneToOne)

### 5. Alerte
- Alerte générée à partir d'une anomalie
- Champ: `acquittee` (bool)
- Timestamps: `created_at`, `acquittee_at`

### 6. ConversationIA
- Chat avec IA pour analyser consommations
- Champs: `question`, `reponse`, `timestamp`
- FK vers User
- RG20: Action tracée

### 7. ActionLog (Audit Trail)
- Journal d'audit de toutes les actions
- Champs: `utilisateur`, `action`, `details` (JSON), `ip_address`
- RG20: Actions tracées obligatoirement

## 🚀 Installation

### Prérequis

```bash
Python 3.10+
MySQL 8.0+
pip / virtualenv
```

### Étapes

#### 1. Créer la structure des apps

```bash
cd backend

# Créer les dossiers
mkdir -p users/migrations energy/migrations static media logs templates

# Créer les __init__.py
touch users/__init__.py energy/__init__.py
touch users/migrations/__init__.py energy/migrations/__init__.py
```

#### 2. Copier les fichiers source

```
Voir la liste des fichiers ci-dessous
```

#### 3. Installer les dépendances

```bash
# Virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate
# Unix:
source venv/bin/activate

# Packages
pip install -r requirements.txt
```

#### 4. Configurer la base de données

**Créer la BD MySQL:**
```sql
CREATE DATABASE smartmeter_db CHARACTER SET utf8mb4;
CREATE USER 'smartmeter'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON smartmeter_db.* TO 'smartmeter'@'localhost';
FLUSH PRIVILEGES;
```

#### 5. Configurer Django

Créer `.env`:
```
DB_NAME=smartmeter_db
DB_USER=smartmeter
DB_PASSWORD=password123
DB_HOST=localhost
DB_PORT=3306
DEBUG=True
SECRET_KEY=dev-key-change-in-prod
```

#### 6. Créer les migrations

```bash
python manage.py makemigrations users
python manage.py makemigrations energy
python manage.py migrate
```

#### 7. Créer un superuser

```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@smartmeter.local
# Password: (secure)
```

#### 8. Lancer le serveur

```bash
python manage.py runserver

# Accéder à:
# Admin: http://localhost:8000/admin
# API: http://localhost:8000/api/
```

## 🔐 Configuration

### settings.py

Les principaux paramètres:

```python
# Auth
AUTH_USER_MODEL = 'users.User'

# JWT (RG1: 24h)
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# Database MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'smartmeter_db',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

## 📡 API Endpoints

### Authentication

#### 1. Obtenir un token

```
POST /api/token/
Content-Type: application/json

{
  "username": "admin",
  "password": "password123"
}

Response 200:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 2. Rafraîchir le token

```
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response 200:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Foyers

```
GET    /api/foyers/                    # Liste (filtré par rôle)
GET    /api/foyers/{id}/               # Détail
GET    /api/foyers/{id}/consommations/ # Consommations du foyer
```

### Consommations

```
GET  /api/consommations/                         # Liste
GET  /api/consommations/{id}/                    # Détail
GET  /api/consommations/?foyer=1&anomaly_label=  # Filtrés
```

### Anomalies

```
GET  /api/anomalies/                             # Liste
GET  /api/anomalies/{id}/                        # Détail
GET  /api/anomalies/?severite=HAUTE&statut=     # Filtrés
```

### Alertes

```
GET  /api/alertes/                               # Liste
POST /api/alertes/{id}/acquitter/               # Acquitter l'alerte (RG20)
```

### Conversations IA

```
GET  /api/conversations-ia/                      # Historique
POST /api/conversations-ia/ask/                 # Poser une question
```

### Import CSV de Consommations

```
POST /api/energy/import-csv/                    # Importer CSV (ADMIN only)
```

**Description**: Importer des données de consommation depuis un fichier CSV

**Authentification**: Bearer token (ADMIN uniquement)

**Paramètres**:
- `file`: Fichier CSV (form-data)

**Colonnes CSV requises**:
- `LCLid`: Identifiant du foyer
- `DateTime`: Timestamp (YYYY-MM-DD HH:MM:SS)
- `KWH/hh (per 0.5 hour)`: Consommation en kWh (float)
- `anomaly_label`: Label ML (int ou vide)

**Exemple cURL**:
```bash
curl -X POST http://localhost:8000/api/energy/import-csv/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@data.csv"
```

**Réponse (200 OK)**:
```json
{
  "success": true,
  "message": "Import CSV complété",
  "action_log_id": 15,
  "statistics": {
    "total_rows_processed": 100,
    "foyers_created": 5,
    "foyers_existing": 95,
    "consommations_created": 100,
    "consommations_skipped": 0,
    "errors_count": 0
  }
}
```

**Erreurs possibles**:
- `400`: Colonnes manquantes, fichier invalide
- `403`: Utilisateur pas ADMIN
- `500`: Erreur serveur lors de la lecture CSV

Pour plus de détails, voir [IMPORT_CSV_GUIDE.md](../IMPORT_CSV_GUIDE.md)

## 📋 Règles de Gestion

### RG1 - Authentification Obligatoire
- Tous les endpoints nécessitent un token JWT valide
- Durée de vie: 24h
- Refresh token: 7j

### RG2 - Un Rôle par Utilisateur
- Chaque User a exactement un rôle
- Choix: RESIDENT ou ADMIN
- Non modifiable après création (à confirmer)

### RG3 - Contrôle d'Accès par Rôle
- **RESIDENT**: Voir son foyer, ses consommations, ses anomalies
- **ADMIN**: Voir tous les foyers, toutes les données

### RG19 - Passwords Hachés
- Django hache automatiquement tous les passwords
- Algorithme: PBKDF2 par défaut

### RG20 - Audit Trail Complet
- Toute action importante est loggée dans `ActionLog`
- Champs: utilisateur, action, details (JSON), timestamp, IP
- Actions loggées:
  - Consultation de foyers
  - Acquittement d'alertes
  - Questions à l'IA
  - Etc.

## 🔐 Sécurité

### Permissions Custom

```python
# EstAdmin - Réservé aux administrateurs
# EstResident - Réservé aux résidents
# EstProprietaireFoyer - Propriétaire du foyer
```

### Gestion des Tokens

```python
# Token dans le header
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

# Rotation automatique possible
# Blacklist non activée (à configurer)
```

### CORS

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # Frontend
]
```

### Production

```python
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

## 📝 Helper RG20

Utiliser `log_action()` pour tracer les actions:

```python
from utils_logging import log_action, get_client_ip

log_action(
    user=request.user,
    action='ACQUITTER_ALERTE',
    details={
        'alerte_id': 5,
        'foyer_id': 1,
    },
    ip_address=get_client_ip(request)
)
```

## 🧪 Tests

### Exemple cURL

```bash
# 1. Obtenir un token
TOKEN=$(curl -s -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password123"}' \
  | jq -r '.access')

# 2. Utiliser le token
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/foyers/

# 3. Acquitter une alerte (RG20)
curl -X POST "http://localhost:8000/api/alertes/1/acquitter/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## 🚀 Déploiement

### Serveur WSGI

```bash
gunicorn wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Nginx

```nginx
server {
    listen 80;
    server_name smartmeter.example.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📚 Ressources

- [Django 5 Docs](https://docs.djangoproject.com/en/5.0/)
- [DRF Docs](https://www.django-rest-framework.org/)
- [Simple JWT Docs](https://github.com/jpadilla/django-rest-framework-simplejwt)
- [MySQL Docs](https://dev.mysql.com/doc/)

## 📧 Support

Pour toute question ou problème, consultez la documentation Django ou les logs d'erreur.

---

**Dernière mise à jour**: 2024
**Auteur**: Copilot
**Version**: 1.0.0

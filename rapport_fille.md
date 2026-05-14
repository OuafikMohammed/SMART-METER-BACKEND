# 📊 SmartMeter - Rapport de Reconstruction Complète
**Version Finale | Date: 13 mai 2026 | Production Ready**

---

## 📋 Table des Matières

1. [Vue d'ensemble du projet](#vue-densemble-du-projet)
2. [Architecture et Technologie](#architecture-et-technologie)
3. [Prérequis d'installation](#prérequis-dinstallation)
4. [Étape 1: Configuration initiale](#étape-1-configuration-initiale)
5. [Étape 2: Installation des dépendances](#étape-2-installation-des-dépendances)
6. [Étape 3: Configuration MySQL](#étape-3-configuration-mysql)
7. [Étape 4: Migrations Django](#étape-4-migrations-django)
8. [Étape 5: Création des données initiales](#étape-5-création-des-données-initiales)
9. [Étape 6: Configuration du frontend](#étape-6-configuration-du-frontend)
10. [Étape 7: Démarrage des serveurs](#étape-7-démarrage-des-serveurs)
11. [Vérifications et Tests](#vérifications-et-tests)
12. [Gestion des Utilisateurs](#gestion-des-utilisateurs)
13. [API Endpoints](#api-endpoints)
14. [Dépannage](#dépannage)

---

## Vue d'ensemble du projet

### 🎯 Objectif
SmartMeter est une plateforme complète de gestion et de monitoring de la consommation électrique avec:
- **Tableau de bord** pour les résidents
- **Panneau d'administration** pour les gestionnaires
- **Détection d'anomalies** via Hugging Face AI
- **Système d'alertes** automatisé
- **Chat IA** pour l'assistance aux utilisateurs
- **Import CSV** pour les données Kaggle

### 👥 Utilisateurs Cibles
- **ADMIN**: Gestionnaires avec accès à tous les foyers et données
- **RESIDENT**: Résidents avec accès limité à leur foyer uniquement

### 📦 Modèles de Données
| Modèle | Description | Relations |
|--------|-------------|-----------|
| User | Utilisateurs (ADMIN/RESIDENT) | FK → Foyer |
| Foyer | Ménages/propriétés | 1→N Consommation, 1→N Utilisateurs |
| Consommation | Mesures de consommation (kWh) | FK → Foyer, 1→1 Anomalie |
| Anomalie | Anomalies détectées | FK → Consommation |
| Alerte | Alertes générées | FK → Anomalie |
| ConversationIA | Chats avec l'IA | FK → User |
| ActionLog | Audit trail | FK → User |

---

## Architecture et Technologie

### Backend
```
Framework:          Django 5.0
API:                Django REST Framework
Authentification:   JWT (Simple JWT)
Base de Données:    MySQL 8.0+ (Production) / SQLite (Dev)
Serveur:            Gunicorn (Production) / Runserver (Dev)
Python:             3.8+
```

### Frontend
```
Framework:          Next.js 14 (TypeScript)
Styling:            Tailwind CSS
Animations:         Framer Motion
Composants UI:      Shadcn/ui, Lucide Icons
State Management:   React Context + Hooks
Requêtes API:       Fetch API avec JWT
```

### Stack Complet
```
BACKEND STACK:
├── Django 5.0 (Web Framework)
├── DRF (REST API)
├── Simple JWT (Authentication)
├── PyMySQL (MySQL Driver)
├── django-cors-headers (CORS)
├── django-filter (Filtering)
├── pandas (CSV Processing)
├── requests (HTTP)
└── gunicorn (Production Server)

FRONTEND STACK:
├── Next.js 14 (Framework)
├── TypeScript (Type Safety)
├── Tailwind CSS (Styling)
├── Framer Motion (Animations)
├── Axios/Fetch (API Calls)
├── React Context (State)
└── Lucide React (Icons)

DATABASE:
├── MySQL 8.0+ (Primary)
├── Charset: utf8mb4
└── Collation: utf8mb4_unicode_ci

TOOLS:
├── Git (Version Control)
├── Postman (API Testing)
├── MySQL Workbench (DB Admin)
└── VS Code / PyCharm (IDE)
```

---

## Prérequis d'installation

### 1. Système d'Exploitation
- Windows 10+ / macOS 10.14+ / Linux (Ubuntu 18.04+)

### 2. Logiciels Requis
```bash
# Vérifiez les versions installées:
python --version          # Python 3.8+
node --version           # Node.js 16+
npm --version            # npm 8+
mysql --version          # MySQL 8.0+
git --version            # Git 2.0+
```

### 3. Installation

#### Windows PowerShell (Recommandé)
```powershell
# 1. Installer Python (depuis python.org)
# 2. Installer Node.js (depuis nodejs.org)
# 3. Installer MySQL (depuis mysql.com)
# 4. Installer Git (depuis git-scm.com)

# Vérifier l'installation
python --version
node --version
npm --version
mysql --version
```

#### Linux/macOS
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.10 python3-pip nodejs mysql-server git

# macOS
brew install python@3.10 node mysql git
```

### 4. Localiser le Répertoire du Projet
```
C:\Users\{USERNAME}\Desktop\Electrecity\
├── SMART-METER-BACKEND/   ← Django Backend
└── SMART-METER-FRONTEND/  ← Next.js Frontend
```

---

## Étape 1: Configuration initiale

### 1.1 Préparer l'Environnement de Travail

#### Windows PowerShell
```powershell
# Naviguer au répertoire
cd "C:\Users\omrac\Desktop\Electrecity"

# Créer l'environnement virtuel Python
python -m venv .venv

# Activer l'environnement virtuel
.\.venv\Scripts\Activate.ps1

# Si vous avez une erreur d'exécution, exécutez d'abord:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

#### Linux/macOS
```bash
cd ~/Desktop/Electrecity

# Créer l'environnement virtuel
python3 -m venv .venv

# Activer l'environnement
source .venv/bin/activate
```

### 1.2 Configurer les Variables d'Environnement

```bash
# Créer le fichier .env dans SMART-METER-BACKEND/
cd SMART-METER-BACKEND

# Windows: Créer le fichier .env
cat > .env << 'EOF'
DEBUG=False
SECRET_KEY=django-insecure-dev-key-change-this-to-50-chars-minimum
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.mysql
DB_NAME=smartmeter_db
DB_USER=smartmeter_user
DB_PASSWORD=SmartMeter@2026
DB_HOST=localhost
DB_PORT=3306

JWT_SECRET=smartmeter-jwt-secret-key-min-32-chars
JWT_EXPIRATION_HOURS=24

CORS_ALLOWED_ORIGINS=http://localhost:3000
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

HUGGINGFACE_API_KEY=your_huggingface_key_here

LOG_LEVEL=INFO
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
EOF
```

**⚠️ IMPORTANT**: Avant la production, changez:
- `SECRET_KEY` → caractères aléatoires (50+ chars)
- `DB_PASSWORD` → mot de passe fort
- `DEBUG` → False
- `SECURE_SSL_REDIRECT` → True

---

## Étape 2: Installation des dépendances

### 2.1 Backend Django

```powershell
# Windows PowerShell - dans SMART-METER-BACKEND/
.\.venv\Scripts\Activate.ps1

# Installer les dépendances Python
pip install --upgrade pip setuptools wheel
pip install -r backend/requirements.txt

# Vérifier l'installation
python -m django --version
```

**Contenu de `requirements.txt`:**
```
# Django
Django==5.0
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1

# Database
PyMySQL==1.1.1

# CORS
django-cors-headers==4.3.1

# Filtering
django-filter==23.5

# Environment variables
python-decouple==3.8

# HTTP requests
requests==2.31.0

# Data processing
pandas==2.1.0

# Production server
gunicorn==21.2.0

# Monitoring
sentry-sdk==1.40.4

# Development
black==24.1.1
flake8==7.0.0
isort==5.13.2
django-extensions==3.2.3
```

### 2.2 Frontend Next.js

```powershell
# Windows - dans SMART-METER-FRONTEND/
cd ..\SMART-METER-FRONTEND

npm install

# Vérifier l'installation
npm --version
npx next --version
```

---

## Étape 3: Configuration MySQL

### 3.1 Créer la Base de Données et l'Utilisateur

#### Via MySQL CLI
```bash
# 1. Connectez-vous à MySQL
mysql -u root -p

# 2. Exécutez ces commandes SQL:
```

**SQL Script:**
```sql
-- Créer la base de données
CREATE DATABASE smartmeter_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Créer l'utilisateur dédié
CREATE USER 'smartmeter_user'@'localhost' 
IDENTIFIED BY 'SmartMeter@2026';

-- Accorder les privilèges
GRANT ALL PRIVILEGES ON smartmeter_db.* 
TO 'smartmeter_user'@'localhost';

-- Appliquer les modifications
FLUSH PRIVILEGES;

-- Vérifier
SHOW DATABASES;
SELECT user, host FROM mysql.user WHERE user='smartmeter_user';
```

#### Via MySQL Workbench
1. Connectez-vous en tant que root
2. Créez une nouvelle base de données nommée `smartmeter_db`
3. Utilisez le charset `utf8mb4` et la collation `utf8mb4_unicode_ci`
4. Créez un nouvel utilisateur `smartmeter_user`
5. Assignez tous les privilèges sur `smartmeter_db`

### 3.2 Tester la Connexion

```bash
# Vérifier que la connexion fonctionne
mysql -u smartmeter_user -p -h localhost smartmeter_db

# Devrait afficher:
# mysql> 
# (aucune erreur de connexion)

# Pour quitter:
# mysql> exit
```

### 3.3 Configuration dans Django

Le fichier `settings.py` utilise les variables d'environnement:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'smartmeter_db'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'CHARSET': 'utf8mb4',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'autocommit': True,
        },
    }
}
```

**Assurez-vous que le fichier `.env` contient:**
```
DB_ENGINE=django.db.backends.mysql
DB_NAME=smartmeter_db
DB_USER=smartmeter_user
DB_PASSWORD=SmartMeter@2026
DB_HOST=localhost
DB_PORT=3306
```

---

## Étape 4: Migrations Django

### 4.1 Appliquer les Migrations

```powershell
# Windows - dans SMART-METER-BACKEND/
cd backend

# Vérifier l'état des migrations
python manage.py showmigrations

# Appliquer toutes les migrations
python manage.py migrate

# Vous devriez voir:
# Operations to perform:
#   Apply all migrations: users, energy, ...
# Running migrations:
#   Applying users.0001_initial... OK
#   Applying energy.0001_initial... OK
#   ... (5 migrations totales)
```

### 4.2 Vérifier le Schéma MySQL

```sql
-- Connectez-vous à MySQL et vérifiez les tables
USE smartmeter_db;
SHOW TABLES;

-- Tables attendues:
-- +-----------------------------------+
-- | Tables_in_smartmeter_db           |
-- +-----------------------------------+
-- | django_migrations                 |
-- | django_content_type               |
-- | django_admin_log                  |
-- | users_user                        |
-- | energy_foyer                      |
-- | energy_consommation               |
-- | energy_anomalie                   |
-- | energy_alerte                     |
-- | energy_conversationIA             |
-- | energy_actionlog                  |
-- +-----------------------------------+

-- Vérifier la structure d'une table:
DESCRIBE users_user;
DESCRIBE energy_foyer;
```

### 4.3 Créer un Super-Utilisateur (Administrateur)

```powershell
# Dans le répertoire SMART-METER-BACKEND/backend/
python manage.py createsuperuser

# Remplir les informations:
# Username: admin
# Email: admin@smartmeter.local
# Password: Enter123!@# (changez en production)
# Password (again): Enter123!@#
```

---

## Étape 5: Création des données initiales

### 5.1 Importer les Données Kaggle

#### Option 1: Utiliser le CSV fourni (example_import.csv)

```bash
# Le fichier example_import.csv contient des données de test
# Structure: LCLid, DateTime, KWH/hh, anomaly_label

# Pour importer via l'API:
# Utilisez Postman ou curl
```

#### Option 2: Créer des données manuellement

```bash
# Accéder à Django Shell
python manage.py shell

# Importer les modèles
from energy.models import Foyer, Consommation
from users.models import User
from django.utils import timezone
from datetime import datetime, timedelta

# 1. Créer un foyer
foyer = Foyer.objects.create(
    numero_foyer='LCL001',
    adresse='123 Rue de la Paix',
    code_postal='75001',
    ville='Paris',
    puissance_souscrite=6.0
)

# 2. Créer un utilisateur résident
user = User.objects.create_user(
    username='resident1',
    email='resident1@example.com',
    password='SecurePassword123!',
    role='RESIDENT',
    foyer=foyer,
    first_name='Jean',
    last_name='Dupont'
)

# 3. Créer des enregistrements de consommation
today = timezone.now()
for i in range(10):
    Consommation.objects.create(
        foyer=foyer,
        timestamp=today - timedelta(hours=i),
        kwh=2.5 + (i * 0.1),
        temperature=20.0,
        anomaly_label=None
    )

# Vérifier
print(f"Foyer créé: {foyer}")
print(f"Utilisateur créé: {user}")
print(f"Enregistrements: {Consommation.objects.filter(foyer=foyer).count()}")

# Quitter
exit()
```

### 5.2 Créer des Utilisateurs Admin et Residents

#### Via Django Admin Interface

```bash
# Démarrer le serveur Django
python manage.py runserver

# Accéder à http://localhost:8000/admin
# Username: admin
# Password: (celui créé à l'étape 4.3)

# Créer un nouvel utilisateur:
# 1. Allez sur "Users"
# 2. Cliquez "Add User"
# 3. Remplissez:
#    - Username: resident2
#    - Password: SecurePassword123!
#    - First Name: Marie
#    - Last Name: Martin
# 4. Sauvegardez et retournez à la liste
# 5. Cliquez sur l'utilisateur et changez:
#    - Role: RESIDENT
#    - Foyer: (sélectionnez un foyer)
# 6. Sauvegardez
```

#### Via le Django Shell

```bash
python manage.py shell

from users.models import User
from energy.models import Foyer

# Créer un utilisateur ADMIN
admin = User.objects.create_user(
    username='admin2',
    email='admin2@smartmeter.local',
    password='AdminPassword123!',
    role='ADMIN',
    first_name='Admin',
    last_name='User'
)

# Créer un utilisateur RESIDENT
foyer = Foyer.objects.first()  # Ou créez un foyer
resident = User.objects.create_user(
    username='resident3',
    email='resident3@smartmeter.local',
    password='ResidentPassword123!',
    role='RESIDENT',
    foyer=foyer,
    first_name='Sophie',
    last_name='Rousseau'
)

# Afficher les utilisateurs créés
print("ADMINS:")
for admin in User.objects.filter(role='ADMIN'):
    print(f"  - {admin.username} ({admin.email})")

print("\nRESIDENTS:")
for resident in User.objects.filter(role='RESIDENT'):
    print(f"  - {resident.username} ({admin.email}) → Foyer: {resident.foyer}")

exit()
```

### 5.3 Consulter les Utilisateurs et Leurs Mots de Passe (ADMIN)

#### ⚠️ ATTENTION: Les mots de passe sont hashés en base de données
```sql
-- Les mots de passe ne sont PAS stockés en clair pour des raisons de sécurité
-- Ils sont hashés avec l'algorithme PBKDF2-SHA256

USE smartmeter_db;

-- Afficher tous les utilisateurs
SELECT id, username, email, role, foyer_id, is_active, is_staff 
FROM users_user 
ORDER BY role DESC, username;

-- Afficher les détails d'un utilisateur spécifique
SELECT * FROM users_user 
WHERE username = 'admin';

-- Afficher le nombre d'utilisateurs par rôle
SELECT role, COUNT(*) as count 
FROM users_user 
GROUP BY role;
```

#### Via Django Admin
```
http://localhost:8000/admin/users/user/
```

#### Via Python Shell
```bash
python manage.py shell

from users.models import User
from django.contrib.auth.hashers import make_password

# Lister tous les utilisateurs
print("=== TOUS LES UTILISATEURS ===")
for user in User.objects.all():
    print(f"ID: {user.id}")
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"Rôle: {user.role}")
    print(f"Foyer: {user.foyer}")
    print(f"Actif: {user.is_active}")
    print(f"Password Hash: {user.password}")  # Hashé, ne montre pas le mot de passe
    print("-" * 40)

# Si vous avez OUBLIÉ un mot de passe, le réinitialiser:
user = User.objects.get(username='admin')
user.set_password('NewPassword123!')
user.save()
print(f"Mot de passe réinitialisé pour {user.username}")

exit()
```

---

## Étape 6: Configuration du frontend

### 6.1 Configurer Next.js

```powershell
# Dans SMART-METER-FRONTEND/
cd ..\SMART-METER-FRONTEND

# Créer le fichier .env.local
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_API_BASE=http://localhost:8000
EOF

# Ou créer le fichier manuellement avec ce contenu:
```

**Fichier `.env.local`:**
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

### 6.2 Structure du Frontend

```
SMART-METER-FRONTEND/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Layout principal
│   │   ├── page.tsx            # Page d'accueil
│   │   ├── auth/               # Pages d'authentification
│   │   ├── dashboard/          # Dashboard résident
│   │   └── admin/              # Panneau admin
│   ├── components/
│   │   ├── auth/               # Composants auth
│   │   ├── layout/             # Composants layout
│   │   ├── sections/           # Sections réutilisables
│   │   └── ui/                 # Composants UI
│   ├── context/
│   │   └── AuthContext.tsx     # Context d'authentification
│   └── hooks/
│       ├── useSecureApi.ts     # Hook API avec JWT
│       ├── useDashboard.ts     # Hook dashboard
│       └── ...
├── public/                     # Fichiers statiques
├── next.config.ts
├── tsconfig.json
└── tailwind.config.ts
```

### 6.3 Clés Principales du Frontend

**Context d'Authentification (`src/context/AuthContext.tsx`):**
- Gère JWT tokens (access + refresh)
- Stockage sécurisé dans localStorage
- Partage l'état auth à tous les composants

**Hook API Sécurisé (`src/hooks/useSecureApi.ts`):**
- Ajoute automatiquement le JWT aux requêtes
- Gère les erreurs 401 (refresh token)
- Fallback vers login si expiration

**Pages Principales:**
- `/auth/login` - Formulaire de connexion
- `/dashboard` - Dashboard résident
- `/admin` - Overview admin
- `/admin/anomalies` - Gestion des anomalies
- `/admin/alertes` - Gestion des alertes

---

## Étape 7: Démarrage des serveurs

### 7.1 Démarrer le Backend Django

#### Windows PowerShell
```powershell
# Navigate to backend
cd "C:\Users\omrac\Desktop\Electrecity\SMART-METER-BACKEND"

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Navigate to backend directory
cd backend

# Start Django development server
python manage.py runserver 0.0.0.0:8000

# Vous devriez voir:
# Starting development server at http://127.0.0.1:8000/
# Quit the server with CTRL-BREAK.
```

#### Linux/macOS
```bash
cd ~/Desktop/Electrecity/SMART-METER-BACKEND

source .venv/bin/activate

cd backend

python manage.py runserver 0.0.0.0:8000
```

#### 🌐 Accès Backend
- API Admin: http://localhost:8000/admin/
- API Root: http://localhost:8000/api/
- Docs: http://localhost:8000/api/ (si swagger installé)

### 7.2 Démarrer le Frontend Next.js

#### Windows PowerShell (Nouveau Terminal)
```powershell
# Navigate to frontend
cd "C:\Users\omrac\Desktop\Electrecity\SMART-METER-FRONTEND"

# Install dependencies if not already done
npm install

# Start development server
npm run dev

# Vous devriez voir:
# ▲ Next.js 14.0.0
# - Local:        http://localhost:3000
# - Environments: .env.local
```

#### Linux/macOS
```bash
cd ~/Desktop/Electrecity/SMART-METER-FRONTEND

npm run dev
```

#### 🌐 Accès Frontend
- Application: http://localhost:3000/
- Page de connexion: http://localhost:3000/auth/login
- Dashboard: http://localhost:3000/dashboard

### 7.3 Accès Complet (Tous les Services)

| Service | URL | Accès |
|---------|-----|-------|
| **Frontend** | http://localhost:3000 | ✅ Public |
| **Login** | http://localhost:3000/auth/login | ✅ Public |
| **Dashboard** | http://localhost:3000/dashboard | 🔐 RESIDENT |
| **Admin Panel** | http://localhost:3000/admin | 🔐 ADMIN |
| **Backend API** | http://localhost:8000/api | ✅ Public (auth required) |
| **Admin Interface** | http://localhost:8000/admin | 🔐 ADMIN |
| **Database** | localhost:3306 | 🔐 MySQL |

---

## Vérifications et Tests

### ✅ Checklist de Démarrage

#### 1. Backend Django
```powershell
# Vérifier que le serveur est lancé
# Devrait afficher: "Starting development server at http://127.0.0.1:8000/"

# Test API root (dans un navigateur ou curl)
curl http://localhost:8000/api/

# Résultat attendu: JSON avec les endpoints disponibles
```

#### 2. Frontend Next.js
```powershell
# Vérifier que le serveur est lancé
# Devrait afficher: "- Local: http://localhost:3000"

# Accéder à http://localhost:3000
# Devrait afficher la page d'accueil
```

#### 3. Base de Données MySQL
```bash
# Vérifier les tables
mysql -u smartmeter_user -p smartmeter_db -e "SHOW TABLES;"

# Résultat: Toutes les tables présentes
# - django_migrations
# - users_user
# - energy_foyer
# - energy_consommation
# - energy_anomalie
# - energy_alerte
# - energy_conversationIA
# - energy_actionlog
```

#### 4. Authentification
```powershell
# Test login via API
$loginData = @{
    username = "admin"
    password = "Enter123!@#"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/api/auth/login/" `
    -Method POST `
    -ContentType "application/json" `
    -Body $loginData

# Résultat: Token JWT dans la réponse
# $response.Content | ConvertFrom-Json | Select-Object access, refresh
```

### 🧪 Tests Manuels (Postman)

**1. Login - Obtenir un Token JWT**
```
POST http://localhost:8000/api/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "Enter123!@#"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": { "id": 1, "username": "admin", "role": "ADMIN" }
}
```

**2. Utiliser le Token pour Accéder aux Endpoints**
```
GET http://localhost:8000/api/energy/foyers/
Authorization: Bearer {access_token}

Response: Liste de tous les foyers (si ADMIN)
```

**3. Créer un Foyer (ADMIN uniquement)**
```
POST http://localhost:8000/api/energy/foyers/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "numero_foyer": "LCL002",
  "adresse": "456 Rue de la République",
  "code_postal": "75002",
  "ville": "Paris",
  "puissance_souscrite": 6.0
}
```

---

## Gestion des Utilisateurs

### 📊 Tous les Utilisateurs et Leurs Accès

#### ADMIN Users
```sql
SELECT 
    u.id,
    u.username,
    u.email,
    u.first_name,
    u.last_name,
    u.role,
    u.is_active,
    u.is_staff,
    u.date_joined
FROM users_user u
WHERE u.role = 'ADMIN'
ORDER BY u.date_joined DESC;
```

#### RESIDENT Users
```sql
SELECT 
    u.id,
    u.username,
    u.email,
    u.first_name,
    u.last_name,
    u.role,
    f.numero_foyer as 'Foyer Assigné',
    u.is_active,
    u.date_joined
FROM users_user u
LEFT JOIN energy_foyer f ON u.foyer_id = f.id
WHERE u.role = 'RESIDENT'
ORDER BY f.numero_foyer, u.username;
```

#### Tous les Utilisateurs
```sql
SELECT 
    u.id,
    u.username,
    u.email,
    u.role,
    f.numero_foyer,
    u.is_active,
    u.date_joined
FROM users_user u
LEFT JOIN energy_foyer f ON u.foyer_id = f.id
ORDER BY u.role DESC, u.username;
```

### 🔐 Ajouter un Nouvel Utilisateur

```python
# Via Django Shell
python manage.py shell

from users.models import User
from energy.models import Foyer

# 1. Créer un ADMIN
admin_user = User.objects.create_user(
    username='new_admin',
    email='new_admin@smartmeter.local',
    password='SecureAdminPassword123!',
    first_name='Nouveau',
    last_name='Admin',
    role='ADMIN'
)

# 2. Créer un RESIDENT
foyer = Foyer.objects.get(numero_foyer='LCL001')
resident_user = User.objects.create_user(
    username='new_resident',
    email='new_resident@smartmeter.local',
    password='SecureResidentPassword123!',
    first_name='Nouveau',
    last_name='Résident',
    role='RESIDENT',
    foyer=foyer
)

print(f"Admin créé: {admin_user.username}")
print(f"Résident créé: {resident_user.username} → {resident_user.foyer}")

exit()
```

### 🔑 Réinitialiser un Mot de Passe

```python
# Via Django Shell
python manage.py shell

from users.models import User

# Récupérer l'utilisateur
user = User.objects.get(username='admin')

# Réinitialiser le mot de passe
new_password = 'NewPassword123!'
user.set_password(new_password)
user.save()

print(f"Mot de passe réinitialisé pour {user.username}")
print(f"Nouveau mot de passe: {new_password}")

exit()
```

### 🗑️ Supprimer un Utilisateur

```python
# Via Django Shell
python manage.py shell

from users.models import User

# Supprimer un utilisateur
user = User.objects.get(username='old_resident')
username = user.username
user.delete()

print(f"Utilisateur {username} supprimé")

exit()
```

### 📈 Statistiques des Utilisateurs

```sql
-- Nombre d'utilisateurs par rôle
SELECT role, COUNT(*) as 'Nombre' 
FROM users_user 
GROUP BY role;

-- Utilisateurs actifs vs inactifs
SELECT 
    role, 
    is_active, 
    COUNT(*) as 'Nombre'
FROM users_user
GROUP BY role, is_active;

-- Utilisateurs créés par mois
SELECT 
    DATE_FORMAT(date_joined, '%Y-%m') as 'Mois',
    role,
    COUNT(*) as 'Nombre'
FROM users_user
GROUP BY DATE_FORMAT(date_joined, '%Y-%m'), role
ORDER BY DATE_FORMAT(date_joined, '%Y-%m') DESC;
```

---

## API Endpoints

### 🔐 Authentification

| Méthode | Endpoint | Accès | Description |
|---------|----------|-------|-------------|
| POST | `/api/auth/login/` | Public | Connexion et obtention JWT |
| POST | `/api/auth/logout/` | Authentifié | Déconnexion |
| GET | `/api/auth/profile/` | Authentifié | Profil de l'utilisateur connecté |
| POST | `/api/auth/refresh/` | Public | Renouveler le access token |

### 📊 Foyers (Households)

| Méthode | Endpoint | Accès | Description |
|---------|----------|-------|-------------|
| GET | `/api/energy/foyers/` | Admin=tous, Resident=sien | Lister les foyers |
| GET | `/api/energy/foyers/{id}/` | Admin=tous, Resident=sien | Détails d'un foyer |
| POST | `/api/energy/foyers/` | Admin | Créer un foyer |
| PUT/PATCH | `/api/energy/foyers/{id}/` | Admin | Modifier un foyer |
| DELETE | `/api/energy/foyers/{id}/` | Admin | Supprimer un foyer |
| GET | `/api/energy/admin/foyers/` | Admin | Lister tous les foyers |

### ⚡ Consommation (Energy Consumption)

| Méthode | Endpoint | Accès | Description |
|---------|----------|-------|-------------|
| GET | `/api/energy/consommations/` | Admin=tous, Resident=sien | Lister les consommations |
| GET | `/api/energy/consommations/{id}/` | Admin=tous, Resident=sien | Détails d'une consommation |
| POST | `/api/energy/consommations/` | Admin | Créer une consommation |
| GET | `/api/energy/consommations/kpi/` | Authentifié | KPIs de consommation |

### 🚨 Anomalies

| Méthode | Endpoint | Accès | Description |
|---------|----------|-------|-------------|
| GET | `/api/energy/anomalies/` | Admin=tous, Resident=sien | Lister les anomalies |
| GET | `/api/energy/anomalies/{id}/` | Admin=tous, Resident=sien | Détails d'une anomalie |
| PATCH | `/api/energy/anomalies/{id}/marquer_consultee/` | Authentifié | Marquer comme consultée |
| PATCH | `/api/energy/anomalies/{id}/marquer_acquittee/` | Authentifié | Marquer comme acquittée |

### 🔔 Alertes (Alerts)

| Méthode | Endpoint | Accès | Description |
|---------|----------|-------|-------------|
| GET | `/api/energy/alertes/` | Admin=tous, Resident=sien | Lister les alertes |
| GET | `/api/energy/alertes/{id}/` | Admin=tous, Resident=sien | Détails d'une alerte |
| PATCH | `/api/energy/alertes/{id}/acquitter/` | Authentifié | Acquitter une alerte |
| GET | `/api/energy/alertes/archivees/` | Authentifié | Lister les alertes archivées |

### 💬 Conversations IA

| Méthode | Endpoint | Accès | Description |
|---------|----------|-------|-------------|
| GET | `/api/energy/conversations-ia/` | Authentifié | Lister les conversations |
| POST | `/api/energy/conversations-ia/` | Authentifié | Créer une conversation |
| GET | `/api/energy/conversations-ia/{id}/` | Authentifié | Détails d'une conversation |

### 📤 Import de Données

| Méthode | Endpoint | Accès | Description |
|---------|----------|-------|-------------|
| POST | `/api/energy/import-csv/` | Admin | Importer un CSV Kaggle |
| GET | `/api/energy/import-csv/status/` | Admin | Statut de l'import |

### 👥 Gestion des Utilisateurs (Admin)

| Méthode | Endpoint | Accès | Description |
|---------|----------|-------|-------------|
| GET | `/api/users/` | Admin | Lister les utilisateurs |
| GET | `/api/users/{id}/` | Admin | Détails d'un utilisateur |
| POST | `/api/users/` | Admin | Créer un utilisateur |
| PUT/PATCH | `/api/users/{id}/` | Admin | Modifier un utilisateur |
| DELETE | `/api/users/{id}/` | Admin | Supprimer un utilisateur |
| GET | `/api/energy/admin/residents/` | Admin | Lister tous les résidents |
| GET | `/api/energy/admin/residents/{id}/` | Admin | Détails d'un résident |
| PATCH | `/api/energy/admin/residents/{id}/assign-foyer/` | Admin | Assigner un foyer |

---

## Dépannage

### ❌ Erreur: "Connection refused" - MySQL

```
ERROR 2003 (HY000): Can't connect to MySQL server on 'localhost' (10061)
```

**Solution:**
```powershell
# 1. Vérifier que MySQL est démarré
Get-Service -Name MySQL80

# 2. Si le service n'est pas lancé, le démarrer
Start-Service -Name MySQL80

# 3. Vérifier que la base de données existe
mysql -u root -p
> SHOW DATABASES;
> USE smartmeter_db;
```

### ❌ Erreur: "No such module" - Django

```
ModuleNotFoundError: No module named 'django'
```

**Solution:**
```powershell
# Vérifier l'activation du venv
.\.venv\Scripts\Activate.ps1

# Réinstaller les dépendances
pip install -r backend/requirements.txt
```

### ❌ Erreur: "Permission denied" - Frontend

```
npm ERR! Error: EACCES: permission denied
```

**Solution:**
```powershell
# Windows: Redémarrer PowerShell en Admin
# Puis réessayer:
npm install
npm run dev
```

### ❌ Erreur: "CORS" - Frontend vers Backend

```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution:**
```python
# Vérifier settings.py:
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
]

# Redémarrer le backend:
python manage.py runserver
```

### ❌ Erreur: JWT Token Expired

```
{"detail": "Token is invalid or expired"}
```

**Solution:**
```javascript
// Dans le hook useSecureApi (frontend):
// 1. Envoyer une requête avec le refresh token
// 2. Obtenir un nouveau access token
// 3. Réessayer la requête originale
// 4. Si échec, rediriger vers login
```

### ❌ Erreur: "Can't connect to local MySQL server"

```
(2003, "Can't connect to MySQL server on 'localhost' (10061)")
```

**Solutions:**
```powershell
# 1. Vérifier que MySQL est en écoute sur le port 3306
netstat -ano | findstr :3306

# 2. Vérifier les credentials dans .env
cat .env | findstr DB_

# 3. Tester la connexion directement
mysql -u smartmeter_user -p -h localhost

# 4. Si problème persiste, réinitialiser MySQL
net stop MySQL80
net start MySQL80
```

### ⚠️ Erreur: Migrations échouées

```
ERROR: Unable to create tables
```

**Solution:**
```powershell
# 1. Vérifier les migrations manquantes
python manage.py showmigrations

# 2. Créer les migrations
python manage.py makemigrations

# 3. Appliquer les migrations
python manage.py migrate --noinput

# 4. Vérifier l'état
python manage.py showmigrations
```

### ✅ Commandes Utiles de Dépannage

```bash
# Vérifier Django
python manage.py check

# Afficher l'état des migrations
python manage.py showmigrations

# Lister toutes les routes API
python manage.py show_urls

# Accéder au shell Django
python manage.py shell

# Vérifier la version Django
python -m django --version

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Vider le cache
python manage.py clear_cache

# Créer une sauvegarde de la base de données
mysqldump -u smartmeter_user -p smartmeter_db > backup.sql

# Restaurer une sauvegarde
mysql -u smartmeter_user -p smartmeter_db < backup.sql
```

---

## Production Deployment

### 🚀 Préparation pour Production

#### 1. Variables d'Environnement
```bash
# .env (Production)
DEBUG=False
SECRET_KEY=your-super-secret-key-with-50-chars-minimum-random-generated
ALLOWED_HOSTS=smartmeter.yourcompany.com,www.smartmeter.yourcompany.com

DB_ENGINE=django.db.backends.mysql
DB_NAME=smartmeter_prod
DB_USER=smartmeter_prod_user
DB_PASSWORD=VerySecurePasswordWithSpecialChars123!@#$%
DB_HOST=db.smartmeter.yourcompany.com
DB_PORT=3306

JWT_EXPIRATION_HOURS=24

CORS_ALLOWED_ORIGINS=https://smartmeter.yourcompany.com

SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
CSRF_COOKIE_HTTPONLY=True

SENTRY_DSN=your-sentry-dsn-here
```

#### 2. Collecte des Fichiers Statiques
```bash
python manage.py collectstatic --noinput
```

#### 3. Lancer avec Gunicorn
```bash
# Installation
pip install gunicorn

# Lancer le serveur
gunicorn wsgi:application --bind 0.0.0.0:8000 --workers 4

# Avec systemd (Linux)
# Créer /etc/systemd/system/smartmeter.service
[Unit]
Description=SmartMeter Django Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/smartmeter
ExecStart=/path/to/venv/bin/gunicorn wsgi:application --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target

# Activer et démarrer
sudo systemctl enable smartmeter
sudo systemctl start smartmeter
```

#### 4. Nginx Configuration
```nginx
upstream smartmeter {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name smartmeter.yourcompany.com;

    # Rediriger vers HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name smartmeter.yourcompany.com;

    # SSL
    ssl_certificate /etc/ssl/certs/smartmeter.crt;
    ssl_certificate_key /etc/ssl/private/smartmeter.key;

    # Static files
    location /static/ {
        alias /path/to/static/;
    }

    # Media files
    location /media/ {
        alias /path/to/media/;
    }

    # API
    location / {
        proxy_pass http://smartmeter;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Résumé Rapide (TL;DR)

```bash
# 1. Backend Setup
cd SMART-METER-BACKEND
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
pip install -r backend/requirements.txt

# 2. Database Setup (MySQL)
mysql -u root -p
# CREATE DATABASE smartmeter_db CHARACTER SET utf8mb4;
# CREATE USER 'smartmeter_user'@'localhost' IDENTIFIED BY 'SmartMeter@2026';
# GRANT ALL PRIVILEGES ON smartmeter_db.* TO 'smartmeter_user'@'localhost';

# 3. Django Setup
cd backend
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# 4. Frontend Setup (Nouveau Terminal)
cd SMART-METER-FRONTEND
npm install
npm run dev

# 5. Accéder
# http://localhost:3000 (Frontend)
# http://localhost:8000/admin (Django Admin)
```

---

## 📚 Documentation Supplémentaire

- **Backend**: `/backend/README.md`
- **Frontend**: `/SMART-METER-FRONTEND/README.md`
- **MySQL Setup**: `./MYSQL_DATABASE_SETUP.md`
- **Installation**: `./INSTALLATION_GUIDE.md`

---

## ✅ Checklist Finale

- [x] Database SQLite cleared
- [x] MySQL database created
- [x] Unnecessary files removed
- [x] Django migrations ready
- [x] User models configured
- [x] Authentication JWT working
- [x] Admin interface ready
- [x] Frontend Next.js configured
- [x] API endpoints documented
- [x] All 7 database models created
- [x] Production deployment guide ready

---

**Version**: 1.0.0  
**Date**: 13 mai 2026  
**Status**: ✅ Production Ready  
**Support**: Email: support@smartmeter.local

---

## 📞 Quick Support

| Problème | Solution |
|----------|----------|
| MySQL connection refused | Vérifier que MySQL est lancé: `net start MySQL80` |
| Django module not found | Activer venv: `.\.venv\Scripts\Activate.ps1` |
| Port already in use | Changer le port: `python manage.py runserver 8001` |
| CORS error | Vérifier CORS_ALLOWED_ORIGINS dans settings.py |
| Token expired | Utiliser le refresh token pour obtenir un nouveau access token |

---

**Fin du Rapport | Bonne implémentation! 🚀**

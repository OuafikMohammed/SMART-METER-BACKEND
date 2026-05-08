# SmartMeter Backend - Guide d'Installation Complet

## 📋 Prérequis

- Python 3.10+
- MySQL 8.0+
- pip / virtualenv
- Git (optionnel)

## 🚀 Installation Étape par Étape

### 1. Créer la structure des applications

```bash
cd backend

# Créer les dossiers des applications
mkdir -p users/migrations energy/migrations static media logs templates

# Créer les fichiers __init__.py
touch users/__init__.py energy/__init__.py
touch users/migrations/__init__.py energy/migrations/__init__.py
```

### 2. Copier les fichiers source

Copier les contenus des fichiers suivants dans les emplacements appropriés:

**File Structure:**
```
backend/
├── manage.py
├── wsgi.py                      ← À créer
├── settings.py                  ← À remplacer
├── urls.py                      ← À créer  
├── permissions.py               ← À créer
├── utils_logging.py             ← À créer
├── requirements.txt             ← À créer
├── .env.example                 ← À créer
│
├── users/
│   ├── __init__.py
│   ├── apps.py                  ← À créer
│   ├── models.py                ← À créer
│   ├── admin.py                 ← À créer
│   ├── views.py                 ← À créer
│   ├── serializers.py           ← À créer
│   ├── permissions.py           ← À créer
│   └── migrations/
│       └── __init__.py
│
└── energy/
    ├── __init__.py
    ├── apps.py                  ← À créer
    ├── models.py                ← À créer
    ├── admin.py                 ← À créer
    ├── views.py                 ← À créer
    ├── serializers.py           ← À créer
    ├── urls.py                  ← À créer
    └── migrations/
        └── __init__.py
```

### 3. Installer les dépendances

```bash
# Créer un virtual environment
python -m venv venv

# Activer le virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Installer les packages
pip install -r requirements.txt
pip install mysql-connector-python  # ou mysqlclient
```

### 4. Configurer la base de données

#### Option A: Créer la BD MySQL manuellement

```sql
CREATE DATABASE smartmeter_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'smartmeter'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON smartmeter_db.* TO 'smartmeter'@'localhost';
FLUSH PRIVILEGES;
```

#### Option B: Ou utiliser les variables d'environnement

Créer un fichier `.env`:
```
DB_NAME=smartmeter_db
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306
DEBUG=True
SECRET_KEY=your-secret-key
```

### 5. Exécuter les migrations

```bash
# Créer les fichiers de migration
python manage.py makemigrations users
python manage.py makemigrations energy

# Appliquer les migrations
python manage.py migrate

# Vérifier les migrations
python manage.py showmigrations
```

### 6. Créer un superutilisateur

```bash
python manage.py createsuperuser

# Répondre aux questions:
# Username: admin
# Email: admin@smartmeter.local
# Password: (secure password)
# Password (again): (confirm password)
```

### 7. Tester le serveur

```bash
python manage.py runserver

# Accéder à:
# Admin: http://localhost:8000/admin
# API: http://localhost:8000/api/token/
```

## 🧪 Tests Initiaux

### 1. Obtenir un token JWT

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'

# Réponse:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2. Utiliser le token pour appeler l'API

```bash
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/foyers/
```

## 📁 Fichiers à créer

### 1. `users/apps.py`
```python
from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'Gestion des Utilisateurs'
```

### 2. `energy/apps.py`
```python
from django.apps import AppConfig

class EnergyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'energy'
    verbose_name = 'Gestion de l\'Énergie'
```

### 3. `users/admin.py`
```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('SmartMeter', {'fields': ('role', 'foyer')}),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'role', 'foyer', 'is_staff')
    list_filter = ('role', 'is_staff', 'foyer')
    search_fields = ('username', 'email', 'first_name', 'last_name')
```

### 4. `energy/admin.py`
```python
from django.contrib import admin
from .models import Foyer, Consommation, Anomalie, Alerte, ConversationIA, ActionLog

@admin.register(Foyer)
class FoyerAdmin(admin.ModelAdmin):
    list_display = ('numero_foyer', 'adresse', 'ville', 'puissance_souscrite', 'is_active')
    list_filter = ('is_active', 'ville', 'created_at')
    search_fields = ('numero_foyer', 'adresse', 'ville')

@admin.register(Consommation)
class ConsommationAdmin(admin.ModelAdmin):
    list_display = ('foyer', 'timestamp', 'kwh', 'temperature', 'anomaly_label')
    list_filter = ('foyer', 'timestamp', 'anomaly_label')
    search_fields = ('foyer__numero_foyer',)
    readonly_fields = ('timestamp', 'kwh')

@admin.register(Anomalie)
class AnomalieAdmin(admin.ModelAdmin):
    list_display = ('consommation', 'severite', 'score_confiance', 'statut', 'created_at')
    list_filter = ('severite', 'statut', 'created_at')
    search_fields = ('consommation__foyer__numero_foyer',)

@admin.register(Alerte)
class AlerteAdmin(admin.ModelAdmin):
    list_display = ('anomalie', 'acquittee', 'created_at')
    list_filter = ('acquittee', 'created_at')

@admin.register(ConversationIA)
class ConversationIAAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'timestamp')
    list_filter = ('utilisateur', 'timestamp')
    search_fields = ('utilisateur__username', 'question')

@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'action', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('utilisateur__username', 'action')
    readonly_fields = ('timestamp', 'utilisateur', 'action', 'details', 'ip_address')
```

## 🔍 Structure des Requêtes API

### Authentication
```
POST /api/token/
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Refresh Token
```
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## 📝 Règles de Gestion Implémentées

- **RG1**: Authentification obligatoire via JWT
- **RG2**: Chaque utilisateur a un rôle unique (RESIDENT/ADMIN)
- **RG3**: Contrôle d'accès selon le rôle
- **RG19**: Mots de passe hachés automatiquement
- **RG20**: Tous les actions tracées dans ActionLog

## 🐛 Dépannage

### Erreur: "django.db.utils.OperationalError"
Vérifier la connexion MySQL et les variables d'environnement DB_*

### Erreur: "ModuleNotFoundError: No module named 'mysql'"
Installer: `pip install mysqlclient`

### Erreur: "TABLES_NOT_FOUND"
Exécuter: `python manage.py migrate`

## 📚 Documentation Complète

- [Django 5 Documentation](https://docs.djangoproject.com/en/5.0/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [djangorestframework-simplejwt](https://github.com/jpadilla/django-rest-framework-simplejwt)

## 🚀 Déploiement Production

1. Mettre `DEBUG=False` dans `.env`
2. Changer `SECRET_KEY` par une clé sécurisée
3. Configurer `ALLOWED_HOSTS`
4. Utiliser `gunicorn` comme serveur WSGI
5. Configurer un proxy reversa (nginx)
6. Utiliser SSL/TLS
7. Configurer une base de données MySQL dédiée

Exemple `gunicorn`:
```bash
gunicorn wsgi:application --bind 0.0.0.0:8000 --workers 4
```

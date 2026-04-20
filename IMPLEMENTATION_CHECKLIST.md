# ✅ Checklist d'Implémentation SmartMeter

## 📋 Avant de Commencer

- [ ] Python 3.10+ installé (`python --version`)
- [ ] MySQL 8.0+ en local ou accès distant
- [ ] Virtualenv disponible
- [ ] Accès au dossier `backend/`

## 📁 Étape 1: Organiser les Fichiers (10 min)

### Créer la structure
```bash
cd d:\COURS_EMSI_3ANNEE_IIR\SMARTMETER\backend

mkdir users\migrations
mkdir energy\migrations
mkdir static media logs templates

# Créer __init__.py
copy nul users\__init__.py
copy nul users\migrations\__init__.py
copy nul energy\__init__.py
copy nul energy\migrations\__init__.py
```

### Copier les fichiers Python
```bash
# users app
copy ..\users_init.py users\__init__.py
copy ..\users_apps.py users\apps.py
copy ..\users_models.py users\models.py
copy ..\users_admin.py users\admin.py

# energy app
copy ..\energy_init.py energy\__init__.py
copy ..\energy_apps.py energy\apps.py
copy ..\energy_models.py energy\models.py
copy ..\energy_admin.py energy\admin.py
copy ..\energy_serializers.py energy\serializers.py
copy ..\energy_views.py energy\views.py
copy ..\energy_urls.py energy\urls.py

# root files
copy ..\settings.py settings.py
copy ..\urls.py urls.py
copy ..\permissions.py permissions.py
copy ..\utils_logging.py utils_logging.py
copy ..\wsgi.py wsgi.py
copy ..\requirements.txt requirements.txt
copy ..\\.env.example .env.example
```

## 📦 Étape 2: Installer les Dépendances (5 min)

```bash
# Créer virtual environment
python -m venv venv

# Activer (Windows)
venv\Scripts\activate

# Installer requirements
pip install -r requirements.txt

# Vérifier
pip list | findstr Django
```

**✓ Vérification:** Vous devez voir:
- Django 5.0
- djangorestframework 3.14.0
- djangorestframework-simplejwt 5.3.2
- mysqlclient 2.2.0

## 🗄️ Étape 3: Configurer la Base de Données (5 min)

### Option A: MySQL local
```sql
-- Dans MySQL Workbench ou cli MySQL:
CREATE DATABASE smartmeter_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'smartmeter'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON smartmeter_db.* TO 'smartmeter'@'localhost';
FLUSH PRIVILEGES;
```

### Option B: Utiliser variables d'environnement
```bash
# Créer .env dans backend/
DB_NAME=smartmeter_db
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
DEBUG=True
SECRET_KEY=django-insecure-dev-key
```

**✓ Vérification:** 
```bash
# Tester la connexion
python manage.py dbshell
# Doit afficher: "mysql> "
```

## 🔄 Étape 4: Créer les Migrations (5 min)

```bash
# Générer les migrations
python manage.py makemigrations users
python manage.py makemigrations energy

# Lister les migrations
python manage.py showmigrations

# Appliquer les migrations
python manage.py migrate

# Vérifier les tables MySQL
# SELECT * FROM information_schema.tables WHERE table_schema='smartmeter_db';
```

**✓ Vérification:** Vous devez voir:
```
[X] users.0001_initial
[X] energy.0001_initial
[X] auth
[X] contenttypes
[X] sessions
```

## 👤 Étape 5: Créer un Superuser (2 min)

```bash
python manage.py createsuperuser

# Répondre aux questions:
# Username: admin
# Email: admin@smartmeter.local
# Password: (entrer un mot de passe sécurisé)
# Password (again): (confirmer)
```

**✓ Vérification:**
```bash
python manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
admin = User.objects.filter(username='admin').first()
print(admin.role, admin.foyer)  # Doit afficher: RESIDENT None (ou ADMIN)
```

## 🚀 Étape 6: Tester le Serveur (5 min)

```bash
# Démarrer Django
python manage.py runserver

# Dans un autre terminal, tester les endpoints:

# 1. Admin Django
# Ouvrir: http://localhost:8000/admin
# Logins: admin / password

# 2. Obtenir un token JWT
curl -X POST http://localhost:8000/api/token/ ^
  -H "Content-Type: application/json" ^
  -d "{\"username\": \"admin\", \"password\": \"your-password\"}"

# Réponse attendue:
# {
#   "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
# }

# 3. Utiliser le token
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/foyers/
```

**✓ Vérification:**
- Admin accessible
- Token obtenu
- API répond

## 📊 Étape 7: Créer des Données Test (10 min)

```python
# python manage.py shell

from users.models import User
from energy.models import Foyer, Consommation
from django.utils import timezone

# Créer un foyer
foyer = Foyer.objects.create(
    numero_foyer='FOYER001',
    adresse='123 Rue de la Paix',
    code_postal='75000',
    ville='Paris',
    puissance_souscrite=6.0
)

# Créer un résident
resident = User.objects.create_user(
    username='jean',
    email='jean@example.com',
    password='password123',
    role='RESIDENT',
    foyer=foyer
)

# Créer une consommation
consommation = Consommation.objects.create(
    foyer=foyer,
    timestamp=timezone.now(),
    kwh=5.2,
    temperature=22.0
)

print("✓ Données test créées!")
```

## 🔍 Étape 8: Vérifier les Règles de Gestion (15 min)

### ✅ RG1 - Authentification Obligatoire
```bash
# Doit échouer sans token
curl http://localhost:8000/api/foyers/
# Response: {"detail":"Authentication credentials were not provided."}

# Doit réussir avec token
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/foyers/
```

### ✅ RG2 - 1 Rôle par User
```python
# python manage.py shell
from users.models import User
user = User.objects.get(username='admin')
print(user.role)  # ADMIN ou RESIDENT (pas multiple)
```

### ✅ RG3 - Contrôle d'Accès par Rôle
```python
# RESIDENT ne voit que son foyer
# ADMIN voit tous les foyers
```

### ✅ RG19 - Passwords Hachés
```python
# python manage.py shell
from users.models import User
user = User.objects.get(username='admin')
print(user.password)  # Commence par pbkdf2_sha256$
```

### ✅ RG20 - Audit Trail
```python
# python manage.py shell
from energy.models import ActionLog
logs = ActionLog.objects.all()
for log in logs:
    print(f"{log.utilisateur.username} - {log.action} - {log.timestamp}")
```

## 📚 Étape 9: Consulter la Documentation

- [ ] Lire `README.md` pour les endpoints API
- [ ] Lire `INSTALLATION_GUIDE.md` pour les détails
- [ ] Consulter `GENERATION_SUMMARY.md` pour la vue d'ensemble

## 🚀 Étape 10: Déploiement (optionnel)

```bash
# Installer gunicorn
pip install gunicorn

# Tester gunicorn
gunicorn wsgi:application --bind 127.0.0.1:8000 --workers 2

# En production:
# - Configurer .env avec DEBUG=False
# - Utiliser une vraie SECRET_KEY
# - Configurer ALLOWED_HOSTS
# - Utiliser nginx comme reverse proxy
```

## 🐛 Dépannage

### Erreur: "django.db.utils.OperationalError"
```bash
# Vérifier MySQL
mysql -u root -p

# Vérifier variables .env
type .env

# Relancer les migrations
python manage.py migrate
```

### Erreur: "No module named 'mysql'"
```bash
pip install mysqlclient
# Ou si error: pip install mysql-connector-python
```

### Erreur: "Tables not found"
```bash
python manage.py migrate
python manage.py migrate --fake-initial
```

### Token JWT invalide
```bash
# Vérifier que le token n'est pas expiré (24h)
# Utiliser /api/token/refresh/ pour obtenir nouveau token
```

## ✅ Critères de Succès Final

- [ ] Serveur Django démarre sans erreur
- [ ] Admin Django accessible (http://localhost:8000/admin)
- [ ] Token JWT obtenu avec succès
- [ ] API endpoints fonctionnels
- [ ] RG1-RG20 toutes respectées
- [ ] 7 modèles créés et fonctionnels
- [ ] Base de données MySQL connectée
- [ ] Audit trail fonctionne

## 📞 Support

En cas de problème:
1. Consulter les logs: `logs/smartmeter.log`
2. Utiliser `python manage.py shell` pour déboguer
3. Vérifier la documentation Django: https://docs.djangoproject.com/en/5.0/

---

**Statut**: Prêt à l'emploi ✅
**Version**: 1.0.0
**Temps total**: ~1-2 heures

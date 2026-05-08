# ⚡ SPRINT 3 - Quick Start Commands

## Backend Setup (5 minutes)

### 1. Configuration
```bash
cd SMART-METER-BACKEND/backend

# Copier .env.example en .env
cp .env.example .env

# Éditer .env avec vos clés:
# - HUGGINGFACE_API_KEY (https://huggingface.co/settings/tokens)
# - EMAIL_HOST_USER et EMAIL_HOST_PASSWORD (Gmail App Password)

nano .env
```

### 2. Migrations
```bash
python manage.py migrate
```

### 3. Traiter les anomalies
```bash
# Détecter et traiter les anomalies anormales (anomaly_label=1)
python manage.py process_anomalies

# Avec output verbeux
python manage.py process_anomalies --verbosity=2
```

---

## Frontend Setup (3 minutes)

### Installation des dépendances
```bash
cd SMART-METER-FRONTEND

# Assurer que les packages sont installés
npm install framer-motion lucide-react sonner
```

### Accéder au dashboard
```
http://localhost:3000/dashboard/anomalies
```

---

## Testing

### Test l'API Hugging Face
```bash
cd SMART-METER-BACKEND/backend

python manage.py shell
>>> from energy.services.anomaly_service import obtenir_score_huggingface
>>> score = obtenir_score_huggingface(95.5)
>>> print(f"Score: {score:.2%}")
# Attendu: Score: 95.00% (ou 0.50 si erreur API)
```

### Test l'Email
```bash
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail(
...     "Test SmartMeter",
...     "Test message",
...     "from@example.com",
...     ["to@example.com"],
... )
# Attendu: 1 (succès)
```

### Test l'endpoint API
```bash
# Récupérer toutes les anomalies
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/energy/anomalies/

# Filtrer par sévérité
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/energy/anomalies/?severite=HAUTE"

# Acquitter une anomalie
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/energy/anomalies/1/marquer_acquittee/
```

---

## Workflow complet

### 1️⃣ Démarrer les serveurs
```bash
# Terminal 1: Backend
cd SMART-METER-BACKEND/backend
python manage.py runserver 0.0.0.0:8000

# Terminal 2: Frontend
cd SMART-METER-FRONTEND
npm run dev
```

### 2️⃣ Traiter les anomalies
```bash
# Terminal 3: Traitement
cd SMART-METER-BACKEND/backend
python manage.py process_anomalies
```

### 3️⃣ Visualiser le dashboard
```
Ouvrir: http://localhost:3000/dashboard/anomalies
```

### 4️⃣ Tester l'acquittement
```
1. Dans le dashboard, cliquer "Acquitter" sur une anomalie
2. Toast de confirmation s'affiche
3. La ligne passe en statut "Acquittée"
4. Email envoyé à l'admin (vérifier dans Gmail)
```

---

## Troubleshooting

### ❌ HUGGINGFACE_API_KEY not found
```bash
# Vérifier que .env existe et contient la clé
cat SMART-METER-BACKEND/backend/.env | grep HUGGINGFACE

# Ou tester directement
python manage.py shell
>>> import os
>>> os.environ.get('HUGGINGFACE_API_KEY')
```

### ❌ Email not working
```bash
# Vérifier les logs
tail -f SMART-METER-BACKEND/logs/smartmeter.log

# Tester Gmail App Password:
# - Doit contenir 16 caractères (avec espaces)
# - 2FA doit être activé
# - Pas le mot de passe normal!
```

### ❌ 404 sur /api/energy/anomalies/
```bash
# Vérifier les URLs sont enregistrées
python manage.py shell
>>> from django.urls import get_resolver
>>> resolver = get_resolver()
>>> resolver.url_patterns  # Chercher 'anomalies'
```

### ❌ CORS error au frontend
```bash
# Vérifier settings.py
cat SMART-METER-BACKEND/backend/settings.py | grep CORS_ALLOWED

# Devrait contenir: http://localhost:3000
```

---

## Logs & Monitoring

### Voir les anomalies créées
```bash
tail -f logs/smartmeter.log | grep "Anomalie créée"
```

### Voir les emails envoyés
```bash
tail -f logs/smartmeter.log | grep "Email d'alerte envoyé"
```

### Voir les erreurs API HF
```bash
tail -f logs/smartmeter.log | grep "Hugging Face API"
```

---

## Données de test

### Créer des anomalies de test
```bash
python manage.py shell
>>> from energy.models import Consommation, Foyer
>>> from datetime import datetime

# Créer un foyer s'il n'existe pas
>>> foyer, _ = Foyer.objects.get_or_create(
...     numero_foyer="TEST001",
...     defaults={
...         "adresse": "123 Test Street",
...         "code_postal": "75001",
...         "ville": "Paris",
...         "puissance_souscrite": 6.0
...     }
... )

# Créer une consommation anormale
>>> c = Consommation.objects.create(
...     foyer=foyer,
...     timestamp=datetime.now(),
...     kwh=95.5,
...     anomaly_label=1,  # Important: anomaly_label=1
...     temperature=22.5
... )

# Traiter les anomalies
>>> exit()
python manage.py process_anomalies
```

---

## Variables d'environnement (production)

```env
# Hugging Face
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxx

# Gmail SMTP
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your.email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx

# Database
DB_ENGINE=django.db.backends.mysql
DB_NAME=smartmeter_prod
DB_USER=smartmeter
DB_PASSWORD=strong_password_here
DB_HOST=db.example.com
DB_PORT=3306

# Security
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=api.example.com,www.example.com
CORS_ALLOWED_ORIGINS=https://example.com
```

---

## Commandes Django utiles

```bash
# Afficher toutes les anomalies
python manage.py dbshell
SELECT COUNT(*) FROM energy_anomalie;
SELECT * FROM energy_anomalie WHERE statut='NOUVELLE' LIMIT 5;

# Voir les alertes
SELECT * FROM energy_alerte WHERE acquittee=False;

# Réinitialiser les statuts (DEV ONLY)
DELETE FROM energy_alerte;
DELETE FROM energy_anomalie;
```

---

## Performance & Scaling

### Si >100 anomalies à traiter
```python
# Utiliser batch processing dans anomaly_service.py
for consommation in consommations_anormales.iterator(chunk_size=50):
    # traiter...
```

### Si l'API HF est lente
```python
# Ajouter du caching avec Redis
from django.views.decorators.cache import cache_page
```

### Si trop d'emails
```python
# Regrouper les emails par heure
# Envoyer un digest au lieu d'1 email par anomalie
```

---

## Roadmap Post-Sprint 3

- [ ] Ajouter un digest email journalier
- [ ] Mettre en cache les scores Hugging Face
- [ ] Implémenter une queue Celery pour traitement async
- [ ] Dashboard temps réel avec WebSocket
- [ ] Prédictions de consommation future
- [ ] Integration API ML externe

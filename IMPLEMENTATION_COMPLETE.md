# SmartMeter Intelligence Backend - Implémentation Complète

## RÉSUMÉ D'EXÉCUTION

Le backend SmartMeter Intelligence a été complètement révisé et implémenté selon le Cahier des Charges.

### Données Créées

- **Admins**: 2
- **Résidents**: 4 (2 par admin)
- **Lectures de Consommation**: 28 (7 jours par résident)
- **Total kWh Admin 1**: 112.4 kWh
- **Total kWh Admin 2**: 129.7 kWh

---

## 1. FICHIERS MODIFIÉS

### Modèles (Models)

**`backend/users/models.py`**
- Ajout du champ `managed_by` (ForeignKey) pour gérer la relation Admin → Résidents
- Index sur `managed_by` pour les requêtes optimisées
- Toujours compatible avec le champ `foyer` existant

**`backend/energy/models.py`**
- Nouveau modèle `ConsumptionReading` pour les lectures de consommation
- Champs: `resident`, `meter_id`, `timestamp`, `consumption_kwh`, `cost_estimate`, `tariff_type`
- Constraints uniques: `(resident, meter_id, timestamp)`
- Indexes sur `resident`, `meter_id`, et `timestamp`

### Sérializers

**`backend/energy/serializers.py`**
- `ConsumptionReadingSerializer`: Sérialiser les lectures individuelles
- `AdminDashboardSerializer`: Données agrégées pour l'admin
- `ResidentDashboardSerializer`: Données du résident
- `CurrentUserSerializer`: Info utilisateur connecté
- Autres serializers utilitaires

### Views

**`backend/energy/views_smartmeter.py` (NOUVEAU)**
- `current_user()`: GET /api/auth/me/
- `AdminResidentsListView`: GET /api/admin/residents/
- `AdminDashboardView`: GET /api/admin/dashboard/
- `ResidentDashboardView`: GET /api/resident/dashboard/
- `ResidentReadingsView`: GET /api/resident/readings/

### Permissions

**`backend/energy/permissions.py`**
- `IsAdminRole`: Autorise uniquement les ADMIN
- `IsResidentRole`: Autorise uniquement les RESIDENT
- `CanViewConsumptionReading`: Isolation des données par utilisateur

### Commandes Management

**`backend/energy/management/commands/seed_smartmeter_data.py` (NOUVEAU)**
- Crée 2 admins + 4 résidents + 28 readings
- Idempotente (peut être relancée sans doublons)
- Hache les mots de passe correctement

### Configuration

**`backend/users/urls.py`**
- Ajout de `GET /api/auth/me/`

**`backend/energy/urls.py`**
- Ajout des nouveaux endpoints admin et résident

**`backend/users/admin.py`**
- Mise à jour du Django Admin pour afficher `managed_by`

**`backend/energy/admin.py`**
- Enregistrement de `ConsumptionReadingAdmin`

### Migrations

**`backend/users/migrations/0003_user_managed_by.py`**
- Migration pour le champ `managed_by`

**`backend/energy/migrations/0006_consumptionreading.py`**
- Migration pour le modèle `ConsumptionReading`

---

## 2. CREDENTIALS DE CONNEXION

Tous les utilisateurs ont le mot de passe: **`pass123`**

### Admins

```
Email: houdamouttalib@gmail.com
Pass: pass123
Gère 2 résidents:
  - abdelwadoud@gmail.com
  - mohammed@gmail.com

Email: youneseljonhy@gmail.com
Pass: pass123
Gère 2 résidents:
  - abdelwadoudomrachi@gmail.com
  - mohammedouafik@gmail.com
```

### Résidents

```
abdelwadoud@gmail.com (géré par houdamouttalib@gmail.com)
Pass: pass123
Meter: MTR-ADM1-001
Total 7 jours: 65.6 kWh

mohammed@gmail.com (géré par houdamouttalib@gmail.com)
Pass: pass123
Meter: MTR-ADM1-002
Total 7 jours: 46.8 kWh

abdelwadoudomrachi@gmail.com (géré par youneseljonhy@gmail.com)
Pass: pass123
Meter: MTR-ADM2-001
Total 7 jours: 89.6 kWh

mohammedouafik@gmail.com (géré par youneseljonhy@gmail.com)
Pass: pass123
Meter: MTR-ADM2-002
Total 7 jours: 40.1 kWh
```

---

## 3. ENDPOINTS API

### Authentication

```
POST /api/auth/login/
- Body: { "email": "user@example.com", "password": "pass123" }
- Returns: { "access", "refresh", "user": { "id", "email", "role", "managed_by" } }

GET /api/auth/me/
- Headers: Authorization: Bearer <token>
- Returns: Current user info with role and managed_by

POST /api/auth/token/refresh/
- Body: { "refresh": "<token>" }
```

### Admin Endpoints

```
GET /api/admin/residents/
- Headers: Authorization: Bearer <token>
- Returns: List of residents managed by this admin
- Response:
  {
    "count": 2,
    "residents": [
      {
        "id": 3,
        "email": "resident@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "RESIDENT"
      }
    ]
  }

GET /api/admin/dashboard/
- Headers: Authorization: Bearer <token>
- Returns: Aggregated data for all managed residents
- Response:
  {
    "admin_email": "admin@example.com",
    "total_residents": 2,
    "total_consumption_kwh": 127.4,
    "total_cost_estimate": 31.85,
    "average_consumption_per_resident": 63.7,
    "residents": [
      {
        "email": "resident1@example.com",
        "meter_id": "MTR-001",
        "total_consumption_kwh": 65.6,
        "total_cost_estimate": 16.4
      }
    ],
    "consumption_by_day": [
      {
        "date": "2026-05-01",
        "total_consumption_kwh": 13.9
      }
    ]
  }
```

### Resident Endpoints

```
GET /api/resident/dashboard/
- Headers: Authorization: Bearer <token>
- Returns: Resident's consumption overview
- Response:
  {
    "resident_email": "resident@example.com",
    "meter_id": "MTR-001",
    "total_consumption_kwh": 65.6,
    "total_cost_estimate": 16.4,
    "average_daily_consumption": 9.4,
    "readings": [ ... ]
  }

GET /api/resident/readings/?meter_id=MTR-001&start_date=2026-05-01&end_date=2026-05-07
- Headers: Authorization: Bearer <token>
- Query Params: meter_id, start_date, end_date, tariff_type (optional)
- Returns: List of consumption readings for this resident
```

---

## 4. COMMANDES À EXÉCUTER

```bash
# Appliquer les migrations
python manage.py migrate

# Créer les données initiales
python manage.py seed_smartmeter_data

# Lancer le serveur
python manage.py runserver 0.0.0.0:8000

# Accéder à Django Admin
# http://localhost:8000/admin/
```

---

## 5. REQUÊTES SQL POUR VÉRIFICATION MySQL

### Voir tous les utilisateurs

```sql
SELECT id, email, role, managed_by_id, is_staff, is_active 
FROM users_user 
ORDER BY role, email;
```

### Voir les admins

```sql
SELECT id, email, role 
FROM users_user 
WHERE role = 'ADMIN';
```

### Voir les résidents avec leur admin

```sql
SELECT 
  r.id, 
  r.email AS resident_email, 
  a.email AS admin_email
FROM users_user r
LEFT JOIN users_user a ON r.managed_by_id = a.id
WHERE r.role = 'RESIDENT'
ORDER BY a.email, r.email;
```

### Voir les readings

```sql
SELECT 
  id, 
  resident_id, 
  meter_id, 
  timestamp, 
  consumption_kwh, 
  cost_estimate
FROM energy_consumption_reading
ORDER BY timestamp DESC
LIMIT 50;
```

### Données groupées par résident

```sql
SELECT 
  u.email, 
  SUM(c.consumption_kwh) AS total_kwh, 
  SUM(c.cost_estimate) AS total_cost,
  COUNT(c.id) AS reading_count
FROM energy_consumption_reading c
JOIN users_user u ON c.resident_id = u.id
GROUP BY u.email
ORDER BY total_kwh DESC;
```

### Données groupées par admin

```sql
SELECT 
  a.email AS admin_email, 
  COUNT(DISTINCT r.id) AS resident_count,
  SUM(c.consumption_kwh) AS total_kwh, 
  SUM(c.cost_estimate) AS total_cost
FROM energy_consumption_reading c
JOIN users_user r ON c.resident_id = r.id
JOIN users_user a ON r.managed_by_id = a.id
GROUP BY a.email
ORDER BY total_kwh DESC;
```

---

## 6. LOGIQUE DE SÉCURITÉ ET ISOLATION DES DONNÉES

### Admin
- Voit uniquement les résidents qu'il gère (filtre: `managed_by = current_user`)
- Voit uniquement les readings de ces résidents
- Peut voir les données agrégées de son périmètre
- Ne voit jamais les données d'un autre admin

### Resident
- Voit uniquement ses propres readings
- Ne voit pas les données des autres résidents
- Ne peut pas accéder aux endpoints admin
- Peut voir son dashboard personnel

### Filtres Appliqués
```python
# Admin Dashboard
readings = ConsumptionReading.objects.filter(resident__managed_by=request.user)

# Resident Dashboard
readings = ConsumptionReading.objects.filter(resident=request.user)
```

---

## 7. STRUCTURE DES TABLES

### `users_user`
```
id (BigAutoField)
email (EmailField, unique)
username (CharField, unique)
first_name (CharField)
last_name (CharField)
role (CharField: ADMIN | RESIDENT)
managed_by_id (ForeignKey, nullable) ← Admin responsable
foyer_id (ForeignKey, nullable) ← Compatibilité
is_staff (BooleanField)
is_active (BooleanField)
password (CharField, hashed)
date_joined (DateTimeField)
```

### `energy_consumption_reading`
```
id (BigAutoField)
resident_id (ForeignKey, required)
meter_id (CharField)
timestamp (DateTimeField)
consumption_kwh (DecimalField)
cost_estimate (DecimalField)
tariff_type (CharField: standard | peak | off_peak)
created_at (DateTimeField)
updated_at (DateTimeField)

Unique Constraint: (resident_id, meter_id, timestamp)
Indexes: resident_id, meter_id, timestamp
```

---

## 8. PRÉPARATION POUR IMPORT KAGGLE FUTUR

La structure est préparée pour intégrer le dataset Kaggle London Smart Meters:

- Les readings sont liées au résident uniquement
- Les meter_id peuvent être matchés avec le dataset Kaggle
- Les données peuvent être divisées entre résidents
- Les admins verront automatiquement les données agrégées de leurs résidents

Future commande (optionnelle):
```bash
python manage.py import_kaggle_data --file path/to/london_data.csv --resident_id=3
```

---

## 9. COMPATIBILITÉ MYSQL

Le backend supporte MySQL avec variables d'environnement:

```bash
# .env (ou variables système)
DB_ENGINE=django.db.backends.mysql
DB_NAME=smartmeter_db
DB_USER=root
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=3306
```

Charset par défaut: `utf8mb4` pour supporter caractères spéciaux.

---

## 10. TESTER LES ENDPOINTS

### Exemple avec curl

```bash
# Login Admin 1
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"houdamouttalib@gmail.com","password":"pass123"}'

# Get token from response
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

# Get current user
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/auth/me/

# Get admin residents
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/admin/residents/

# Get admin dashboard
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/admin/dashboard/

# Login Resident
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"abdelwadoud@gmail.com","password":"pass123"}'

# Get resident dashboard
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/resident/dashboard/

# Get resident readings
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/resident/readings/
```

---

## 11. VÉRIFICATIONS COMPLÉTÉES

- ✓ User model avec `managed_by` field
- ✓ ConsumptionReading model créé
- ✓ Relations Admin → Résidents correctes
- ✓ Migrations appliquées
- ✓ 2 Admins créés
- ✓ 4 Résidents créés (2 par admin)
- ✓ 28 Readings créés (7 par résident)
- ✓ Passwords hashés correctement
- ✓ Permissions et isolation des données
- ✓ Endpoints API implémentés
- ✓ Django Admin configuré
- ✓ Commande seed idempotente
- ✓ MySQL compatible
- ✓ Préparé pour import Kaggle

---

## 12. STRUCTURE DE RÉPERTOIRES

```
backend/
├── users/
│   ├── models.py (modified - added managed_by)
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py (modified)
│   ├── migrations/
│   │   ├── 0003_user_managed_by.py (new)
├── energy/
│   ├── models.py (modified - added ConsumptionReading)
│   ├── serializers.py (modified - added new serializers)
│   ├── views.py
│   ├── views_smartmeter.py (new)
│   ├── permissions.py (modified - added new permissions)
│   ├── urls.py (modified)
│   ├── admin.py (modified - added ConsumptionReadingAdmin)
│   ├── migrations/
│   │   ├── 0006_consumptionreading.py (new)
│   ├── management/
│   │   ├── commands/
│   │   │   ├── seed_smartmeter_data.py (new)
├── settings.py (no change needed)
├── urls.py (no change needed)
```

---

## Notes Importantes

1. **Mots de passe**: Tous les utilisateurs créés via seed_smartmeter_data ont le même mot de passe `pass123` pour faciliter le test. À changer en production.

2. **Idempotence**: La commande seed peut être relancée sans créer de doublons (utilise `update_or_create`).

3. **Isolation des données**: L'isolation est garantie au niveau de la queryset (filtrage côté ORM). Ajouter des tests pour vérifier que les admins ne voient pas les données croisées.

4. **Tarification**: Coût = consumption_kwh × 0.25 (tarif fixe 0.25 par kWh). À adapter selon les besoins réels.

5. **Compatibilité future**: Le modèle ConsumptionReading est conçu pour accueillir des millions de readings du dataset Kaggle sans modification.

---

## Prochaines étapes (optionnel)

1. Ajouter tests unitaires pour vérifier isolation des données
2. Implémenter paginatio dans les endpoints
3. Ajouter filtrage avancé (date range, meter_id) dans les endpoints
4. Créer endpoint import Kaggle
5. Ajouter alertes et anomalies pour les résidents
6. Configurer rate limiting et caching

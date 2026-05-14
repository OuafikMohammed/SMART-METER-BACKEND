# 🗄️ MySQL Migrations for SmartMeter - Complete Guide

**Objective**: Create all database tables in MySQL using Django migrations  
**Time**: 10-15 minutes  
**Prerequisites**: MySQL installed and running, MySQL Workbench (optional)

---

## Step 1: Verify MySQL is Running

### Windows PowerShell

```powershell
# Check if MySQL service is running
Get-Service MySQL80

# Output should show: "Running"
# If not running, start it:
Start-Service MySQL80

# Verify connection (will prompt for password)
mysql -u root -p
# (Type your root password or press Enter if no password)
# Exit: type "exit"
```

### macOS

```bash
brew services list
# Should show: mysql@8.0 started

# If not running:
brew services start mysql@8.0
```

### Linux

```bash
sudo systemctl status mysql
# Should show: active (running)

# If not running:
sudo systemctl start mysql
```

---

## Step 2: Create MySQL Database & User

### Option A: Using MySQL Command Line (Fastest)

```powershell
# Windows PowerShell
mysql -u root -p

# You'll be prompted for password (press Enter if no password or type it)
```

Once logged in, run these SQL commands:

```sql
-- Create the database
CREATE DATABASE smartmeter_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create the user
CREATE USER 'smartmeter_user'@'localhost' IDENTIFIED BY 'SmartMeter@2026';

-- Grant all privileges
GRANT ALL PRIVILEGES ON smartmeter_db.* TO 'smartmeter_user'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

-- Verify (you should see the database)
SHOW DATABASES;

-- Exit MySQL
EXIT;
```

**Expected Output:**
```
Query OK, 1 row affected
Query OK, 0 rows affected
Query OK, 0 rows affected
Query OK, 0 rows affected
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| smartmeter_db      |  ← This is your new database
| sys                |
+--------------------+
```

### Option B: Using MySQL Workbench

1. Open **MySQL Workbench**
2. Connect to your MySQL server
3. Click **File** → **New Query Tab**
4. Paste the SQL commands above
5. Click **Execute** (Lightning bolt icon) ⚡
6. Verify database created in left panel

---

## Step 3: Set MySQL Password in .env File

The `.env` file needs your MySQL password.

### Find Your .env File

```powershell
# Windows - navigate to backend folder
cd "C:\Users\omrac\Desktop\Electrecity\SMART-METER-BACKEND"

# Open the .env file in VS Code or notepad
# Path: .env
```

### Edit the `.env` File

Find this line:
```
DB_PASSWORD=
```

Change it to:
```
DB_PASSWORD=SmartMeter@2026
```

**Complete Database Section Should Look Like:**
```
# Database Configuration - MySQL
DB_ENGINE=django.db.backends.mysql
DB_NAME=smartmeter_db
DB_USER=smartmeter_user
DB_PASSWORD=SmartMeter@2026
DB_HOST=localhost
DB_PORT=3306
```

**Save the file** (Ctrl + S)

---

## Step 4: Verify Django Can Connect to MySQL

```powershell
# Navigate to backend folder
cd "C:\Users\omrac\Desktop\Electrecity\SMART-METER-BACKEND\backend"

# Check Django configuration
python manage.py check

# Should output:
# System check identified no issues (0 silenced).
```

If you see errors about database connection, check:
- ✅ MySQL is running: `Get-Service MySQL80` (should show "Running")
- ✅ Password in .env is correct
- ✅ Database name, user, host are correct
- ✅ Port is 3306

---

## Step 5: Run Django Migrations

### See Current Migration Status

```powershell
# Still in: C:\Users\omrac\Desktop\Electrecity\SMART-METER-BACKEND\backend

# View pending migrations
python manage.py showmigrations

# Output:
# users
#  [ ] 0001_initial
#  [ ] 0002_alter_user_foyer_alter_user_role
#
# energy
#  [ ] 0001_initial
#  [ ] 0002_initial
#  [ ] 0003_alter_consommation_anomaly_label_and_more
#  [ ] 0004_sprint3_anomalies_alertes
#  [ ] 0005_rename_energy_alrt_statut_created_idx_energy_aler_statut_ccac5a_idx_and_more
```

### Apply All Migrations

```powershell
# Apply migrations to MySQL
python manage.py migrate

# Output:
# Operations to perform:
#   Apply all migrations: admin, auth, contenttypes, sessions, users, energy
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying auth.0001_initial... OK
#   Applying auth.0002_alter_permission_options... OK
#   ...
#   Applying energy.0005_rename_energy_alrt_statut_created_idx... OK
```

**All migrations should show: ✅ OK**

---

## Step 6: Verify Migrations in MySQL Workbench

### Using MySQL Workbench

1. **Open MySQL Workbench**
2. **Double-click** your "SmartMeter Dev" connection
3. **Left side panel**: Click to expand **Schemas**
4. **Expand**: `smartmeter_db` → `Tables`

**You should see these tables:**
```
smartmeter_db/
├── Tables/
│   ├── auth_group
│   ├── auth_group_permissions
│   ├── auth_permission
│   ├── auth_user
│   ├── auth_user_groups
│   ├── auth_user_user_permissions
│   ├── django_admin_log
│   ├── django_content_type
│   ├── django_migrations
│   ├── django_session
│   ├── energy_actionlog
│   ├── energy_alerte
│   ├── energy_anomalie
│   ├── energy_consommation
│   ├── energy_conversationIA
│   ├── energy_foyer
│   ├── users_user
│   └── ... (other tables)
```

**Count: 17+ tables should be present**

### Using MySQL Command Line

```powershell
# Connect to your database
mysql -u smartmeter_user -p smartmeter_db

# View all tables
SHOW TABLES;

# Output:
# +-------------------------------------+
# | Tables_in_smartmeter_db             |
# +-------------------------------------+
# | auth_group                          |
# | auth_group_permissions              |
# | auth_permission                     |
# | auth_user                           |
# | auth_user_groups                    |
# | auth_user_user_permissions          |
# | django_admin_log                    |
# | django_content_type                 |
# | django_migrations                   |
# | django_session                      |
# | energy_actionlog                    |
# | energy_alerte                       |
# | energy_anomalie                     |
# | energy_consommation                 |
# | energy_conversationIA               |
# | energy_foyer                        |
# | users_user                          |
# +-------------------------------------+
```

---

## Step 7: Create a Superuser (Admin Account)

```powershell
# Still in: C:\Users\omrac\Desktop\Electrecity\SMART-METER-BACKEND\backend

# Create superuser
python manage.py createsuperuser

# Follow the prompts:
# Username: admin
# Email: admin@smartmeter.local
# Password: Enter123!@#
# Password (again): Enter123!@#
# Superuser created successfully.
```

**Save these credentials:**
- **Username**: admin
- **Email**: admin@smartmeter.local
- **Password**: Enter123!@# (or whatever you set)

---

## Step 8: Verify Database Structure

### View Users Table Structure

```powershell
mysql -u smartmeter_user -p smartmeter_db

# View structure of users_user table
DESCRIBE users_user;

# Output:
# +-----------------------+--------------+------+-----+---------+----------------+
# | Field                 | Type         | Null | Key | Default | Extra          |
# +-----------------------+--------------+------+-----+---------+----------------+
# | id                    | bigint       | NO   | PRI | NULL    | auto_increment |
# | password              | varchar(128) | NO   |     | NULL    |                |
# | last_login            | datetime     | YES  |     | NULL    |                |
# | is_superuser          | tinyint(1)   | NO   |     | NULL    |                |
# | username              | varchar(150) | NO   | UNI | NULL    |                |
# | first_name            | varchar(150) | NO   |     | NULL    |                |
# | last_name             | varchar(150) | NO   |     | NULL    |                |
# | email                 | varchar(254) | NO   |     | NULL    |                |
# | is_staff              | tinyint(1)   | NO   |     | NULL    |                |
# | is_active             | tinyint(1)   | NO   |     | NULL    |                |
# | date_joined           | datetime     | NO   |     | NULL    |                |
# | role                  | varchar(20)  | NO   |     | RESIDENT|                |
# | foyer_id              | bigint       | YES  | MUL | NULL    |                |
# +-----------------------+--------------+------+-----+---------+----------------+

EXIT;
```

### View All Tables

```powershell
mysql -u smartmeter_user -p smartmeter_db

# Show all table structures
SHOW FULL TABLES WHERE Table_type='BASE TABLE';

# Count total tables
SELECT COUNT(*) as total_tables FROM information_schema.TABLES WHERE TABLE_SCHEMA='smartmeter_db';

# Check table sizes
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
FROM information_schema.TABLES
WHERE table_schema = 'smartmeter_db'
ORDER BY (data_length + index_length) DESC;

EXIT;
```

---

## Step 9: Test the Connection from Django

```powershell
# In: C:\Users\omrac\Desktop\Electrecity\SMART-METER-BACKEND\backend

# Open Django shell
python manage.py shell

# Inside the shell, run:
from django.contrib.auth.models import User
from energy.models import Foyer

# Count users
User.objects.count()
# Should return: 1 (the superuser you just created)

# Count foyers (empty initially)
Foyer.objects.count()
# Should return: 0

# Exit shell
exit()
```

---

## 🎉 Migrations Complete!

Your MySQL database is now set up with all 17+ tables created by Django migrations.

### Summary of What Was Created

| Component | Status |
|-----------|--------|
| Database: `smartmeter_db` | ✅ Created |
| User: `smartmeter_user` | ✅ Created |
| All Django tables | ✅ Migrated |
| Superuser account | ✅ Created |
| Ready for data import | ✅ Yes |

---

## Next Steps

### 1. View Your Data in Workbench

```powershell
# Start Django admin to create test data
python manage.py runserver
```

Then visit: http://localhost:8000/admin
- Username: admin
- Password: Enter123!@#

### 2. Import Kaggle Data

```powershell
# Import CSV data (if you have a CSV file)
python manage.py import_kaggle_users your_data.csv
```

### 3. Test API Endpoints

```powershell
# Visit API root
http://localhost:8000/api/
```

### 4. Start Frontend

```powershell
# In new terminal
cd SMART-METER-FRONTEND
npm run dev
# Visit http://localhost:3000
```

---

## ⚠️ Troubleshooting

### ❌ "Can't connect to MySQL server"

```powershell
# Check MySQL is running
Get-Service MySQL80

# If not running, start it
Start-Service MySQL80

# Try again
python manage.py migrate
```

### ❌ "Unknown database 'smartmeter_db'"

```powershell
# Create the database
mysql -u root -p
```

Then run:
```sql
CREATE DATABASE smartmeter_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### ❌ "Access denied for user 'smartmeter_user'"

```powershell
# Verify password in .env file
cat .env | findstr DB_PASSWORD

# Should show: DB_PASSWORD=SmartMeter@2026

# If password is wrong, update it in .env and try again
```

### ❌ "No migrations to apply"

```powershell
# This is normal if migrations already applied
# Verify:
python manage.py showmigrations

# All should show [X] OK
```

---

## 📊 Verify in MySQL Workbench

**Visual Verification Steps:**

1. **Open MySQL Workbench**
2. **Double-click** "SmartMeter Dev" connection
3. **Left side**: Schemas → smartmeter_db → Tables
4. **You should see:**
   - ✅ users_user (for user accounts)
   - ✅ energy_foyer (for households)
   - ✅ energy_consommation (for energy usage)
   - ✅ energy_anomalie (for anomalies)
   - ✅ energy_alerte (for alerts)
   - ✅ energy_conversationIA (for AI chat)
   - ✅ energy_actionlog (for audit logging)
   - ✅ Plus 10+ Django system tables

5. **Right-click** → **"Select Rows - Limit 1000"**
6. **See your data!**

---

## ✅ Final Checklist

- [ ] MySQL service is running
- [ ] Database `smartmeter_db` created
- [ ] User `smartmeter_user` created
- [ ] `.env` file has `DB_PASSWORD=SmartMeter@2026`
- [ ] `python manage.py check` shows no errors
- [ ] `python manage.py migrate` ran successfully
- [ ] `python manage.py showmigrations` shows all [X]
- [ ] 17+ tables appear in MySQL Workbench
- [ ] Superuser account created
- [ ] Can connect to database from Django shell

**All complete? You're ready to run the application! 🚀**

---

**Status**: ✅ Database Migrations Complete  
**Date**: May 13, 2026  
**Version**: 1.0

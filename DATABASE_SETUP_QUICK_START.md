# SmartMeter Database - Quick Start Guide

## 📁 Files Created

This database configuration package includes 5 documents:

1. **MYSQL_DATABASE_SETUP.md** - Complete reference documentation
2. **smartmeter_migrations.sql** - Raw SQL migration script
3. **.env.example** - Environment configuration template
4. **setup_database.sh** - Automated setup for Linux/macOS
5. **setup_database.ps1** - Automated setup for Windows PowerShell

---

## 🚀 Quick Setup (3 Options)

### Option 1: Automated Setup (Recommended)

#### Windows (PowerShell)
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup_database.ps1
```

#### Linux/macOS (Bash)
```bash
chmod +x setup_database.sh
./setup_database.sh
```

---

### Option 2: Manual Setup with SQL

```bash
# 1. Connect to MySQL
mysql -u root -p

# 2. Create database and user
CREATE DATABASE smartmeter_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'smartmeter_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON smartmeter_db.* TO 'smartmeter_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# 3. Load schema
mysql -u smartmeter_user -p -h localhost smartmeter_db < smartmeter_migrations.sql

# 4. Verify
mysql -u smartmeter_user -p -h localhost smartmeter_db -e "SHOW TABLES;"
```

---

### Option 3: Django Integration

```bash
# 1. Copy environment template
cp .env.example .env
# Edit .env with your database credentials

# 2. Install Python dependencies
pip install mysqlclient python-decouple

# 3. Run Django migrations
python manage.py migrate

# 4. Create superuser
python manage.py createsuperuser

# 5. Test connection
python manage.py dbshell
```

---

## 📊 Database Schema Overview

### Tables (8 total)

| Table | Purpose | Records |
|-------|---------|---------|
| `users_user` | Extended Django user model | Users with roles |
| `energy_foyer` | Households/properties | Properties to monitor |
| `energy_consommation` | Energy measurements | Time-series data |
| `energy_anomalie` | Detected anomalies | Anomaly records |
| `energy_alerte` | Alerts from anomalies | Notifications |
| `energy_conversationIA` | AI chat history | User-AI conversations |
| `energy_actionlog` | Audit trail | All user actions |

### Key Features

✅ **UTF8MB4 Support** - Full Unicode support  
✅ **Foreign Key Constraints** - Data integrity  
✅ **Optimized Indexes** - Fast queries  
✅ **Comprehensive Auditing** - RG20 compliance  
✅ **Type Validation** - Check constraints  

---

## 🔑 Credentials Template

### Database Credentials
```
Database: smartmeter_db
Username: smartmeter_user
Host: localhost
Port: 3306
Character Set: utf8mb4
```

### Django Configuration (settings.py)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'smartmeter_db',
        'USER': 'smartmeter_user',
        'PASSWORD': 'your_password_here',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}
```

---

## ⚙️ Configuration Steps

### Step 1: Create .env File
```bash
cp .env.example .env
```

Edit `.env` with:
```env
DB_ENGINE=django.db.backends.mysql
DB_NAME=smartmeter_db
DB_USER=smartmeter_user
DB_PASSWORD=your_secure_password_here
DB_HOST=localhost
DB_PORT=3306
DEBUG=True
SECRET_KEY=your-secret-key-min-50-chars
```

### Step 2: Install Requirements
```bash
pip install -r requirements.txt
# or manually:
pip install mysqlclient python-decouple
```

### Step 3: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 4: Create Admin Account
```bash
python manage.py createsuperuser
```

### Step 5: Start Server
```bash
python manage.py runserver
# Access: http://localhost:8000/admin
```

---

## 🧪 Verification Checklist

- [ ] MySQL server is running
- [ ] Database `smartmeter_db` exists
- [ ] User `smartmeter_user` has full privileges
- [ ] All 8 tables are created
- [ ] Foreign key constraints are in place
- [ ] .env file is configured
- [ ] Django migrations completed
- [ ] Superuser account created
- [ ] Django admin is accessible

### Verify via SQL
```sql
USE smartmeter_db;

-- Show all tables
SHOW TABLES;

-- Check table count (should be 8)
SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'smartmeter_db';

-- Show foreign keys
SELECT CONSTRAINT_NAME, TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'smartmeter_db'
AND REFERENCED_TABLE_NAME IS NOT NULL;
```

---

## 🔧 Common Tasks

### Backup Database
```bash
# Linux/macOS
mysqldump -u smartmeter_user -p smartmeter_db > backup_$(date +%Y%m%d).sql

# Windows PowerShell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe" `
  -u smartmeter_user -p smartmeter_db | `
  Out-File "backup_$(Get-Date -Format yyyyMMdd).sql"
```

### Restore Database
```bash
mysql -u smartmeter_user -p smartmeter_db < backup_20260420.sql
```

### Reset Database (DANGEROUS!)
```bash
mysql -u smartmeter_user -p smartmeter_db < smartmeter_migrations.sql
```

### Check Database Size
```sql
SELECT 
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) as size_mb
FROM information_schema.TABLES
WHERE table_schema = 'smartmeter_db';
```

---

## 🐛 Troubleshooting

### Connection Denied
```bash
# Verify credentials
mysql -u smartmeter_user -p -h localhost -D smartmeter_db -e "SELECT 1"

# Check user privileges
mysql -u root -p -e "SHOW GRANTS FOR 'smartmeter_user'@'localhost'"
```

### Table Not Found After Django Migrate
```bash
# Ensure migrations folder exists
ls backend/energy/migrations/
ls backend/users/migrations/

# Reset and re-migrate
python manage.py migrate --run-syncdb
```

### Foreign Key Constraint Error
```sql
-- Check foreign keys
SHOW CREATE TABLE energy_anomalie\G

-- Temporarily disable checks (use cautiously)
SET FOREIGN_KEY_CHECKS = 0;
-- ... perform operations ...
SET FOREIGN_KEY_CHECKS = 1;
```

### Charset Issues
```sql
-- Verify charset
SHOW CREATE DATABASE smartmeter_db;
SHOW CREATE TABLE energy_foyer;

-- Alter if needed
ALTER DATABASE smartmeter_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## 📚 Related Documents

- **MYSQL_DATABASE_SETUP.md** - Full reference guide
- **smartmeter_migrations.sql** - Raw SQL schema
- **Backend Structure** - See `SMARTMETER_CODE_REFERENCE.py`
- **Installation Guide** - See `INSTALLATION_GUIDE.md`

---

## 🎯 Next Steps

1. ✅ Run setup script (Option 1)
2. ✅ Configure .env file
3. ✅ Run Django migrations
4. ✅ Create superuser
5. ✅ Start development server
6. ✅ Access admin panel at `/admin`
7. ✅ Begin development!

---

## 📞 Support

For issues:
1. Check **MYSQL_DATABASE_SETUP.md** Troubleshooting section
2. Review Django MySQL documentation
3. Verify MySQL server is running
4. Check .env credentials match database user

---

**Last Updated:** 2026-04-20  
**Version:** 1.0  
**Status:** ✅ Ready for production

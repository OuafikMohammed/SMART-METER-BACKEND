# SmartMeter - MySQL Database Configuration Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Database Creation](#database-creation)
3. [Tables Structure](#tables-structure)
4. [SQL Migrations](#sql-migrations)
5. [Django Integration](#django-integration)
6. [Backup & Recovery](#backup--recovery)

---

## Prerequisites

### Required Tools
- MySQL 8.0+ (or MariaDB 10.5+)
- Django 5.0+
- Python 3.8+
- `mysql-connector-python` or `mysqlclient` library

### Installation

#### Windows
```bash
# Using pip to install MySQL connector
pip install mysqlclient
# OR
pip install mysql-connector-python
```

#### Linux/Mac
```bash
# Ubuntu/Debian
sudo apt-get install mysql-server mysql-client

# macOS
brew install mysql
```

---

## Database Creation

### Step 1: Connect to MySQL
```bash
# Windows/Linux/Mac
mysql -u root -p
```

### Step 2: Create Database and User
```sql
-- Create database
CREATE DATABASE smartmeter_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create dedicated user
CREATE USER 'smartmeter_user'@'localhost' IDENTIFIED BY 'your_secure_password_here';

-- Grant all privileges
GRANT ALL PRIVILEGES ON smartmeter_db.* TO 'smartmeter_user'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

-- Verify
SHOW GRANTS FOR 'smartmeter_user'@'localhost';
```

### Step 3: Verify Connection
```bash
mysql -u smartmeter_user -p -h localhost smartmeter_db
```

---

## Tables Structure

### Complete Database Schema

This SmartMeter application uses 8 main tables across 2 Django apps:

#### **App: users**
1. `auth_user` - Django's authentication table (extended by custom User model)

#### **App: energy**
1. `energy_foyer` - Energy households
2. `energy_consommation` - Energy consumption records
3. `energy_anomalie` - Detected anomalies
4. `energy_alerte` - Alerts from anomalies
5. `energy_conversationIA` - AI chatbot conversations
6. `energy_actionlog` - Audit trail for all user actions

---

## SQL Migrations

### Migration 1: Create Users Table (Extended)

```sql
-- Create custom user table (extends Django's auth_user)
CREATE TABLE IF NOT EXISTS users_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME NULL,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined DATETIME NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'RESIDENT' CHECK (role IN ('RESIDENT', 'ADMIN')),
    foyer_id BIGINT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_role (role),
    INDEX idx_foyer (foyer_id),
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_is_active (is_active),
    
    CONSTRAINT chk_role CHECK (role IN ('RESIDENT', 'ADMIN'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Migration 2: Create Foyer Table

```sql
-- Create Foyer (Household) table
CREATE TABLE IF NOT EXISTS energy_foyer (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    numero_foyer VARCHAR(50) NOT NULL UNIQUE,
    adresse LONGTEXT NOT NULL,
    code_postal VARCHAR(10) NOT NULL,
    ville VARCHAR(100) NOT NULL,
    puissance_souscrite FLOAT NOT NULL COMMENT 'Power subscription in kW',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_numero_foyer (numero_foyer),
    INDEX idx_is_active (is_active),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Table storing household/property information';
```

### Migration 3: Add Foreign Key to User

```sql
-- Add foreign key from users_user to energy_foyer
ALTER TABLE users_user 
ADD CONSTRAINT fk_users_user_foyer 
FOREIGN KEY (foyer_id) REFERENCES energy_foyer(id) ON DELETE PROTECT;
```

### Migration 4: Create Consommation Table

```sql
-- Create energy consumption records table
CREATE TABLE IF NOT EXISTS energy_consommation (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    foyer_id BIGINT NOT NULL,
    timestamp DATETIME NOT NULL COMMENT 'Measurement time',
    kwh FLOAT NOT NULL COMMENT 'Energy consumption in kWh',
    anomaly_label VARCHAR(50) NULL COMMENT 'ML-detected anomaly label',
    temperature FLOAT NULL COMMENT 'Ambient temperature in °C',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_foyer_timestamp (foyer_id, timestamp DESC),
    INDEX idx_timestamp (timestamp DESC),
    INDEX idx_anomaly_label (anomaly_label),
    
    CONSTRAINT fk_consommation_foyer 
    FOREIGN KEY (foyer_id) REFERENCES energy_foyer(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Energy consumption measurements per household';
```

### Migration 5: Create Anomalie Table

```sql
-- Create anomaly detection table
CREATE TABLE IF NOT EXISTS energy_anomalie (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    consommation_id BIGINT NOT NULL UNIQUE,
    score_confiance FLOAT NOT NULL COMMENT 'Confidence score [0.0, 1.0]',
    severite VARCHAR(20) NOT NULL DEFAULT 'MOYENNE' CHECK (severite IN ('BASSE', 'MOYENNE', 'HAUTE', 'CRITIQUE')),
    statut VARCHAR(20) NOT NULL DEFAULT 'NOUVELLE' CHECK (statut IN ('NOUVELLE', 'CONSULTEE', 'ACQUITTEE')),
    description LONGTEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_statut_created_at (statut, created_at DESC),
    INDEX idx_severite (severite),
    INDEX idx_score_confiance (score_confiance),
    
    CONSTRAINT chk_score_confiance CHECK (score_confiance >= 0.0 AND score_confiance <= 1.0),
    CONSTRAINT chk_severite CHECK (severite IN ('BASSE', 'MOYENNE', 'HAUTE', 'CRITIQUE')),
    CONSTRAINT chk_statut_anomalie CHECK (statut IN ('NOUVELLE', 'CONSULTEE', 'ACQUITTEE')),
    CONSTRAINT fk_anomalie_consommation 
    FOREIGN KEY (consommation_id) REFERENCES energy_consommation(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Detected anomalies in energy consumption';
```

### Migration 6: Create Alerte Table

```sql
-- Create alerts table
CREATE TABLE IF NOT EXISTS energy_alerte (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    anomalie_id BIGINT NOT NULL UNIQUE,
    acquittee BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    acquittee_at DATETIME NULL,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_acquittee_created_at (acquittee, created_at DESC),
    INDEX idx_acquittee (acquittee),
    
    CONSTRAINT fk_alerte_anomalie 
    FOREIGN KEY (anomalie_id) REFERENCES energy_anomalie(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Alerts generated from anomalies, can be acknowledged';
```

### Migration 7: Create ConversationIA Table

```sql
-- Create AI conversation history table
CREATE TABLE IF NOT EXISTS energy_conversationIA (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    utilisateur_id BIGINT NOT NULL,
    question LONGTEXT NOT NULL,
    reponse LONGTEXT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_utilisateur_timestamp (utilisateur_id, timestamp DESC),
    INDEX idx_timestamp (timestamp DESC),
    
    CONSTRAINT fk_conversationIA_user 
    FOREIGN KEY (utilisateur_id) REFERENCES users_user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='User-AI conversations for consumption analysis';
```

### Migration 8: Create ActionLog Table

```sql
-- Create audit log table (RG20 - Action tracking)
CREATE TABLE IF NOT EXISTS energy_actionlog (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    utilisateur_id BIGINT NOT NULL,
    action VARCHAR(100) NOT NULL COMMENT 'Action type (e.g., VIEW_CONSUMPTION, ACKNOWLEDGE_ANOMALY)',
    details JSON NULL COMMENT 'Additional details in JSON format',
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45) NULL COMMENT 'IPv4 or IPv6 address',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_utilisateur_timestamp (utilisateur_id, timestamp DESC),
    INDEX idx_action_timestamp (action, timestamp DESC),
    INDEX idx_timestamp (timestamp DESC),
    
    CONSTRAINT fk_actionlog_user 
    FOREIGN KEY (utilisateur_id) REFERENCES users_user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Audit trail for all user actions (RG20 compliance)';
```

---

## Django Integration

### Step 1: Configure settings.py

```python
# settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'smartmeter_db',
        'USER': 'smartmeter_user',
        'PASSWORD': 'your_secure_password_here',  # Use environment variables!
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'connect_timeout': 10,
        },
        'ATOMIC_REQUESTS': True,
        'AUTOCOMMIT': True,
        'CONN_MAX_AGE': 600,
    }
}

# For production, use environment variables:
# from decouple import config
# 'PASSWORD': config('DB_PASSWORD', default=''),
```

### Step 2: Use Environment Variables (Recommended)

Create `.env` file:
```env
DB_ENGINE=django.db.backends.mysql
DB_NAME=smartmeter_db
DB_USER=smartmeter_user
DB_PASSWORD=your_secure_password_here
DB_HOST=localhost
DB_PORT=3306
```

Update `settings.py`:
```python
from decouple import config

DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE'),
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

### Step 3: Install Required Packages

```bash
pip install mysqlclient
# OR
pip install mysql-connector-python

# For environment variables
pip install python-decouple
```

### Step 4: Create Django Migrations

```bash
# Create migrations from models
python manage.py makemigrations

# Show pending migrations
python manage.py showmigrations

# Apply migrations
python manage.py migrate

# Verify migrations
python manage.py showmigrations --list
```

### Step 5: Create Superuser

```bash
python manage.py createsuperuser
```

---

## Complete Migration Script

Run all migrations at once:

```bash
# Execute this SQL file to set up the entire database
mysql -u root -p smartmeter_db < smartmeter_migrations.sql
```

**smartmeter_migrations.sql** content:
```sql
-- SmartMeter Complete Database Setup Script
-- Execute: mysql -u root -p smartmeter_db < smartmeter_migrations.sql

SET FOREIGN_KEY_CHECKS = 0;

-- Create Foyer table
CREATE TABLE IF NOT EXISTS energy_foyer (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    numero_foyer VARCHAR(50) NOT NULL UNIQUE,
    adresse LONGTEXT NOT NULL,
    code_postal VARCHAR(10) NOT NULL,
    ville VARCHAR(100) NOT NULL,
    puissance_souscrite FLOAT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_numero_foyer (numero_foyer),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create User table (Django auth extension)
CREATE TABLE IF NOT EXISTS users_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME NULL,
    is_superuser BOOLEAN DEFAULT FALSE,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    email VARCHAR(254),
    is_staff BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    date_joined DATETIME NOT NULL,
    role VARCHAR(20) DEFAULT 'RESIDENT',
    foyer_id BIGINT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_foyer (foyer_id),
    INDEX idx_role (role),
    CONSTRAINT fk_user_foyer FOREIGN KEY (foyer_id) 
        REFERENCES energy_foyer(id) ON DELETE PROTECT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Consommation table
CREATE TABLE IF NOT EXISTS energy_consommation (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    foyer_id BIGINT NOT NULL,
    timestamp DATETIME NOT NULL,
    kwh FLOAT NOT NULL,
    anomaly_label VARCHAR(50) NULL,
    temperature FLOAT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_foyer_timestamp (foyer_id, timestamp DESC),
    INDEX idx_timestamp (timestamp DESC),
    CONSTRAINT fk_consommation_foyer FOREIGN KEY (foyer_id) 
        REFERENCES energy_foyer(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Anomalie table
CREATE TABLE IF NOT EXISTS energy_anomalie (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    consommation_id BIGINT NOT NULL UNIQUE,
    score_confiance FLOAT NOT NULL,
    severite VARCHAR(20) DEFAULT 'MOYENNE',
    statut VARCHAR(20) DEFAULT 'NOUVELLE',
    description LONGTEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_statut (statut),
    CONSTRAINT fk_anomalie_consommation FOREIGN KEY (consommation_id) 
        REFERENCES energy_consommation(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Alerte table
CREATE TABLE IF NOT EXISTS energy_alerte (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    anomalie_id BIGINT NOT NULL UNIQUE,
    acquittee BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    acquittee_at DATETIME NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_acquittee (acquittee),
    CONSTRAINT fk_alerte_anomalie FOREIGN KEY (anomalie_id) 
        REFERENCES energy_anomalie(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create ConversationIA table
CREATE TABLE IF NOT EXISTS energy_conversationIA (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    utilisateur_id BIGINT NOT NULL,
    question LONGTEXT NOT NULL,
    reponse LONGTEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_utilisateur (utilisateur_id),
    CONSTRAINT fk_conversationIA_user FOREIGN KEY (utilisateur_id) 
        REFERENCES users_user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create ActionLog table
CREATE TABLE IF NOT EXISTS energy_actionlog (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    utilisateur_id BIGINT NOT NULL,
    action VARCHAR(100) NOT NULL,
    details JSON NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_utilisateur (utilisateur_id),
    INDEX idx_action (action),
    CONSTRAINT fk_actionlog_user FOREIGN KEY (utilisateur_id) 
        REFERENCES users_user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;
```

---

## Backup & Recovery

### Create Backup

```bash
# Full database backup
mysqldump -u smartmeter_user -p smartmeter_db > smartmeter_backup_$(date +%Y%m%d_%H%M%S).sql

# Backup with compression
mysqldump -u smartmeter_user -p smartmeter_db | gzip > smartmeter_backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Restore Backup

```bash
# From SQL file
mysql -u smartmeter_user -p smartmeter_db < smartmeter_backup_20240101_120000.sql

# From compressed file
gunzip < smartmeter_backup_20240101_120000.sql.gz | mysql -u smartmeter_user -p smartmeter_db
```

### Automated Backup Script

Create `backup_smartmeter.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DB_NAME="smartmeter_db"
DB_USER="smartmeter_user"
DATE=$(date +%Y%m%d_%H%M%S)

mysqldump -u $DB_USER -p --all-databases | gzip > $BACKUP_DIR/smartmeter_$DATE.sql.gz

# Keep only last 30 backups
find $BACKUP_DIR -name "smartmeter_*.sql.gz" -mtime +30 -delete

echo "Backup completed: smartmeter_$DATE.sql.gz"
```

Make executable and add to crontab:
```bash
chmod +x backup_smartmeter.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /path/to/backup_smartmeter.sh
```

---

## Useful MySQL Commands

```bash
# Show all databases
SHOW DATABASES;

# Select database
USE smartmeter_db;

# Show all tables
SHOW TABLES;

# Show table structure
DESCRIBE energy_foyer;
DESC energy_consommation;

# Show table status
SHOW TABLE STATUS;

# Check foreign keys
SELECT CONSTRAINT_NAME, TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME 
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
WHERE TABLE_SCHEMA = 'smartmeter_db' AND REFERENCED_TABLE_NAME IS NOT NULL;

# Get table size
SELECT TABLE_NAME, ROUND(((data_length + index_length) / 1024 / 1024), 2) AS `Size (MB)`
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'smartmeter_db';

# Get database size
SELECT SUM(ROUND(((data_length + index_length) / 1024 / 1024), 2)) AS `Database Size (MB)`
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'smartmeter_db';
```

---

## Troubleshooting

### Connection Issues

```bash
# Test connection
mysql -u smartmeter_user -h localhost -p smartmeter_db -e "SELECT 1"

# Check MySQL service status
sudo systemctl status mysql  # Linux
brew services list | grep mysql  # macOS

# Start MySQL service
sudo systemctl start mysql  # Linux
brew services start mysql  # macOS
```

### Common Errors

| Error | Solution |
|-------|----------|
| `Access denied for user` | Check username/password in settings.py |
| `Unknown database` | Create database with `CREATE DATABASE smartmeter_db;` |
| `Foreign key constraint fails` | Check ON DELETE rules or truncate tables in order |
| `Table doesn't exist` | Run `python manage.py migrate` |
| `Charset UTF8MB4 not supported` | Update MySQL version to 5.7.7+ |

---

## Performance Optimization

### Enable Query Cache (MySQL 5.7)
```sql
SET GLOBAL query_cache_size = 268435456;  -- 256MB
SET GLOBAL query_cache_type = 1;
```

### Add Partitioning for Large Tables

```sql
-- Partition energy_consommation by month
ALTER TABLE energy_consommation 
PARTITION BY RANGE (YEAR_MONTH(timestamp)) (
    PARTITION p202401 VALUES LESS THAN (202402),
    PARTITION p202402 VALUES LESS THAN (202403),
    PARTITION p202403 VALUES LESS THAN (202404),
    PARTITION pmax VALUES LESS THAN MAXVALUE
);
```

### Monitor Performance
```sql
-- Show slow queries
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;

-- Check current connections
SHOW PROCESSLIST;

-- Check table stats
ANALYZE TABLE energy_foyer;
ANALYZE TABLE energy_consommation;
```

---

## Additional Resources

- [Django MySQL Documentation](https://docs.djangoproject.com/en/5.0/ref/databases/#mysql-notes)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [MySQLClient Documentation](https://mysqlclient.readthedocs.io/)
- [Django Migrations](https://docs.djangoproject.com/en/5.0/topics/migrations/)

---

## Quick Start Summary

```bash
# 1. Create database and user
mysql -u root -p < create_database.sql

# 2. Install Python packages
pip install mysqlclient python-decouple

# 3. Configure .env file
cp .env.example .env
# Edit .env with database credentials

# 4. Run Django migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Test connection
python manage.py dbshell

# 7. Start Django development server
python manage.py runserver
```

---

**Last Updated:** 2026-04-20  
**Version:** 1.0  
**Database Version:** MySQL 8.0+

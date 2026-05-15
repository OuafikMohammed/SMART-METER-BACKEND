#!/usr/bin/env python
"""
Quick check for MySQL connection and database creation.
"""

import sys

try:
    import pymysql
    print("✅ PyMySQL is installed")
except ImportError:
    print("❌ PyMySQL not installed - installing...")
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'PyMySQL'])
    import pymysql

# Try to connect
try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        port=3306
    )
    cursor = connection.cursor()
    
    # Create database if not exists
    cursor.execute("CREATE DATABASE IF NOT EXISTS smartmeter_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    print("✅ Database smartmeter_db created or already exists")
    
    # Show databases
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    print("\n📋 Available databases:")
    for db in databases:
        print(f"   - {db[0]}")
    
    cursor.close()
    connection.close()
    print("\n✅ MySQL connection successful!")
    
except pymysql.Error as e:
    print(f"❌ MySQL connection failed: {e}")
    print("\n⚠️  Make sure MySQL is running:")
    print("   1. Check if MySQL service is started")
    print("   2. Or start MySQL with: mysql.server start (Mac) or net start MySQL (Windows)")
    sys.exit(1)

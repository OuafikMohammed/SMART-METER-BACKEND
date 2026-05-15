#!/usr/bin/env python
"""Generate SQL schemas for all tables in smartmeter_db"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

# Get all tables
with connection.cursor() as cursor:
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'smartmeter_db' ORDER BY TABLE_NAME")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f'\n{"="*100}')
        print(f'TABLE: {table_name.upper()}')
        print(f'{"="*100}\n')
        
        # Get CREATE TABLE statement
        cursor.execute(f'SHOW CREATE TABLE {table_name}')
        result = cursor.fetchone()
        print(result[1])
        print()
        
        # Get column info
        cursor.execute(f'DESCRIBE {table_name}')
        columns = cursor.fetchall()
        print(f'\nCOLUMNS ({len(columns)}):')
        print(f'{" Field":<35} {" Type":<35} {" Null":<8} {" Key":<8} {" Default":<20}')
        print('-'*110)
        for col in columns:
            field, col_type, null, key, default, extra = col
            default_str = str(default) if default else 'NULL'
            print(f'{field:<35} {str(col_type):<35} {null:<8} {key:<8} {default_str:<20}')
        
        # Get row count
        cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        count = cursor.fetchone()[0]
        print(f'\nTotal Rows: {count}')
        print()

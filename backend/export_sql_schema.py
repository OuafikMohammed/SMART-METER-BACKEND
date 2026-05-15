#!/usr/bin/env python
"""Export all SQL table schemas to a file"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

output = []
output.append("="*120)
output.append("SMARTMETER DATABASE - ALL TABLES SCHEMA (MySQL)")
output.append("="*120)
output.append("")

# Get all tables
with connection.cursor() as cursor:
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'smartmeter_db' ORDER BY TABLE_NAME")
    tables = cursor.fetchall()
    
    for idx, table in enumerate(tables, 1):
        table_name = table[0]
        
        output.append(f"\n{'#'*120}")
        output.append(f"# TABLE {idx}: {table_name.upper()}")
        output.append(f"{'#'*120}\n")
        
        # Get CREATE TABLE statement
        cursor.execute(f'SHOW CREATE TABLE {table_name}')
        result = cursor.fetchone()
        output.append(result[1])
        output.append("\n")
        
        # Get row count
        cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        count = cursor.fetchone()[0]
        output.append(f"-- Total Rows: {count}")
        output.append(f"-- Status: {'✓ EMPTY' if count == 0 else f'✓ {count} rows'}\n")

# Write to file
output_text = "\n".join(output)
with open('database_schema_export.sql', 'w', encoding='utf-8') as f:
    f.write(output_text)

print(output_text)
print(f"\n\n✓ Export saved to: database_schema_export.sql")

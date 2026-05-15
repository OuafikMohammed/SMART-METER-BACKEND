#!/usr/bin/env python
"""
Load fixture data into MySQL with proper foreign key handling.
"""
import json
import pymysql
from pathlib import Path

def load_fixture_to_mysql():
    # Connect to MySQL
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='smartmeter_db',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    
    # Load fixture
    fixture_file = Path(__file__).parent / 'fixtures' / 'initial_data.json'
    with open(fixture_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📂 Loaded {len(data)} objects from fixture")
    
    # Disable foreign key checks
    cursor.execute('SET FOREIGN_KEY_CHECKS=0')
    
    # Group by model
    models = {}
    for item in data:
        model = item['model']
        if model not in models:
            models[model] = []
        models[model].append(item)
    
    print(f"📋 Found {len(models)} models: {', '.join(models.keys())}")
    
    # Load order (dependencies first)
    load_order = [
        'auth.permission',
        'auth.group',
        'django_admin_log',
        'contenttypes.contenttype',
        'sessions.session',
        'users.user',
        'energy.foyer',
        'energy.consommation',
        'energy.anomalie',
        'energy.alerte',
        'energy.conversationIA',
        'energy.actionlog',
        'energy.consumption_reading',
    ]
    
    loaded = 0
    for model_name in load_order:
        if model_name in models:
            items = models[model_name]
            print(f"\n  Loading {len(items)} {model_name} records...")
            for item in items:
                # Map model to table
                table = model_name.split('.')[-1].lower()
                if table == 'contenttype':
                    table = 'django_content_type'
                elif table == 'permission':
                    table = 'auth_permission'
                elif table == 'group':
                    table = 'auth_group'
                elif table == 'conversationia':
                    table = 'energy_conversationia'
                elif table == 'consumption_reading':
                    table = 'energy_consumption_reading'
                elif table == 'actionlog':
                    table = 'energy_actionlog'
                else:
                    table = f'{model_name.split(".")[0]}_{table}'
                
                try:
                    # Insert record with specific id
                    fields = item['fields']
                    pk = item['pk']
                    
                    # Build insert statement
                    columns = ['id'] + list(fields.keys())
                    values = [pk] + list(fields.values())
                    placeholders = ', '.join(['%s'] * len(columns))
                    sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
                    
                    cursor.execute(sql, values)
                    loaded += 1
                    
                except Exception as e:
                    print(f"    ⚠️ Error loading {model_name} pk={pk}: {e}")
                    # Try to continue
    
    # Re-enable foreign key checks
    cursor.execute('SET FOREIGN_KEY_CHECKS=1')
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n✅ Loaded {loaded} records to MySQL")

if __name__ == '__main__':
    try:
        load_fixture_to_mysql()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

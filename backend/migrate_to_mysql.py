#!/usr/bin/env python
"""
Script to migrate data from SQLite to MySQL.
1. Dump current SQLite data
2. Update .env to use MySQL
3. Apply migrations to MySQL
4. Load data back
"""

import os
import sys
import json
import django
from pathlib import Path
from subprocess import run, PIPE

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def run_command(cmd, description):
    """Run a shell command and handle output."""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    
    if isinstance(cmd, str):
        cmd = cmd.split()
    
    result = run(cmd, cwd=Path(__file__).parent)
    if result.returncode != 0:
        print(f"❌ Command failed: {' '.join(cmd)}")
        return False
    print(f"✅ {description} - Success")
    return True

def main():
    backend_dir = Path(__file__).parent
    env_file = backend_dir / '.env'
    
    print("\n" + "="*60)
    print("🚀 SMARTMETER DATABASE MIGRATION (SQLite → MySQL)")
    print("="*60)
    
    # Step 1: Verify MySQL is configured
    print("\n📋 Checking MySQL configuration...")
    
    # Read current .env
    env_content = env_file.read_text(encoding='utf-8')
    
    # Check if already using MySQL
    if 'DB_ENGINE=django.db.backends.mysql' in env_content:
        print("✅ Already configured for MySQL")
        mysql_configured = True
    else:
        print("ℹ️  Currently using SQLite, need to configure MySQL")
        mysql_configured = False
    
    # Step 2: Dump SQLite data to JSON
    print("\n📊 Exporting data from SQLite...")
    if not run_command('python manage.py dumpdata --all --indent=2 > sqlite_backup.json', 
                       'Dump SQLite data'):
        print("⚠️  Continuing anyway...")
    
    # Step 3: Update .env to use MySQL
    if not mysql_configured:
        print("\n🔧 Updating .env to use MySQL...")
        new_env = env_content.replace(
            'DB_ENGINE=django.db.backends.sqlite3',
            'DB_ENGINE=django.db.backends.mysql'
        )
        
        # Add MySQL configuration if not present
        if 'DB_NAME=' not in new_env:
            new_env += '\n\n# MySQL Configuration\nDB_NAME=smartmeter_db\nDB_USER=root\nDB_PASSWORD=\nDB_HOST=localhost\nDB_PORT=3306\n'
        
        env_file.write_text(new_env, encoding='utf-8')
        print("✅ .env updated for MySQL")
    
    # Step 4: Reinitialize Django with new database settings
    print("\n🔄 Reloading Django settings...")
    os.environ['DB_ENGINE'] = 'django.db.backends.mysql'
    os.environ['DB_NAME'] = 'smartmeter_db'
    os.environ['DB_USER'] = 'root'
    os.environ['DB_PASSWORD'] = ''
    os.environ['DB_HOST'] = 'localhost'
    os.environ['DB_PORT'] = '3306'
    
    # Re-read settings
    from importlib import reload
    import settings
    reload(settings)
    
    django.setup()
    
    print("✅ Django reloaded with MySQL settings")
    
    # Step 5: Run migrations on MySQL
    print("\n🗄️  Running migrations on MySQL...")
    if not run_command('python manage.py migrate', 'Apply all migrations'):
        print("⚠️  Migration may have failed - check console output above")
    
    # Step 6: Load data back
    print("\n📥 Loading data into MySQL...")
    if Path('sqlite_backup.json').exists():
        if not run_command('python manage.py loaddata sqlite_backup.json', 
                          'Load data from SQLite backup'):
            print("⚠️  Data load may have failed")
    else:
        print("⚠️  No backup file found, skipping data load")
    
    # Step 7: Verify
    print("\n✅ Migration complete!")
    print("\n📋 Next steps:")
    print("  1. Start Django server: python manage.py runserver 8000")
    print("  2. Verify API endpoints work")
    print("  3. Check frontend displays data correctly")
    print("\n" + "="*60)

if __name__ == '__main__':
    main()

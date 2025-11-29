#!/usr/bin/env python3
"""
Management CLI for FastAPI application
Usage: python manage.py <command> [options]
"""

import argparse
import subprocess
import sys
from pathlib import Path
from sqlalchemy import inspect, text
from app.database.base import engine

# ============================================================================
# Utility Functions
# ============================================================================
def run_command(cmd, check=True):
    """Run a shell command"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        sys.exit(1)
    return result

# ============================================================================
# Migration Commands
# ============================================================================
def migrate():
    """Run pending migrations"""
    print("🔄 Running migrations...")
    run_command("alembic upgrade head")
    print("✅ Migrations completed!")


def migrate_rollback(steps=1):
    """Rollback migrations"""
    print(f"⏪ Rolling back {steps} migration(s)...")
    run_command(f"alembic downgrade -{steps}")
    print("✅ Rollback completed!")


def migrate_reset():
    """Reset all migrations (rollback to base)"""
    print("⚠️  Resetting all migrations...")
    confirm = input("Are you sure? This will rollback ALL migrations (yes/no): ")
    if confirm.lower() != 'yes':
        print("Cancelled.")
        return
    run_command("alembic downgrade base")
    print("✅ All migrations rolled back!")


def migrate_refresh():
    """Reset and re-run all migrations"""
    print("🔄 Refreshing migrations (reset + migrate)...")
    migrate_reset()
    migrate()


def migrate_status():
    """Show migration status"""
    print("📊 Migration Status:")
    print("-" * 50)
    run_command("alembic current")
    print("\n📜 Migration History:")
    print("-" * 50)
    run_command("alembic history")


def migrate_make(message):
    """Create a new migration"""
    if not message:
        print("❌ Error: Migration message is required")
        print("Usage: python manage.py migrate:make 'your message here'")
        sys.exit(1)
    print(f"📝 Creating migration: {message}")
    run_command(f'alembic revision --autogenerate -m "{message}"')
    print("✅ Migration created!")


# ============================================================================
# Database Management Commands
# ============================================================================
def db_reset():
    """Drop all tables and clear alembic_version"""
    print("⚠️  DANGER: This will drop ALL tables!")
    confirm = input("Are you sure? Type 'yes' to continue: ")
    if confirm.lower() != 'yes':
        print("Cancelled.")
        return
    
    print("🗑️  Dropping all tables...")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    with engine.connect() as conn:
        # Drop alembic_version first
        conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
        # Drop all other tables
        for table in tables:
            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
        conn.commit()
    
    print(f"✅ Dropped {len(tables)} table(s): {', '.join(tables)}")


def db_clear_alembic():
    """Clear alembic_version table (fixes migration tracking issues)"""
    print("🧹 Clearing alembic_version table...")
    try:
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
            conn.commit()
        print("✅ alembic_version table cleared!")
        print("💡 Now you can create a fresh migration with: python manage.py migrate:make 'message'")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure your database is running and accessible")


def db_wipe():
    """Drop all tables and clear alembic_version"""
    print("⚠️  DANGER: This will drop ALL tables!")
    confirm = input("Are you sure? Type 'yes' to continue: ")
    if confirm.lower() != 'yes':
        print("Cancelled.")
        return
    
    print("🗑️  Dropping all tables...")
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            print("ℹ️  No tables found.")
            return
        
        with engine.connect() as conn:
            # Drop alembic_version first
            conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
            # Drop all other tables
            for table in tables:
                if table != 'alembic_version':  # Already dropped
                    conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    print(f"  Dropped: {table}")
            conn.commit()
        
        print(f"✅ Dropped {len(tables)} table(s): {', '.join(tables)}")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure your database is running and accessible")


def db_fresh():
    """Drop all tables, clear migrations, and re-run migrations"""
    print("🔄 Fresh migration (reset DB + migrate)...")
    db_reset()
    # Clear migration files
    migrations_dir = Path("app/database/migrations")
    alembic_versions = Path("alembic/versions")
    
    for file in migrations_dir.glob("*.py"):
        if file.name != "__init__.py":
            file.unlink()
            print(f"  Deleted: {file}")
    
    for file in alembic_versions.glob("*.py"):
        if file.name != "__init__.py":
            file.unlink()
            print(f"  Deleted: {file}")
    
    print("✅ Database reset and migration files cleared!")
    print("💡 Run 'python manage.py migrate:make' to create a new migration")


def migrate_fresh():
    """Alias for db:fresh"""
    db_fresh()


# ============================================================================
# Shell Commands
# ============================================================================
def tinker():
    """Open interactive shell"""
    print("🐚 Opening interactive shell...")
    run_command("python shell.py", check=False)

# ============================================================================
# CLI Setup
# ============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Management CLI for FastAPI application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage.py migrate              # Run migrations
  python manage.py migrate:rollback     # Rollback last migration
  python manage.py migrate:rollback 3    # Rollback 3 migrations
  python manage.py migrate:reset         # Rollback all migrations
  python manage.py migrate:refresh      # Reset + migrate
  python manage.py migrate:status       # Show migration status
  python manage.py migrate:make "add users table"  # Create migration
  python manage.py db:reset             # Drop all tables
  python manage.py db:wipe             # Drop all tables (same as db:reset)
  python manage.py db:clear-alembic     # Clear alembic_version table
  python manage.py db:fresh             # Reset DB + clear migrations
  python manage.py tinker               # Open interactive shell
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Migrate commands
    migrate_parser = subparsers.add_parser('migrate', help='Run pending migrations')
    migrate_parser.set_defaults(func=migrate)
    
    rollback_parser = subparsers.add_parser('migrate:rollback', help='Rollback migrations')
    rollback_parser.add_argument('steps', type=int, nargs='?', default=1, help='Number of steps to rollback')
    rollback_parser.set_defaults(func=lambda args: migrate_rollback(args.steps))
    
    reset_parser = subparsers.add_parser('migrate:reset', help='Reset all migrations')
    reset_parser.set_defaults(func=migrate_reset)
    
    refresh_parser = subparsers.add_parser('migrate:refresh', help='Reset and re-run migrations')
    refresh_parser.set_defaults(func=migrate_refresh)
    
    status_parser = subparsers.add_parser('migrate:status', help='Show migration status')
    status_parser.set_defaults(func=migrate_status)
    
    make_parser = subparsers.add_parser('migrate:make', help='Create a new migration')
    make_parser.add_argument('message', help='Migration message')
    make_parser.set_defaults(func=lambda args: migrate_make(args.message))
    
    # Database commands
    db_reset_parser = subparsers.add_parser('db:reset', help='Drop all tables')
    db_reset_parser.set_defaults(func=db_reset)
    
    db_wipe_parser = subparsers.add_parser('db:wipe', help='Drop all tables')
    db_wipe_parser.set_defaults(func=db_wipe)
    
    db_clear_alembic_parser = subparsers.add_parser('db:clear-alembic', help='Clear alembic_version table')
    db_clear_alembic_parser.set_defaults(func=db_clear_alembic)
    
    db_fresh_parser = subparsers.add_parser('db:fresh', help='Drop all tables and clear migrations')
    db_fresh_parser.set_defaults(func=db_fresh)
    
    migrate_fresh_parser = subparsers.add_parser('migrate:fresh', help='Alias for db:fresh')
    migrate_fresh_parser.set_defaults(func=migrate_fresh)
    
    # Shell command
    tinker_parser = subparsers.add_parser('tinker', help='Open interactive shell')
    tinker_parser.set_defaults(func=tinker)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Handle commands that need args differently
    if args.command in ['migrate:rollback', 'migrate:make']:
        args.func(args)
    else:
        args.func()


if __name__ == '__main__':
    main()
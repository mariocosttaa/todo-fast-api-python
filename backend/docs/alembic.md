# Alembic Migration Commands

This document covers the most commonly used Alembic commands for database migrations.

## Basic Migration Commands

### Run Migrations
Apply all pending migrations to the database:
```bash
alembic upgrade head
```

### Check Current Migration Status
See which migration is currently applied:
```bash
alembic current
```

### View Migration History
List all migrations (applied and pending):
```bash
alembic history
```

### View Detailed History
See migration history with more details:
```bash
alembic history --verbose
```

## Creating Migrations

### Auto-generate Migration
Create a new migration based on model changes:
```bash
alembic revision --autogenerate -m "your migration message"
```

### Create Empty Migration
Create a blank migration file for manual edits:
```bash
alembic revision -m "your migration message"
```

## Rolling Back Migrations

### Rollback One Migration
Rollback the last applied migration:
```bash
alembic downgrade -1
```

### Rollback Multiple Migrations
Rollback the last N migrations:
```bash
alembic downgrade -3
```

### Rollback to Specific Revision
Rollback to a specific migration revision:
```bash
alembic downgrade <revision_id>
```

### Rollback All Migrations
Rollback to the base (remove all migrations):
```bash
alembic downgrade base
```

## Advanced Commands

### Upgrade to Specific Revision
Upgrade to a specific migration:
```bash
alembic upgrade <revision_id>
```

### Show SQL for Migration
Preview the SQL that will be executed (without running it):
```bash
alembic upgrade head --sql
```

### Show SQL for Downgrade
Preview the SQL for rollback:
```bash
alembic downgrade -1 --sql
```

### Merge Branches
If you have multiple migration branches, merge them:
```bash
alembic merge -m "merge message" <revision1> <revision2>
```

## Common Workflows

### Fresh Start (Development)
Drop all tables and start fresh:
```bash
# 1. Drop all tables manually or use database tools
# 2. Clear alembic_version table
# 3. Create a new initial migration
alembic revision --autogenerate -m "initial migration"
alembic upgrade head
```

### Reset and Re-migrate
```bash
# Rollback all migrations
alembic downgrade base

# Re-apply all migrations
alembic upgrade head
```

### Check What Will Be Applied
Before running migrations, see what will happen:
```bash
alembic upgrade head --sql
```

## Migration File Location

Migrations are stored in: `app/database/migrations/`

Each migration file contains:
- `revision`: Unique identifier for the migration
- `down_revision`: Previous migration in the chain
- `upgrade()`: Function that applies the migration
- `downgrade()`: Function that rolls back the migration

## Troubleshooting

### Migration Tracking Issues
If migrations get out of sync:
```bash
# Check current status
alembic current

# View history
alembic history

# If needed, manually fix the alembic_version table
```

### Clear Alembic Version Table
If you need to reset migration tracking:
```sql
DROP TABLE IF EXISTS alembic_version CASCADE;
```

Then create a fresh migration:
```bash
alembic revision --autogenerate -m "fresh start"
```

## Best Practices

1. **Always commit migration files** to version control
2. **Test migrations** on a development database first
3. **Review auto-generated migrations** before applying
4. **Use descriptive messages** when creating migrations
5. **Never edit applied migrations** - create new ones instead
6. **Backup database** before running migrations in production


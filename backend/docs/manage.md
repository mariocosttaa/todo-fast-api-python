# Interactive Shell (manage.py)

The `manage.py` file provides an interactive Python shell for database operations and model management, similar to Django's shell or Rails console.

## Usage

Run the interactive shell:
```bash
python manage.py
```

This opens an interactive Python REPL with pre-configured database session and helper functions.

## Available Models

The following models are available in the shell:
- `User` - User model
- `Todo` - Todo item model
- `RefreshToken` - Refresh token model

## Available Utilities

- `session` - SQLModel database session (for advanced queries)
- `datetime` - Python datetime utilities
- `uuid` - UUID generation utilities

## Generic ORM Functions

These functions work with any model class:

### `all(model_class)`
Get all records from a model.

**Example:**
```python
users = all(User)
todos = all(Todo)
```

### `find(model_class, id)`
Find a record by its ID.

**Example:**
```python
user = find(User, uuid.UUID('123e4567-e89b-12d3-a456-426614174000'))
```

### `first(model_class)`
Get the first record from a model.

**Example:**
```python
first_user = first(User)
```

### `count(model_class)`
Count total records in a model.

**Example:**
```python
user_count = count(User)
```

### `create(model_class, **kwargs)`
Create a new record.

**Example:**
```python
new_user = create(User, name='John', email='john@example.com', hashed_password='hashed')
```

### `save(instance)`
Save or update a record.

**Example:**
```python
user.name = 'Jane'
save(user)
```

### `delete(instance)`
Delete a record from the database.

**Example:**
```python
delete(user)
```

## Model Static Methods

Each model also has static methods for convenience:

### `Model.all()`
Get all records.

**Example:**
```python
users = User.all()
```

### `Model.find(id)`
Find a record by ID.

**Example:**
```python
user = User.find(uuid.UUID('123e4567-e89b-12d3-a456-426614174000'))
```

### `Model.first()`
Get the first record.

**Example:**
```python
first_user = User.first()
```

### `Model.count()`
Count records.

**Example:**
```python
user_count = User.count()
```

### `Model.create(**kwargs)`
Create a new record.

**Example:**
```python
new_user = User.create(name='John', email='john@example.com', hashed_password='hashed')
```

## Complete Examples

### Working with Users

```python
# Get all users
users = User.all()

# Find user by ID
user = User.find(uuid.UUID('some-uuid-here'))

# Get first user
first_user = User.first()

# Count users
user_count = User.count()

# Create a new user
new_user = User.create(
    name='John Doe',
    email='john@example.com',
    hashed_password='hashed_password_here'
)

# Update a user
user.name = 'Jane Doe'
save(user)

# Delete a user
delete(user)
```

### Working with Todos

```python
# Get all todos
todos = Todo.all()

# Find todo by ID
todo = Todo.find(some_uuid)

# Create a new todo
new_todo = Todo.create(
    title='My Todo',
    user_id=user.id,
    order=1
)
```

### Advanced Queries

For more complex queries, use the `session` directly:

```python
from sqlmodel import select

# Find users by email
users = session.exec(
    select(User).where(User.email == 'test@example.com')
).all()

# Complex queries with joins, filters, etc.
todos = session.exec(
    select(Todo).where(Todo.user_id == user.id).order_by(Todo.order)
).all()
```

## Database Management Functions

### `drop_all_tables()`
⚠️ **DANGEROUS** - Drops all tables and clears alembic_version.

**Example:**
```python
drop_all_tables()
```

### `reset_database()`
Complete database reset: drops all tables and clears alembic version.

**Example:**
```python
reset_database()
```

## Tips

1. **Use tab completion** - The shell supports tab completion for model names and methods
2. **Import additional modules** - You can import any Python module you need
3. **Access session directly** - Use `session` for complex queries that helper functions don't cover
4. **Exit the shell** - Type `exit()` or press `Ctrl+D` to exit

## Common Use Cases

- **Quick data inspection**: Check what data exists in your database
- **Testing queries**: Try out SQLModel queries before adding them to your code
- **Data manipulation**: Create, update, or delete records for testing
- **Debugging**: Inspect model instances and relationships
- **Development**: Seed data or test model relationships


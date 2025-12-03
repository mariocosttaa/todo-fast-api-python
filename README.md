# Todo FastAPI

A FastAPI-based Todo application with SQLModel, Alembic migrations, and PostgreSQL.

## Features

- 🚀 FastAPI framework for high-performance API
- 🗄️ SQLModel for database models and ORM
- 📦 Alembic for database migrations
- 🐘 PostgreSQL database support
- 🔐 JWT authentication (with refresh tokens)
- 🐚 Interactive shell for database operations
- 🛠️ Code generators for models, routers, controllers
- 🐳 Docker support

## Project Structure

```
todo-fastapi/
├── alembic/             # Alembic configuration
│   ├── env.py           # Alembic environment setup
│   └── versions/        # Migration files (legacy location)
├── app/
│   ├── database/
│   │   ├── base.py      # Database base configuration
│   │   └── migrations/  # Migration files
│   ├── models/          # SQLModel models
│   │   ├── user.py
│   │   ├── todo.py
│   │   └── refreshToken.py
│   ├── routers/         # API route handlers
│   └── main.py          # FastAPI application entry point
├── manage.py            # Interactive shell
├── generate.py          # Code generator for models, routers, controllers
├── alembic.ini          # Alembic configuration
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Docker Compose configuration
└── Dockerfile           # Docker image configuration
```

## Prerequisites

- Python 3.11+
- PostgreSQL 12+
- pip

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd todo-fastapi
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db
# OR use individual variables:
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=todo_db
```

5. **Run database migrations**
```bash
alembic upgrade head
```

## Running the Application

### Development Server
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Interactive API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Database Migrations

This project uses Alembic for database migrations. See [alembic.md](./alembic.md) for detailed migration commands.

### Common Migration Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "your message"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Check migration status
alembic current

# View migration history
alembic history
```

For more details, see [alembic.md](./alembic.md).

## Code Generators

The project includes a generator script to quickly create models, routers, controllers, and request schemas:

```bash
python3 generate.py --help
```

### Generate a Model

```bash
# Basic model
python3 generate.py model Product

# Model with fields
python3 generate.py model Product --fields name:str:max_length=100,index email:str:unique,index price:float
```

**Field format:** `name:type:options`
- **name**: Field name (snake_case)
- **type**: Python type (str, int, float, bool, UUID, datetime, etc.)
- **options**: Comma-separated options:
  - `unique` - Add unique constraint
  - `index` - Add database index
  - `max_length=N` - Set max length (e.g., `max_length=100`)
  - `foreign_key=table.column` - Add foreign key (e.g., `foreign_key=users.id`)
  - `optional` - Make field optional

**Example:**
```bash
python3 generate.py model Category --fields name:str:max_length=50,index description:str:optional slug:str:unique,index
```

### Generate a Router

```bash
python3 generate.py router ProductRouter
```

This creates a router with CRUD endpoints:
- `GET /products` - List all
- `GET /products/{id}` - Get by ID
- `POST /products` - Create (TODO: needs request validation)
- `PUT /products/{id}` - Update (TODO: needs request validation)
- `DELETE /products/{id}` - Delete

**Don't forget to include it in `app/main.py`:**
```python
from app.routers import product_router
app.include_router(product_router.router)
```

### Generate a Controller

```bash
python3 generate.py controller ProductController
```

Creates a controller class with static methods for CRUD operations that can be used in routers.

### Generate Request Schemas

```bash
python3 generate.py request ProductRequest --fields name:str email:str:optional price:float
```

Creates Pydantic request schemas for validation:
- `CreateProductRequest` - For creating resources
- `UpdateProductRequest` - For updating resources (all fields optional)

## Interactive Shell

The project includes an interactive shell for database operations:

```bash
python3 manage.py
```

This opens a Python REPL with:
- Pre-configured database session
- Helper functions for CRUD operations
- Direct access to all models

**Example usage:**
```python
# Get all users
users = User.all()

# Create a new user
user = User.create(name='John', email='john@example.com', hashed_password='hashed')

# Find user by ID
user = User.find(uuid.UUID('some-uuid'))
```

For complete documentation, see [systemDoc/manage.md](./systemDoc/manage.md).

## Docker

### Using Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Building Docker Image

```bash
docker build -t todo-fastapi .
docker run -p 8000:8000 todo-fastapi
```

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check endpoint

More endpoints will be added as the application develops.

## Development

### Code Structure

- **Models**: Located in `app/models/` - SQLModel classes
- **Routers**: Located in `app/routers/` - API route handlers
- **Database**: Configuration in `app/database/base.py`
- **Migrations**: Stored in `app/database/migrations/`

### Adding New Models

**Using the generator (recommended):**
```bash
python3 generate.py model Product --fields name:str:index price:float
```

**Manual steps:**
1. Create model in `app/models/`
2. Import in `app/models/__init__.py` (auto-updated by generator)
3. Create migration: `alembic revision --autogenerate -m "add new model"`
4. Apply migration: `alembic upgrade head`

### Adding New Routes

**Using the generator (recommended):**
```bash
python3 generate.py router ProductRouter
```

**Manual steps:**
1. Create router in `app/routers/`
2. Import and include in `app/main.py`:
   ```python
   from app.routers import product_router
   app.include_router(product_router.router)
   ```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## Documentation

- [Alembic Commands](./alembic.md) - Database migration guide
- [Interactive Shell](./systemDoc/manage.py.md) - Shell usage documentation

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | Full PostgreSQL connection string | Yes* |
| `POSTGRES_USER` | PostgreSQL username | Yes* |
| `POSTGRES_PASSWORD` | PostgreSQL password | Yes* |
| `POSTGRES_DB` | PostgreSQL database name | Yes* |

*Either `DATABASE_URL` or all three `POSTGRES_*` variables are required.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license here]

## Support

For issues and questions, please open an issue on GitHub.

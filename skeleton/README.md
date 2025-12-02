# Generator Templates

This folder contains template files used by the `generate.py` script to create new files in the project.

## Available Templates

### 1. `controller.txt`
Controller skeleton with:
- HTTPException import
- Logger setup (`logger = get_logger(__name__)`)
- Session and typing imports
- Basic CRUD method structure

### 2. `model.txt`
SQLAlchemy model skeleton with:
- Standard imports (UUID, DateTime, etc.)
- Base model structure
- Default fields (id, created_at, updated_at)

### 3. `request.txt`
Pydantic request schema skeleton with:
- BaseModel and Field imports
- Optional typing support

### 4. `test_controller.txt`
Controller test skeleton with:
- pytest imports
- TestClient and Session fixtures
- Example test structure

### 5. `test_router.txt`
Router/endpoint test skeleton with:
- pytest imports
- TestClient fixture
- Health check example
- Endpoint test example

### 6. `test_generic.txt`
Generic test skeleton with:
- pytest imports
- Multiple fixtures (client, db_session, fake_user_data)
- Flexible test structure

## Usage

These templates are automatically loaded by `generate.py` when you run commands like:

```bash
# Generate a controller (includes logger!)
python3 generate.py controller ProductController

# Generate a model
python3 generate.py model Product

# Generate a request
python3 generate.py request CreateProductRequest

# Generate tests
python3 generate.py test ProductController --type controller
```

## Editing Templates

To modify the generated code structure:
1. Edit the corresponding `.txt` file in this folder
2. Use `${VariableName}` for template variables
3. The changes will apply to all future generated files

## Template Variables

Common variables used:
- `${ModelName}` - Model class name (PascalCase)
- `${ControllerName}` - Controller class name (PascalCase)
- `${RequestName}` - Request class name (PascalCase)
- `${table_name}` - Database table name (snake_case, plural)
- `${model_name}` - Model import path (snake_case)
- `${controller_snake}` - Controller file name (snake_case)
- `${fields}` - Request fields (for request.txt)

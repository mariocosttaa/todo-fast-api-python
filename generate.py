#!/usr/bin/env python3
"""
Simple generator script for creating models, controllers, requests, and tests
Usage:
    python3 generate.py model <ModelName> [or Folder/ModelName for nested]
    python3 generate.py controller <ControllerName> [or Folder/ControllerName for nested]
    python3 generate.py request <RequestName> [--fields field1:type field2:type:optional]
    python3 generate.py test <TestName> [--type controller|router|generic]
    python3 generate.py key
"""
import argparse
import secrets
import re
from pathlib import Path
from string import Template

# Project paths
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "app" / "models"
CONTROLLERS_DIR = BASE_DIR / "app" / "controllers"
REQUESTS_DIR = BASE_DIR / "app" / "requests"
TESTS_DIR = BASE_DIR / "tests"
SKELETON_DIR = BASE_DIR / "skeleton"
ENV_FILE = BASE_DIR / ".env"

# Load templates from skeleton folder
def load_template(template_name: str) -> Template:
    """Load a template from the skeleton folder"""
    template_file = SKELETON_DIR / f"{template_name}.txt"
    if not template_file.exists():
        raise FileNotFoundError(f"Template file not found: {template_file}")
    return Template(template_file.read_text())

# Templates loaded from skeleton folder
MODEL_TEMPLATE = load_template("model")
CONTROLLER_TEMPLATE = load_template("controller")
REQUEST_TEMPLATE = load_template("request")
TEST_CONTROLLER_TEMPLATE = load_template("test_controller")
TEST_ROUTER_TEMPLATE = load_template("test_router")
TEST_GENERIC_TEMPLATE = load_template("test_generic")

def to_snake_case(name: str) -> str:
    """Convert PascalCase to snake_case"""
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def to_plural(name: str) -> str:
    """Simple pluralization"""
    if name.endswith('y'):
        return name[:-1] + 'ies'
    elif name.endswith('s') or name.endswith('x') or name.endswith('z'):
        return name + 'es'
    else:
        return name + 's'

def parse_path_with_folders(name: str) -> tuple:
    """Parse name with folder path like 'Auth/RegisterRequest' -> ('auth', 'RegisterRequest')"""
    parts = name.replace('\\', '/').split('/')
    if len(parts) > 1:
        folder_path = '/'.join([to_snake_case(part) for part in parts[:-1]])
        class_name = parts[-1]
        return folder_path, class_name
    return None, name

def parse_field(field_str: str) -> dict:
    """Parse field string like 'name:str' or 'email:EmailStr:optional'"""
    parts = field_str.split(':')
    field_name = parts[0].strip()
    field_type = parts[1].strip() if len(parts) > 1 else 'str'
    is_optional = len(parts) > 2 and parts[2].strip().lower() in ['optional', 'opt', 'o']
    
    return {
        'name': field_name,
        'type': field_type,
        'optional': is_optional
    }

def format_field(field_info: dict) -> str:
    """Format a field for the request template"""
    field_name = field_info['name']
    field_type = field_info['type']
    is_optional = field_info['optional']
    
    # Handle special types
    if field_type.lower() == 'email':
        field_type = 'EmailStr'
        import_line = "from pydantic import BaseModel, Field, EmailStr\n"
    else:
        import_line = ""
    
    # Format the field
    if is_optional:
        field_def = f"    {field_name}: Optional[{field_type}] = Field(None"
    else:
        field_def = f"    {field_name}: {field_type} = Field(..."
    
    # Add common validations based on type
    if field_type.lower() in ['str', 'emailstr']:
        if 'password' in field_name.lower():
            field_def += ", min_length=8, max_length=100"
        elif 'name' in field_name.lower() or 'title' in field_name.lower():
            field_def += ", min_length=1, max_length=50"
        elif 'email' in field_name.lower():
            field_def += ""
    elif field_type.lower() in ['int', 'float']:
        field_def += ""
    
    field_def += ")"
    
    return field_def, import_line

def generate_model(model_name: str):
    """Generate a new model skeleton file"""
    folder_path, class_name = parse_path_with_folders(model_name)
    
    # Build file path
    if folder_path:
        model_dir = MODELS_DIR / folder_path
        model_file = model_dir / f"{to_snake_case(class_name)}.py"
        import_path = f"app.models.{folder_path.replace('/', '.')}.{to_snake_case(class_name)}"
    else:
        model_dir = MODELS_DIR
        model_file = model_dir / f"{to_snake_case(class_name)}.py"
        import_path = f"app.models.{to_snake_case(class_name)}"
    
    if model_file.exists():
        print(f"❌ Model {model_name} already exists at {model_file}")
        return False
    
    # Create directory if needed
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate model content
    content = MODEL_TEMPLATE.substitute(
        ModelName=class_name,
        table_name=to_plural(to_snake_case(class_name))
    )
    
    # Write file
    model_file.write_text(content)
    print(f"✅ Created model: {model_file}")
    
    # Update __init__.py (only for root models, not nested)
    if not folder_path:
        update_models_init(class_name)
    
    return True

def update_models_init(model_name: str):
    """Update app/models/__init__.py to include new model"""
    init_file = MODELS_DIR / "__init__.py"
    
    if not init_file.exists():
        init_file.write_text(f"from app.models.{to_snake_case(model_name)} import {model_name}\n\n__all__ = [\"{model_name}\"]\n")
        return
    
    content = init_file.read_text()
    model_snake = to_snake_case(model_name)
    
    # Add import if not exists
    import_line = f"from app.models.{model_snake} import {model_name}"
    if import_line not in content:
        # Find the last import line
        lines = content.split('\n')
        import_lines = [l for l in lines if l.startswith('from app.models')]
        if import_lines:
            last_import_idx = max(i for i, line in enumerate(lines) if line.startswith('from app.models'))
            lines.insert(last_import_idx + 1, import_line)
        else:
            lines.insert(0, import_line)
        content = '\n'.join(lines)
    
    # Update __all__
    if '__all__' in content:
        import re
        # Find __all__ list
        pattern = r'__all__\s*=\s*\[(.*?)\]'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            all_list = match.group(1)
            if model_name not in all_list:
                # Add to __all__
                all_items = [item.strip().strip('"\'') for item in all_list.split(',') if item.strip()]
                all_items.append(model_name)
                new_all = '__all__ = [' + ', '.join(f'"{item}"' for item in all_items) + ']'
                content = re.sub(pattern, new_all, content, flags=re.DOTALL)
    
    init_file.write_text(content)
    print(f"✅ Updated {init_file}")

def generate_controller(controller_name: str):
    """Generate a new controller file"""
    folder_path, class_name = parse_path_with_folders(controller_name)
    
    model_name = class_name.replace('Controller', '').replace('controller', '')
    if not model_name:
        model_name = class_name
    
    # Build file path
    if folder_path:
        controller_dir = CONTROLLERS_DIR / folder_path
        controller_file = controller_dir / f"{to_snake_case(class_name)}.py"
    else:
        controller_dir = CONTROLLERS_DIR
        controller_file = controller_dir / f"{to_snake_case(class_name)}.py"
    
    if controller_file.exists():
        print(f"❌ Controller {controller_name} already exists at {controller_file}")
        return False
    
    # Create directory if needed
    controller_dir.mkdir(parents=True, exist_ok=True)
    
    model_snake = to_snake_case(model_name)
    
    # Build model import path (assume model is in same folder structure)
    # Template expects path after "app.models." so we just need the relative path
    if folder_path:
        model_import_path = f"{folder_path.replace('/', '.')}.{model_snake}"
    else:
        model_import_path = model_snake
    
    content = CONTROLLER_TEMPLATE.substitute(
        ControllerName=class_name,
        ModelName=model_name,
        model_name=model_import_path
    )
    
    controller_file.write_text(content)
    print(f"✅ Created controller: {controller_file}")
    
    return True

def generate_request(request_name: str, fields: list):
    """Generate a new request schema file"""
    folder_path, class_name = parse_path_with_folders(request_name)
    
    # Build file path
    if folder_path:
        request_dir = REQUESTS_DIR / folder_path
        request_file = request_dir / f"{to_snake_case(class_name)}.py"
    else:
        request_dir = REQUESTS_DIR
        request_file = request_dir / f"{to_snake_case(class_name)}.py"
    
    if request_file.exists():
        print(f"❌ Request {request_name} already exists at {request_file}")
        return False
    
    # Create directory if needed
    request_dir.mkdir(parents=True, exist_ok=True)
    
    # If no fields provided, create empty template
    if not fields or len(fields) == 0:
        content = f"""from pydantic import BaseModel

class {class_name}(BaseModel):
    pass
"""
        
        request_file.write_text(content)
        print(f"✅ Created request: {request_file}")
        print("💡 Add fields manually to the file")
        return True
    
    # Parse fields
    parsed_fields = [parse_field(f) for f in fields]
    
    # Format fields
    field_lines = []
    imports_needed = set()
    
    for field_info in parsed_fields:
        field_def, import_line = format_field(field_info)
        field_lines.append(field_def)
        if import_line and 'EmailStr' in import_line:
            imports_needed.add('EmailStr')
        if field_info['optional']:
            imports_needed.add('Optional')
    
    # Build imports
    import_lines = ["from pydantic import BaseModel, Field"]
    if 'EmailStr' in imports_needed:
        import_lines[0] = "from pydantic import BaseModel, Field, EmailStr"
    if 'Optional' in imports_needed:
        import_lines.append("from typing import Optional")
    
    # Combine imports
    imports_section = '\n'.join(import_lines) + '\n\n'
    
    # Combine fields
    fields_section = '\n'.join(field_lines)
    
    # Generate content
    content = imports_section + REQUEST_TEMPLATE.substitute(
        RequestName=class_name,
        fields=fields_section
    )
    
    # Write file
    request_file.write_text(content)
    print(f"✅ Created request: {request_file}")
    
    return True

def generate_test(test_name: str, test_type: str = "generic"):
    """Generate a new test skeleton file"""
    folder_path, class_name = parse_path_with_folders(test_name)
    
    # Remove 'Test' prefix if present
    if class_name.startswith('Test'):
        class_name = class_name[4:]
    
    # Determine test class name
    test_class_name = f"Test{class_name}"
    
    # Build file path
    if folder_path:
        test_dir = TESTS_DIR / folder_path
        test_file = test_dir / f"test_{to_snake_case(class_name)}.py"
    else:
        test_dir = TESTS_DIR
        test_file = test_dir / f"test_{to_snake_case(class_name)}.py"
    
    if test_file.exists():
        print(f"❌ Test {test_name} already exists at {test_file}")
        return False
    
    # Create directory if needed
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Select template based on type
    if test_type == "controller":
        # Extract controller name
        controller_name = class_name.replace('Controller', '').replace('controller', '')
        if not controller_name:
            controller_name = class_name
        
        controller_snake = to_snake_case(controller_name)
        if folder_path:
            controller_import_path = f"{folder_path.replace('/', '.')}.{controller_snake}"
        else:
            controller_import_path = controller_snake
        
        content = TEST_CONTROLLER_TEMPLATE.substitute(
            ControllerName=class_name if class_name.endswith('Controller') else f"{class_name}Controller",
            controller_snake=controller_import_path
        )
    elif test_type == "router":
        router_name = class_name.replace('Router', '').replace('router', '')
        if not router_name:
            router_name = class_name
        
        content = TEST_ROUTER_TEMPLATE.substitute(
            RouterName=router_name
        )
    else:  # generic
        content = TEST_GENERIC_TEMPLATE.substitute(
            TestName=class_name
        )
    
    # Write file
    test_file.write_text(content)
    print(f"✅ Created test: {test_file}")
    
    return True

def generate_app_key():
    """Generate a secure random app key and update .env file"""
    # Generate a 64-character URL-safe random string
    app_key = secrets.token_urlsafe(48)  # 48 bytes = 64 characters when base64 encoded
    
    # Read existing .env file if it exists
    env_content = ""
    if ENV_FILE.exists():
        env_content = ENV_FILE.read_text()
    
    # Check if APP_KEY already exists
    app_key_pattern = re.compile(r'^APP_KEY=.*$', re.MULTILINE)
    
    if app_key_pattern.search(env_content):
        # Update existing APP_KEY
        env_content = app_key_pattern.sub(f'APP_KEY={app_key}', env_content)
        action = "updated"
    else:
        # Add new APP_KEY
        if env_content and not env_content.endswith('\n'):
            env_content += '\n'
        env_content += f'APP_KEY={app_key}\n'
        action = "added"
    
    # Write back to .env file
    ENV_FILE.write_text(env_content)
    
    print("=" * 60)
    print("🔑 Generated App Key")
    print("=" * 60)
    print(f"\n{app_key}\n")
    print("=" * 60)
    print(f"✅ {action.capitalize()} APP_KEY in .env file")
    print("=" * 60)
    
    return app_key

def main():
    parser = argparse.ArgumentParser(
        description="Simple generator for models, controllers, requests, and tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a model skeleton
  python3 generate.py model Product
  python3 generate.py model Auth/User  # Creates app/models/auth/user.py

  # Generate a controller skeleton
  python3 generate.py controller ProductController
  python3 generate.py controller Auth/AuthController  # Creates app/controllers/auth/auth_controller.py

  # Generate a request schema
  python3 generate.py request RegisterRequest --fields name:str email:email password:str
  python3 generate.py request Auth/RegisterRequest  # Creates app/requests/auth/register_request.py

  # Generate a test skeleton
  python3 generate.py test AuthController --type controller
  python3 generate.py test AuthRouter --type router
  python3 generate.py test UserService --type generic
  python3 generate.py test Auth/AuthController  # Creates tests/auth/test_auth_controller.py

  # Generate a secure app key
  python3 generate.py key
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Model generator
    model_parser = subparsers.add_parser('model', help='Generate a model skeleton')
    model_parser.add_argument('name', help='Model name (PascalCase)')
    
    # Controller generator
    controller_parser = subparsers.add_parser('controller', help='Generate a controller skeleton')
    controller_parser.add_argument('name', help='Controller name')
    
    # Request generator
    request_parser = subparsers.add_parser('request', help='Generate a request schema')
    request_parser.add_argument('name', help='Request name (PascalCase)')
    request_parser.add_argument('--fields', nargs='*', required=False, default=[],
                               help='Fields in format: field_name:type or field_name:type:optional (optional)')
    
    # Test generator
    test_parser = subparsers.add_parser('test', help='Generate a test skeleton')
    test_parser.add_argument('name', help='Test name (PascalCase, Test prefix optional)')
    test_parser.add_argument('--type', choices=['controller', 'router', 'generic'], 
                            default='generic',
                            help='Type of test to generate (default: generic)')
    
    # App key generator
    key_parser = subparsers.add_parser('key', help='Generate a secure app key')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Ensure directories exist
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    CONTROLLERS_DIR.mkdir(parents=True, exist_ok=True)
    REQUESTS_DIR.mkdir(parents=True, exist_ok=True)
    TESTS_DIR.mkdir(parents=True, exist_ok=True)
    
    if args.command == 'model':
        generate_model(args.name)
    elif args.command == 'controller':
        generate_controller(args.name)
    elif args.command == 'request':
        generate_request(args.name, args.fields)
    elif args.command == 'test':
        generate_test(args.name, args.type)
    elif args.command == 'key':
        generate_app_key()

if __name__ == '__main__':
    main()
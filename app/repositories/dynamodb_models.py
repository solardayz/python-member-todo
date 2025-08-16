from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from datetime import datetime
import os

from dotenv import load_dotenv
import sys

print("Starting dynamodb_models.py script...") # Added for debugging

# Add project root to sys.path to allow importing config
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)

from config import config # Assuming this import works now

print("Config module imported.", flush=True)

# Load environment variables from .env file if not already loaded
load_dotenv() # Ensure .env is loaded if not already

# Get the current configuration based on FLASK_ENV
config_name = os.getenv('FLASK_ENV', 'default')
current_config = config[config_name]

# Ensure AWS credentials and region are set in environment or .env
if not (current_config.AWS_ACCESS_KEY_ID and             current_config.AWS_SECRET_ACCESS_KEY and             current_config.AWS_REGION):
        print("Error: AWS credentials and region must be set in .env file.", flush=True)
        exit(1)

class BaseModel(Model):
    class Meta:
        # Use the region and credentials from config.py
        region = current_config.AWS_REGION
        aws_access_key_id = current_config.AWS_ACCESS_KEY_ID
        aws_secret_access_key = current_config.AWS_SECRET_ACCESS_KEY
        read_capacity_units = 1
        write_capacity_units = 1

class UsernameIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'username_index'
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    username = UnicodeAttribute(hash_key=True)

class UserModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = current_config.DYNAMODB_USERS_TABLE_NAME

    id = UnicodeAttribute(hash_key=True)
    username = UnicodeAttribute(null=False)
    email = UnicodeAttribute(null=False)
    password_hash = UnicodeAttribute(null=False) # Store hashed password
    created_at = UTCDateTimeAttribute(default=datetime.now)
    updated_at = UTCDateTimeAttribute(default=datetime.now)

    username_index = UsernameIndex()

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        super(UserModel, self).save(*args, **kwargs)

class TodoUserIdIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'user_id_index'
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    user_id = UnicodeAttribute(hash_key=True)
    created_at = UTCDateTimeAttribute(range_key=True)

class TodoModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = current_config.DYNAMODB_TODOS_TABLE_NAME

    id = UnicodeAttribute(hash_key=True)
    user_id = UnicodeAttribute(null=False)
    description = UnicodeAttribute(null=False)
    status = UnicodeAttribute(null=False)
    created_at = UTCDateTimeAttribute(default=datetime.now)
    updated_at = UTCDateTimeAttribute(default=datetime.now)

    user_id_index = TodoUserIdIndex()

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        super(TodoModel, self).save(*args, **kwargs)

# Optional: Create tables if they don't exist (for development/testing)
# In production, tables should be created via IaC (e.g., CloudFormation, Terraform)
if __name__ == '__main__':
    from pynamodb.exceptions import TableError

    # Ensure environment variables are loaded for config
    load_dotenv() # Ensure .env is loaded if not already

    # Get the current configuration based on FLASK_ENV
    config_name = os.getenv('FLASK_ENV', 'default')
    current_config = config[config_name]

    # Ensure AWS credentials and region are set in environment or .env
    if not (current_config.AWS_ACCESS_KEY_ID and 
            current_config.AWS_SECRET_ACCESS_KEY and 
            current_config.AWS_REGION):
        print("Error: AWS credentials and region must be set in .env file.", flush=True)
        exit(1)

    # Set the connection details for PynamoDB models directly
    # This ensures the models use the correct credentials and region when run standalone
    UserModel.Meta.region = current_config.AWS_REGION
    UserModel.Meta.aws_access_key_id = current_config.AWS_ACCESS_KEY_ID
    UserModel.Meta.aws_secret_access_key = current_config.AWS_SECRET_ACCESS_KEY
    UserModel.Meta.table_name = current_config.DYNAMODB_USERS_TABLE_NAME

    TodoModel.Meta.region = current_config.AWS_REGION
    TodoModel.Meta.aws_access_key_id = current_config.AWS_ACCESS_KEY_ID
    TodoModel.Meta.aws_secret_access_key = current_config.AWS_SECRET_ACCESS_KEY
    TodoModel.Meta.table_name = current_config.DYNAMODB_TODOS_TABLE_NAME

    print(f"Attempting to create tables in region: {current_config.AWS_REGION}", flush=True)

    try:
        print(f"Checking if table {UserModel.Meta.table_name} exists...", flush=True)
        if not UserModel.exists():
            print(f"Creating table: {UserModel.Meta.table_name}...", flush=True)
            UserModel.create_table(wait=True)
            print(f"Table {UserModel.Meta.table_name} created.", flush=True)
        else:
            print(f"Table {UserModel.Meta.table_name} already exists.", flush=True)
    except TableError as e:
        print(f"Error creating table {UserModel.Meta.table_name}: {e}", flush=True)
        exit(1)

    try:
        if not TodoModel.exists():
            print(f"Creating table: {TodoModel.Meta.table_name}...", flush=True)
            TodoModel.create_table(wait=True)
            print(f"Table {TodoModel.Meta.table_name} created.", flush=True)
        else:
            print(f"Table {TodoModel.Meta.table_name} already exists.", flush=True)
    except TableError as e:
        print(f"Error creating table {TodoModel.Meta.table_name}: {e}", flush=True)
        exit(1)

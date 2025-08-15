from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager

from app.controllers.auth_controller import auth_ns
from app.controllers.user_controller import users_ns
from app.controllers.todo_controller import todos_ns

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this in production!

authorizations = {
    'apiKey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Type in the 'Bearer <JWT_TOKEN>' value"
    }
}

api = Api(app, version='1.0', title='User and Todo Management API',
          description='A simple API for user and todo management with JWT authentication',
          doc='/swagger-ui',
          security='apiKey',
          authorizations=authorizations)

jwt = JWTManager(app)

# Register Namespaces
api.add_namespace(auth_ns)
api.add_namespace(users_ns)
api.add_namespace(todos_ns)

if __name__ == '__main__':
    app.run(debug=True)
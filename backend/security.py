from flask_jwt_extended import JWTManager
from models.models import User

jwt = JWTManager()

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.email  

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(email=identity).first()
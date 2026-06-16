class Config:
    DEBUG = True
    SECRET_KEY = 'dev-secret-key-change-in-prod'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///placement_portal.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'my-secret-key'
    
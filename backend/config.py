from datetime import timedelta

class Config:
    DEBUG = True
    SECRET_KEY = 'dev-secret-key-change-in-prod'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///placement_portal.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'my-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_URL = 'redis://localhost:6379/1'
    CACHE_DEFAULT_TIMEOUT = 300
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = '24f2001460@ds.study.iitm.ac.in'
    MAIL_PASSWORD = 'rczp kleo opem euoe'
    MAIL_DEFAULT_SENDER = '24f2001460@ds.study.iitm.ac.in'
    GCHAT_WEBHOOK_URL = 'http://localhost:5000/api/gchat/mock_webhook'

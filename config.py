import os

# store the configuration variables in a class


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'sqlite:///learning.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

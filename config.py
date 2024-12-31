import os

# store the configuration variables in a class


class Config:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'b5a4352ba3d82ce4d45089daa104c4ff'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'sqlite:///learning.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

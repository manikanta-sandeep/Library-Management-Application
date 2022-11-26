import os
current_dir=os.path.abspath(os.path.dirname(__file__))

class Config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevelopmentConfig(Config):
    SQLITE_DB_DIR = os.path.join(current_dir,"../db_directory")
    SQLALCHEMY_DATABASE_URI = "sqlite:///"+os.path.join(SQLITE_DB_DIR,"test.sqlite3")
    DEBUG = True
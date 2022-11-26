from flask import Flask
from application import config
from application.config import LocalDevelopmentConfig
from application.database import db

app=None
def create_app():
    app=Flask(__name__,template_folder="templates")
    print("Starting Manikanta's Local Development")
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    app.app_context().push()
    app.secret_key="BAD_SECRET_KEY"
    return app

app=create_app()

from application.controllers import *

if __name__=='__main__':
    app.run(host='0.0.0.0',port=8025)
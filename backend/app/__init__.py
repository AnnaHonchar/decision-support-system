from flask import Flask
from flask_cors import CORS
from .db import db
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    
    db.init_app(app)

    from .routes import api
    app.register_blueprint(api, url_prefix="/api")

    return app
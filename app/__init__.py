from flask import Flask
from flask_cors import CORS
import os


def create_app(config_name: str) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config['JSON_AS_ASCII'] = False
    
    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY

    CORS(app,
                  resources={
                      r"*": {"origins": "http://localhost:3000"}},
                  expose_headers=["Content-Type", "X-CSRFToken"],
                  supports_credentials=True)
    with app.app_context():
        from app.audio import audio_app
        app.register_blueprint(audio_app, url_prefix='/audio')
    return app

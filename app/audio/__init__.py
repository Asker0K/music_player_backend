from flask import Blueprint

audio_app = Blueprint('audio_app', __name__)

from . import routes

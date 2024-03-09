from flask import Flask, Response, request, url_for, send_from_directory, send_file, render_template
import cv2
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from api.config import Config
from waitress import serve
import time, os
app = Flask(__name__, static_folder='static')
app.config.from_object(Config)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Replace with your secret key
jwt = JWTManager(app)
ROOT = os.path.dirname(__file__)
CORS(app)
from api.register_api import api

if __name__ == '__main__':
    app.register_blueprint(api)
    # serve(app, host="127.0.0.1", port=5000, threads=8)
    app.run(host="127.0.0.1", port=5000, threaded=True)
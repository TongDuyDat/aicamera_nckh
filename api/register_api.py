from flask import Blueprint
from api.live_stream import live
from api.download_record import records
from api.user_api import user_api
from api.camera_api import camera_api
api = Blueprint("api", __name__, url_prefix="/")

api.register_blueprint(live, url_prefix='/api')
api.register_blueprint(records, url_prefix='/api')
api.register_blueprint(user_api, url_prefix='/api')
api.register_blueprint(camera_api, url_prefix='/api')
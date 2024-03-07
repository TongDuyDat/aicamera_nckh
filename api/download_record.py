from io import BytesIO
import os
from flask import Blueprint, jsonify, request,Response, send_file, url_for
from api.config import Config
from  PIL import Image
from pathlib import Path
import pathlib
from database.record_db import Record
temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath
from subprocess import Popen, PIPE
records = Blueprint('records', __name__, url_prefix="/api")
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
save_root_path = os.path.join(root_path, Config.RECORD_PATH)
@records.route('/download_video/<filename>', methods=['GET'])
def download_video(filename):
    # Assuming your video files are stored in a folder named 'videos'
    # Adjust the folder path accordingly
    # Construct the full path to the video file
    video_path = os.path.join(save_root_path, filename)
    # Return the file as a response
    return send_file(video_path, as_attachment=True)

@records.route('/<username>/load_records', methods=['GET'])
def load_records(username):
    """
    Load records for a given username.

    Returns:
        200 - If records are loaded successfully.
        404 - If no records are found for the given username.
        500 - For any other exception that occurs during processing.
    """
    try:
        # Query records for the given username
        records = Record.objects(username=username)
        url = f"http://{Config.ip_address}:{Config.port}/" + "record/"
        # If no records found, return 404
        if not records:
            return jsonify({'error': 'No records found for the given username.'}), 404

        # Serialize records to JSON
        serialized_records = [{
            'url': url + url_for('api.records.download_video', filename=f"{Path(record.file_path).name}"),
            'created_at': record.created_at,
            'id_camera': record.id_camera
        } for record in records]

        # Return records
        return jsonify(serialized_records), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

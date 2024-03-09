from threading import Semaphore
import datetime
import os
import pathlib
import cv2
import time
import torch
from flask import Blueprint, Response, request, stream_with_context
from PIL import Image
from pathlib import Path
from threading import Thread, Lock
from api.config import Config
from database.camera_db import Camera
from database.record_db import Record
from yolov5.detect import detect_img
from yolov5.models.common import DetectMultiBackend
from yolov5.models.experimental import attempt_load
from yolov5.utils.torch_utils import select_device

live = Blueprint('live', __name__, url_prefix="/api")

# Thay đổi PosixPath thành WindowsPath tạm thời
temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath

# Load model
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
device = select_device(device)

# Định nghĩa đường dẫn cho việc lưu trữ video
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
save_root_path = os.path.join(root_path, 'record')
if not os.path.exists(save_root_path):
    os.makedirs(save_root_path)

# Khởi tạo lock cho phân luồng
thread_lock = Lock()
# Hàm thực hiện nhận dạng và streaming video
def detect(step=1, username="", camera_id=0, ai=True):
    # Đường dẫn của video hoặc camera
    model = attempt_load(Config.WEIGHTS, device=device)
    cap = Camera.get_camera_by_id(camera_id, username)
    camera_url = cap.rtsp_url
    if len(camera_url) < 4:
        camera_url = int(camera_url)
    print("INFO: camera_url: ", camera_url, end="\n\n\n\n\n\n")
    camera = cv2.VideoCapture(camera_url)
    count = 0
    if camera:  
        fps = camera.get(cv2.CAP_PROP_FPS)
        w = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    else:  
        fps, w, h = 30, im0.shape[1], im0.shape[0]
    save_record_path = os.path.join(save_root_path, datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    save_path = str(Path(save_record_path).with_suffix(".mp4"))  
    print(save_path)
    vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*"X264"), fps, (w, h))
    flag_create_new_record = True
    while True:
        success, frame = camera.read()
        if not success:
            break
        im0 = frame
        if count % step == 0:   
            im0, _, clss = detect_img(frame, model, True, True)
            if 0 not in clss and flag_create_new_record:
                save_record_path = os.path.join(save_root_path, datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
                save_path = str(Path(save_record_path).with_suffix(".mp4")) 
                vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
                Record.create_record(save_path, username, camera_id)
                print("save record in {savepath}")
                flag_create_new_record = False
            else:
                if 0 in clss:   
                    flag_create_new_record = True
            im0 = cv2.resize(im0, dsize=(frame.shape[1], frame.shape[0]) )
        if not ai:
            im0 = frame
        _, buffer = cv2.imencode('.jpg', im0)
        frame_data = buffer.tobytes()
        time.sleep(.01)
        count += 1
        vid_writer.write(im0)
        # cv2.imshow("view", im0)
        cv2.waitKey(1)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
number_thead = 0
# Route để stream video
semaphore = Semaphore(3)

@live.route('/live/<user_name>/<camera_id>')
def video_stream(user_name, camera_id):
    ai = request.args.get("ai")
    
    # Kiểm tra Semaphore trước khi tạo luồng mới
    with thread_lock:
        if semaphore.acquire(blocking=False):
            thread = Thread(
                daemon=True,
                target=detect,
                args=(1, user_name, camera_id, ai)
            )
            thread.start()
        else:
            print("Hàng đợi đầy. Không thể tạo thêm luồng.")

    return Response(stream_with_context(detect(1, user_name, camera_id, ai)), mimetype='multipart/x-mixed-replace; boundary=frame')

# Hàm để stream các frame đã được nhận dạng
def stream_frames(detect_func, username, camera_id, ai):
    with thread_lock:
        return Response(detect_func(1, username, camera_id, ai), mimetype='multipart/x-mixed-replace; boundary=frame') 


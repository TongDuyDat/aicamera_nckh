from mongoengine import Document, StringField, BooleanField, IntField

class Camera(Document):
    name = StringField(required=True)
    camera_type_id = StringField()
    username = StringField()
    password = StringField()
    rtsp_url = StringField()
    status = BooleanField(default=True)
    position_id = StringField()
    camera_width = IntField()
    camera_height = IntField()
    identification_time = IntField()
    port = StringField()
    ip_address = StringField()
    created_by = StringField()
    meta = {"collection": "CAMERA"}
    @staticmethod
    def create_camera(name, camera_type_id, username, password, rtsp_url,created_by, position_id='', camera_width='', camera_height='', identification_time='', port='', ip_address=''):
        try:
            camera = Camera(
                name=name,
                camera_type_id=camera_type_id,
                username=username,
                password=password,
                rtsp_url=rtsp_url,
                position_id=position_id,
                camera_width=camera_width,
                camera_height=camera_height,
                identification_time=identification_time,
                port=port,
                ip_address=ip_address,
                created_by = created_by
            )
            camera.save()
            return True
        except Exception as e:
            return False, str(e)

    @staticmethod
    def update_camera(camera_id, **kwargs):
        try:
            Camera.objects(id=camera_id).update_one(**kwargs)
            return True
        except Exception as e:
            return False, str(e)

    @staticmethod
    def delete_camera(camera_id):
        try:
            Camera.objects(id=camera_id).delete()
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def get_all_cameras(created_by):
        return Camera.objects(created_by = created_by)

    @staticmethod
    def get_camera_by_id(camera_id, created_by):
        return Camera.objects(id=camera_id, created_by = created_by).first()
    @staticmethod
    def is_camera_exists(id):
        return Camera.objects(id=id).first() is not None
    @staticmethod
    def to_json(cls):
        return {
            "name":cls.name,
            "camera_type_id":cls.camera_type_id,
            "username":cls.username,
            "password":cls.password,
            "rtsp_url":cls.rtsp_url,
            "position_id":cls.position_id,
            "camera_width":cls.camera_width,
            "camera_height":cls.camera_height,
            "identification_time":cls.identification_time,
            "port":cls.port,
            "ip_address":cls.ip_address,
            "created_by" : cls.created_by
        }
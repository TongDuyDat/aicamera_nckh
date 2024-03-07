from mongoengine import Document, BooleanField, StringField, DateTimeField, ReferenceField
from datetime import datetime
class Notification(Document):
    username = StringField(required=True)
    id_record = StringField()
    content = StringField()
    viewed = BooleanField(default=False)
    meta = {"collection": "NOTIFICATION"}
    def get_all_notifications():
        notifications = Notification.objects()
        if notifications:
            return notifications
        return False  
              
    def get_notification_by_id(notification_id):
        notification = Notification.objects(id=notification_id).first()
        if notification:
            return notification
        else:
            return False

    def create_notification(username, id_record, content):
        
        try:
            new_notification = Notification(
            username=username,
            id_record=id_record,
            content=content
        )
            new_notification.save()
            return True
        except:
            return True

    
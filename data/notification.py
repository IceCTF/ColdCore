from data.database import Notification
from exceptions import ValidationError

def get_notifications(team):
    return Notification.select().where(Notification.team == team)

def get_notification(team, id):
    try:
        return Notification.get(Notification.id == id and Notification.team == team)
    except Notification.DoesNotExist:
        raise ValidationError("Notification does not exist!")

def delete_notification(notification):
    notification.delete_instance()

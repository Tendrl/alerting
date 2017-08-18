from tendrl.commons import objects


class NotificationMedia(objects.BaseObject):
    def __init__(self, media=None, *args, **kwargs):
        super(NotificationMedia, self).__init__(*args, **kwargs)
        self.media = media
        self.value = 'alerting/notification_medium'

from tendrl.commons import objects


class NotificationConfig(objects.BaseObject):
    def __init__(self, config=None, *args, **kwargs):
        super(NotificationConfig, self).__init__(*args, **kwargs)
        self.config = config
        self.value = 'notification_settings'

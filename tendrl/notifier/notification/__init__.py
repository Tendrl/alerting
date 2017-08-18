from abc import abstractmethod
import etcd
import importlib
import os
import six
from tendrl.alerting.objects.notification_media import NotificationMedia
from tendrl.alerting.objects.notification_config import NotificationConfig
from tendrl.alerting.utils.util import list_modules_in_package_path
from tendrl.alerting.utils.central_store_util import read as etcd_read
from tendrl.commons.event import Event
from tendrl.commons.message import ExceptionMessage


class PluginMount(type):

    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.register_plugin(cls)

    def register_plugin(cls, plugin):
        instance = plugin()
        cls.plugins.append(instance)


@six.add_metaclass(PluginMount)
class NotificationPlugin(object):
    def __init__(self):
        super(NotificationPlugin, self).__init__()
        self.name = ''

    @abstractmethod
    def save_config_help(self):
        raise NotImplementedError()

    @abstractmethod
    def set_destinations(self):
        raise NotImplementedError()

    @abstractmethod
    def get_alert_destinations(self):
        raise NotImplementedError()

    @abstractmethod
    def format_message(self, alert):
        raise NotImplementedError()

    @abstractmethod
    def dispatch_notification(self, msg):
        raise NotImplementedError()


class NotificationPluginManager(object):
    def load_plugins(self):
        try:
            path = os.path.dirname(os.path.abspath(__file__)) + '/handlers'
            pkg = 'tendrl.alerting.notification.handlers'
            notif_handlers = list_modules_in_package_path(path, pkg)
            for name, handler_fqdn in notif_handlers:
                importlib.import_module(handler_fqdn)
        except (SyntaxError, ValueError, ImportError) as ex:
            Event(
                ExceptionMessage(
                    priority="debug",
                    publisher="alerting",
                    payload={
                        "message": 'Failed to load the time series db'
                        'plugins.',
                        "exception": ex
                    }
                )
            )
            raise ex

    def save_alertnotificationconfig(self):
        notification_config = {}
        for n_plugin in NS.notification_medium:
            for alert_type in NS.alert_types:
                conf_name = '%s_%s' % (n_plugin, alert_type)
                notification_config[conf_name] = "true"
        NotificationConfig(config=notification_config).save()

    def __init__(self):
        super(NotificationPluginManager, self).__init__()
        try:
            self.load_plugins()
            notification_medium = []
            for plugin in NotificationPlugin.plugins:
                notification_medium.append(plugin.name)
            NS.notification_medium = notification_medium
            NotificationMedia(
                media=notification_medium
            ).save()
            self.save_alertnotificationconfig()
        except (
            AttributeError,
            SyntaxError,
            ValueError,
            KeyError,
            ImportError,
            etcd.EtcdException
        ) as ex:
            Event(
                ExceptionMessage(
                    priority="debug",
                    publisher="alerting",
                    payload={
                        "message": 'Failed to intialize notification '
                        'manager',
                        "exception": ex
                    }
                )
            )
            raise ex

    def notify_alert(self, alert):
        # TODO: Revert to object#load method of loading objects once loading of
        # nested dicts in objects is fixed in commons.
        NS.notification_subscriptions = etcd_read(
            '/notification_settings/config'
        )
        if alert is not None:
            for plugin in NotificationPlugin.plugins:
                plugin.dispatch_notification(alert)

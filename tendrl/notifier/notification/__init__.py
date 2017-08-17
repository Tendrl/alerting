from abc import abstractmethod
import etcd
import gevent.event
import importlib
import os
import six

from tendrl.commons.event import Event
from tendrl.commons.message import ExceptionMessage
from tendrl.notifier.objects.notification_media import NotificationMedia
from tendrl.notifier.utils.central_store_util import get_alerts
from tendrl.notifier.utils.central_store_util import update_alert_delivery
from tendrl.notifier.utils.util import list_modules_in_package_path


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


class NotificationPluginManager(gevent.greenlet.Greenlet):
    def load_plugins(self):
        try:
            path = os.path.dirname(os.path.abspath(__file__)) + '/handlers'
            pkg = 'tendrl.notifier.notification.handlers'
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

    def __init__(self):
        super(NotificationPluginManager, self).__init__()
        try:
            self.load_plugins()
            notification_medium = []
            self.complete = gevent.event.Event()
            for plugin in NotificationPlugin.plugins:
                notification_medium.append(plugin.name)
            NotificationMedia(
                media=notification_medium
            ).save()
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

    def _run(self):
        while not self.complete.is_set():
            try:
                alerts = get_alerts()
                gevent.sleep(30)
                for alert in alerts:
                    if not eval(alert.delivery):
                        for plugin in NotificationPlugin.plugins:
                            plugin.dispatch_notification(alert)
                        update_alert_delivery(alert)
            except(
                ValueError,
                KeyError,
                etcd.EtcdException
            )as ex:
                Event(
                    ExceptionMessage(
                        priority="debug",
                        publisher="alerting",
                        payload={
                            "message": "Exception caught in notification "
                            "dispatch"
                            " handlers.",
                            "exception": ex
                        }
                    )
                )

    def stop(self):
        self.complete.set()

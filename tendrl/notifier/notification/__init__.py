from abc import abstractmethod
import importlib
import json
import os
import six
import threading
import time

import etcd

from tendrl.commons.event import Event
from tendrl.commons.message import ExceptionMessage
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


class NotificationPluginManager(threading.Thread):
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
                    publisher="notifier",
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
        self.daemon = True
        try:
            self.load_plugins()
            notification_medium = []
            self.complete = threading.Event()
            for plugin in NotificationPlugin.plugins:
                notification_medium.append(plugin.name)
            NS.notifier.objects.NotificationMedia(
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
                    publisher="notifier",
                    payload={
                        "message": 'Failed to intialize notification '
                        'manager',
                        "exception": ex
                    }
                )
            )
            raise ex

    def run(self):
        _sleep = 0
        while not self.complete.is_set():
            if _sleep > 5:
                _sleep = int(
                    NS.config.data["notification_check_interval"]
                )
            else:
                _sleep += 1

            try:
                lock = None
                alerts = get_alerts()
                for alert in alerts:
                    alert.tags = json.loads(alert.tags)
                    if str(alert.delivered).lower() == "false":
                        lock = etcd.Lock(
                            NS._int.wclient,
                            'alerting/alerts/%s' % alert.alert_id
                        )
                        lock.acquire(
                            blocking=True,
                            lock_ttl=60
                        )
                        if lock.is_acquired:
                            # renew a lock
                            lock.acquire(lock_ttl=60)
                            for plugin in NotificationPlugin.plugins:
                                plugin.dispatch_notification(alert)
                            update_alert_delivery(alert)
                            lock.release()
            except(
                AttributeError,
                SyntaxError,
                ValueError,
                KeyError,
                etcd.EtcdException
            )as ex:
                Event(
                    ExceptionMessage(
                        priority="debug",
                        publisher="notifier",
                        payload={
                            "message": "Exception caught in notification "
                            "dispatch"
                            " handlers.",
                            "exception": ex
                        }
                    )
                )
            finally:
                if isinstance(lock, etcd.lock.Lock) and lock.is_acquired:
                    lock.release()

            time.sleep(_sleep)

    def stop(self):
        self.complete.set()

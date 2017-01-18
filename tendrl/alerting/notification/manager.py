from abc import abstractmethod
import etcd
import importlib
import inspect
import logging
import multiprocessing
import os
import six
from tendrl.alerting.exceptions import AlertingError
from tendrl.alerting.exceptions import InvalidRequest
from tendrl.alerting.notification.exceptions import InvalidHandlerConfig
from tendrl.alerting.notification.exceptions import NotificationDispatchError
from tendrl.alerting.notification.exceptions import NotificationPluginError

LOG = logging.getLogger(__name__)


etcd_server = None


class PluginMount(type):

    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.register_plugin(cls)

    def register_plugin(cls, plugin):
        global etcd_server
        instance = plugin(etcd_server)
        cls.plugins.append(instance)


@six.add_metaclass(PluginMount)
class NotificationPlugin(multiprocessing.Process):
    def __init__(self):
        super(NotificationPlugin, self).__init__()
        self.alerts_queue = multiprocessing.Queue()
        self.name = ''

    @abstractmethod
    def get_config_help(self):
        raise NotImplementedError()

    @abstractmethod
    def validate_config(self, config):
        raise NotImplementedError()

    @abstractmethod
    def add_destination(self, config):
        raise NotImplementedError()

    @abstractmethod
    def set_destinations(self, alert):
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

    def start(self, alerts_queue):
        try:
            self.alerts_queue = alerts_queue
            while not self.complete.is_set():
                alert = self.alerts_queue.get()
                if alert is not None:
                    self.dispatch_notification(alert)
        except NotificationDispatchError as ex:
            LOG.error(
                'Failed to dispatch alert %s via %s. Error %s'
                % (str(alert), self.name, str(ex)),
                exc_info=True)

    def stop(self):
        self.complete.set()


class NotificationPluginManager(object):
    def load_plugins(self):
        try:
            path = os.path.dirname(os.path.abspath(__file__)) + '/handlers'
            pkg = 'tendrl.alerting.notification.handlers'
            for py in [f[:-3] for f in os.listdir(path)
                       if f.endswith('.py') and f != '__init__.py']:
                plugin_name = '.'.join([pkg, py])
                mod = importlib.import_module(plugin_name)
                clsmembers = inspect.getmembers(mod, inspect.isclass)
                for name, cls in clsmembers:
                    exec("from %s import %s" % (plugin_name, name))
        except (SyntaxError, ValueError, ImportError) as ex:
            LOG.error('Failed to load the time series db plugins. Error %s' %
                      ex, exc_info=True)
            raise NotificationPluginError(str(ex))

    def __init__(self, etcdServer):
        try:
            global etcd_server
            etcd_server = etcdServer
            self.load_plugins()
            notification_medium = []
            for plugin in NotificationPlugin.plugins:
                notification_medium.append(plugin.name)
            etcd_server.client.write(
                '/alerting/notification_medium/supported',
                notification_medium
            )
        except (
            SyntaxError,
            ValueError,
            KeyError,
            etcd.EtcdKeyNotFound,
            etcd.EtcdConnectionFailed,
            etcd.EtcdException,
            NotificationPluginError
        ) as ex:
            LOG.error(
                'Failed to intialize notification manager.Error %s' % str(ex),
                exc_info=True
            )
            raise AlertingError(str(ex))

    def start(self, alert_queue):
        try:
            self.alert_queue = alert_queue
            for plugin in NotificationPlugin.plugins:
                plugin.start(self.alert_queue)
        except NotificationDispatchError as ex:
            raise ex

    def stop(self):
        for plugin in NotificationPlugin.plugins:
            plugin.stop()

    def get_handlers(self):
        try:
            global etcd_server
            return etcd_server.client.read(
                '/alerting/notification_medium/supported'
            ).value
        except (
            etcd.EtcdKeyNotFound,
            etcd.EtcdConnectionFailed,
            etcd.EtcdException
        ) as ex:
            LOG.error(
                'Fetching supported notification medium list failed.Error %s'
                % ex,
                exc_info=True
            )
            raise AlertingError(str(ex))

    def get_config_help(self, name):
        for plugin in NotificationPlugin.plugins:
            if plugin.name.lower() == ("%s" % name).lower():
                return plugin.get_config_help()
        raise InvalidRequest(
            'Invalid name passed as request arguement'
        )

    def add_destination(self, plugin_name, config):
        try:
            for plugin in NotificationPlugin.plugins:
                if plugin.name.lower() == ("%s" % plugin_name).lower():
                    plugin.add_destination(config)
            return str(True)
        except InvalidHandlerConfig as ex:
            LOG.error(
                'Saving %s destination config %s to etcd failed. Error %s'
                % (plugin_name, str(config), str(ex)),
                exc_info=True
            )
            raise ex

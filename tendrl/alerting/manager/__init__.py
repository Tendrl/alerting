import etcd
import gevent
from gevent.queue import Queue
import signal
from tendrl.alerting.notification import NotificationPluginManager
from tendrl.alerting.sync import TendrlAlertingSync
from tendrl.alerting.watcher import AlertsWatchManager
from tendrl.alerting.handlers import AlertHandlerManager
from tendrl.alerting import AlertingNS
from tendrl.commons.event import Event
from tendrl.commons.message import ExceptionMessage
from tendrl.commons.message import Message
from tendrl.commons import TendrlNS


class TendrlAlertingManager(object):
    def __init__(self):
        try:
            NS.alert_queue = Queue()
            NS.alert_types = []
            NS.notification_medium = []
            self.alert_handler_manager = AlertHandlerManager()
            NS.notification_plugin_manager = NotificationPluginManager()
            self.watch_manager = AlertsWatchManager()
            self.sync_thread = TendrlAlertingSync()
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
                        "message": 'Error intializing alerting manager',
                        "exception": ex
                    }
                )
            )
            raise ex

    def start(self):
        self.alert_handler_manager.start()
        self.sync_thread.start()
        self.watch_manager.start()

    def stop(self):
        self.watch_manager.stop()
        self.sync_thread.stop()


def main():
    AlertingNS()
    TendrlNS()
    NS.alerting.definitions.save()
    NS.alerting.config.save()
    NS.publisher_id = "alerting"
    
    if NS.config.data.get("with_internal_profiling", False):
        from tendrl.commons import profiler
        profiler.start()
        
    tendrl_alerting_manager = TendrlAlertingManager()
    tendrl_alerting_manager.start()

    complete = gevent.event.Event()

    def terminate(sig, frame):
        Event(
            Message(
                "debug",
                "alerting",
                {
                    "message": 'Signal handler: stopping',
                }
            )
        )
        tendrl_alerting_manager.stop()
        complete.set()

    gevent.signal(signal.SIGINT, terminate)
    gevent.signal(signal.SIGTERM, terminate)

    while not complete.is_set():
        complete.wait(timeout=1)


if __name__ == "__main__":
    main()

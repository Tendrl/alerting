import etcd
import gevent
import signal

from gevent.queue import Queue
from tendrl.commons.event import Event
from tendrl.commons.message import ExceptionMessage
from tendrl.commons import TendrlNS
from tendrl.commons.utils.log_utils import log
from tendrl.notifier.notification import NotificationPluginManager
from tendrl.notifier import NotifierNS


class TendrlNotifierManager(object):
    def __init__(self):
        try:
            NS.notification_queue = Queue()
            self.notification_plugin_manager = NotificationPluginManager()
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
                        "message": 'Error intializing notification manager',
                        "exception": ex
                    }
                )
            )
            raise ex

    def start(self):
        self.notification_plugin_manager.start()

    def stop(self):
        self.notification_plugin_manager.stop()


def main():
    NotifierNS()
    TendrlNS()
    NS.notifier.definitions.save()
    NS.notifier.config.save()
    NS.publisher_id = "notifier"

    if NS.config.data.get("with_internal_profiling", False):
        from tendrl.commons import profiler
        profiler.start()
    tendrl_notifier_manager = TendrlNotifierManager()
    tendrl_notifier_manager.start()
    complete = gevent.event.Event()

    def terminate():
        log(
            "debug",
            "notifier",
            {
                "message": 'Signal handler: stopping',
            }
        )
        tendrl_notifier_manager.stop()
        complete.set()

    gevent.signal(signal.SIGINT, terminate)
    gevent.signal(signal.SIGTERM, terminate)

    while not complete.is_set():
        complete.wait(timeout=1)


if __name__ == "__main__":
    main()

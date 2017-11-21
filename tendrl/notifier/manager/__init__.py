import signal
import threading

import etcd

from tendrl.commons.event import Event
from tendrl.commons.message import ExceptionMessage
from tendrl.commons import TendrlNS
from tendrl.commons.utils.log_utils import log
from tendrl.notifier.notification import NotificationPluginManager
from tendrl.notifier import NotifierNS


class TendrlNotifierManager(object):
    def __init__(self):
        try:
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
                    publisher="notifier",
                    payload={
                        "message": 'Error intializing notification manager',
                        "exception": ex
                    }
                )
            )
            raise ex

    def start(self):
        self.notification_plugin_manager.start()
        self.notification_plugin_manager.join()

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
    complete = threading.Event()

    def terminate(signum, frame):
        log(
            "debug",
            "notifier",
            {
                "message": 'Signal handler: stopping',
            }
        )
        tendrl_notifier_manager.stop()
        complete.set()

    def reload_config(signum, frame):
        NS.config = NS.config.__class__()
        NS.config.save()

   
    signal.signal(signal.SIGINT, terminate)
    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGHUP, reload_config)


    while not complete.is_set():
        complete.wait(timeout=1)


if __name__ == "__main__":
    main()

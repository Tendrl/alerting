from etcd import EtcdKeyNotFound
from etcd import EtcdException
import gevent
import tendrl.alerting.utils.central_store_util as central_store_util
from tendrl.commons.event import Event
from tendrl.commons.message import ExceptionMessage


class AlertsWatchManager(gevent.greenlet.Greenlet):
    def __init__(self):
        super(AlertsWatchManager, self).__init__()
        self.complete = gevent.event.Event()
        self.handled_msgs = []

    def _run(self):
        while not self.complete.is_set():
            gevent.sleep(30)
            try:
                event_ids = central_store_util.get_event_ids()
                for event_id in event_ids:
                    if event_id not in self.handled_msgs:
                        self.handled_msgs.append(event_id)
                        NS.alert_queue.put(event_id)
            except EtcdKeyNotFound:
                continue
            except (EtcdException, AttributeError) as ex:
                Event(
                    ExceptionMessage(
                        priority="debug",
                        publisher="alerting",
                        payload={
                            "message": 'Exception in alert watcher',
                            "exception": ex
                        }
                    )
                )

    def stop(self):
        self.complete.set()

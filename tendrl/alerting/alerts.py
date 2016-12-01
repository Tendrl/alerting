from tendrl.common.etcdobj.etcdobj import Server as etcd_server
import multiprocessing
import ast
import tendrl.alerting.constants as consts
from tendrl.common.config import ConfigNotFound
import logging
from tendrl.common.config import TendrlConfig
from ConfigParser import NoOptionError


config = TendrlConfig()
LOG = logging.getLogger(__name__)


class AlertsManager(multiprocessing.Process):
    def __init__(self, alerts_queue):
        super(AlertsManager, self).__init__()
        multiprocessing.Process.__init__(self)
        self.alerts_queue = alerts_queue
        try:
            etcd_kwargs = {
                'port': int(config.get("common", "etcd_port")),
                'host': config.get("common", "etcd_connection")
            }
            self.etcd_server = etcd_server(etcd_kwargs=etcd_kwargs)
        except (ConfigNotFound, NoOptionError) as ex:
            raise ex

    def WatchAlerts(self):
        try:
            while True:
                changes = self.etcd_server.client.watch(
                    consts.ALERTS_DIRECTORY, recursive=True, timeout=0)
                if changes is not None and changes.value is not None:
                    LOG.debug('The alert is' +
                              str(changes.value), exc_info=True)
                    self.alerts_queue.put(ast.literal_eval(changes.value))
        except (KeyValue, Exception) as e:
            LOG.error('Exception %s caught while watching alerts'.format(
                str(e)), exc_info=True)

    def run(self):
        self.WatchAlerts()

    def stop(self):
        self.terminate()

import logging
import multiprocessing
import signal
from tendrl.alerting.api.manager import APIManager
from tendrl.alerting.exceptions import AlertingError
from tendrl.alerting.notification.exceptions import NotificationDispatchError
from tendrl.alerting.notification.manager import NotificationPluginManager
from tendrl.alerting.persistence.persister import AlertingEtcdPersister
from tendrl.alerting.watcher.manager import AlertsWatchManager
from tendrl.commons.config import ConfigNotFound
from tendrl.commons.config import TendrlConfig
from tendrl.commons import log


LOG = logging.getLogger(__name__)
config = TendrlConfig('alerting', '/etc/tendrl/tendrl.conf')


class AlertingManager(object):
    def __init__(self):
        try:
            api_server_addr = config.get(
                "alerting",
                "api_server_addr"
            )
            api_server_port = config.get(
                "alerting",
                "api_server_port"
            )
            persister = AlertingEtcdPersister(config)
            self.alert_queue = multiprocessing.Queue()
            storage_server = persister.get_store()
            self.n_plugin_manager = NotificationPluginManager(storage_server)
            self.api_manager = APIManager(
                api_server_addr,
                api_server_port,
                self.n_plugin_manager,
                persister
            )
            persister.write_configs(
                config.get(
                    "alerting",
                    "api_server_addr"
                ),
                config.get(
                    "alerting",
                    "api_server_port"
                )
            )
            persister.update_defs()
            self.watch_manager = AlertsWatchManager(
                self.alert_queue,
                AlertingEtcdPersister(config).get_store().client
            )
        except (AlertingError, ConfigNotFound) as ex:
            raise ex

    def start(self):
        try:
            self.api_manager.start()
            self.watch_manager.start()
            self.n_plugin_manager.start(self.alert_queue)
        except (
            AlertingError,
            NotificationDispatchError,
            Exception
        ) as ex:
            LOG.error(
                'Exception %s' % str(ex),
                exc_info=True
            )
            raise ex

    def stop(self):
        try:
            self.alert_queue.close()
            self.api_manager.terminate()
            self.n_plugin_manager.stop()
            self.watch_manager.terminate()
        except Exception as ex:
            LOG.error(
                'Exception %s' % str(ex),
                exc_info=True
            )
            raise ex


def main():
    log.setup_logging(
        config.get('alerting', 'log_cfg_path'),
        config.get('alerting', 'log_level')
    )
    manager = AlertingManager()

    def terminate(sig, frame):
        LOG.error("Signal handler: stopping", exc_info=True)
        manager.stop()

    signal.signal(signal.SIGINT, terminate)
    manager.start()


if __name__ == "__main__":
    main()
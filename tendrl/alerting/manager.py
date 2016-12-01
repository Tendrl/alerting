from tendrl.alerting.alerts import AlertsManager
from tendrl.alerting.notification.alert_notification_manager \
    import AlertNotificationManager
from tendrl.common import log
from tendrl.common.config import TendrlConfig
import multiprocessing
import logging


config = TendrlConfig()
LOG = logging.getLogger(__name__)


class TendrlManager():
    def __init__(self):
        self.alerts_queue = multiprocessing.Queue()
        self.alerts_manager = AlertsManager(self.alerts_queue)
        self.notification_manager = AlertNotificationManager(self.alerts_queue)

    def stop(self):
        try:
            self.notification_manager.stop()
            self.alerts_manager.stop()
        except Exception as ex:
            LOG.error("Terminating workers %s" % ex, exc_info=True)
        finally:
            self.alerts_queue.close()

    def start(self):
        self.alerts_manager.start()
        self.notification_manager.start()


def main():
    try:
        log.setup_logging(
            config.get('tendrl_alerts', 'log_cfg_path'),
            config.get('tendrl_alerts', 'log_level')
        )
        manager = TendrlManager()
        manager.start()
    except KeyboardInterrupt:
        LOG.debug('Caught Keyboard Interrupt...')
        manager.stop()


if __name__ == "__main__":
    main()

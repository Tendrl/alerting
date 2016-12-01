import multiprocessing
from tendrl.alerting.notification.mail_handler import MailHandler
import logging
from tendrl.common.config import ConfigNotFound
from socket import error
from smtplib import SMTPException

LOG = logging.getLogger(__name__)


class AlertNotificationManager(multiprocessing.Process):
    def __init__(self, alerts):
        super(AlertNotificationManager, self).__init__()
        self._complete = multiprocessing.Event()
        self.alerts = alerts
        LOG.debug("Initialized alert notification manager", exc_info=True)

    def run(self):
        alert = {}
        LOG.debug("Started alert notification manager", exc_info=True)
        while not self._complete.is_set():
            alert = self.alerts.get()
            if alert is not None:
                try:
                    mail_handler = MailHandler(alert)
                    mail_handler.start()
                except (error, SMTPException, ConfigNotFound) as ex:
                    LOG.error('Mail handler creation failed.Error %s' %
                              ex, exc_info=True)

    def stop(self):
        self._complete.set()

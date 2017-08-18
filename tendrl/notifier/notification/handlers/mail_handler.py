import smtplib

from etcd import EtcdException
from etcd import EtcdKeyNotFound
from socket import error
from tendrl.commons.config import load_config
from tendrl.commons.event import Event
from tendrl.commons.message import ExceptionMessage
from tendrl.commons.utils.log_utils import log
from tendrl.notifier.notification import NotificationPlugin
from tendrl.notifier.utils import central_store_util

SSL_AUTHENTICATION = 'ssl'
TLS_AUTHENTICATION = 'tls'


class EmailHandler(NotificationPlugin):

    def get_config_help(self):
        config_help = {
            'email_id': {
                'detail': 'The email-id',
                'type': 'String'
            },
            'auth': {
                'detail': "'ssl' or 'tls' or '' if no auth required",
                'type': 'String'
            },
            'email_pass': {
                'detail': 'Password required if auth chosen',
                'type': 'String'
            },
            'email_smtp_port': {
                'detail': 'The smtp mail server port corresponding to mail id',
                'type': 'String'
            },
            'email_smtp_server': {
                'detail': 'The smtp mail server corresponding to the mail id',
                'type': 'String'
            },
            'is_admin': {
                'detail': 'True if this is admin config else False.'
                          'If this field is not True, only email_id suffices.',
                'type': 'Boolean'
            },
            'alert_subscriptions': {
                'detail': '* for all alerts.'
                          'Or list of required types of alerts'
                          'Not required for admin user(is_admin: True)',
                'type': "String(for '*') or List of alert types"
            },
            'clusters': {
                'detail': '* to receive all alerts or list of clusters'
                          'Not required for admin user(is_admin: True)',
                'type': "String(for '*') or List of integration_ids"
            }
        }
        return config_help

    def set_destinations(self):
        # TODO(gowtham):Get user ids from indexes who enabled
        # email notification
        pass

    def get_alert_destinations(self):
        # TODO(gowtham): get user emailds only who have enabled
        # email notfication
        user_configs = []
        try:
            users = central_store_util.read_key('/_tendrl/users')
            for user in users.leaves:
                user_key = user.key
                try:
                    user_email = central_store_util.read_key(
                        "%s/email" % user_key
                    ).value
                    user_configs.append(user_email)
                except EtcdKeyNotFound:
                    continue
            self.user_configs = user_configs
        except (
            EtcdException,
            ValueError,
            KeyError,
            SyntaxError
        ) as ex:
            raise ex

    def format_message(self, alert):
        return "Subject: [Alert] %s, %s threshold breached\n\n%s" % (
            alert.resource, alert.severity, alert.tags['message'])

    def __init__(self):
        self.name = 'email'
        self.admin_config = load_config(
            'notifier',
            '/etc/tendrl/notifier/email.conf.yaml'
        )
        if not self.admin_config.get('auth'):
            self.admin_config['auth'] = ''
        self.user_configs = []

    def get_mail_client(self):
        if (
            self.admin_config.get('auth') is not None and
            self.admin_config['auth'] == SSL_AUTHENTICATION
        ):
            try:
                server = smtplib.SMTP_SSL(
                    self.admin_config['email_smtp_server'],
                    int(self.admin_config['email_smtp_port'])
                )
                return server
            except (
                smtplib.socket.gaierror,
                smtplib.SMTPException
            ) as ex:
                Event(
                    ExceptionMessage(
                        priority="debug",
                        publisher="alerting",
                        payload={
                            "message": 'Failed to fetch client for smtp'
                            '  server %s and smtp port %s' % (
                                self.admin_config['email_smtp_server'],
                                str(self.admin_config['email_smtp_port']),
                            ),
                            "exception": ex
                        }
                    )
                )
                raise ex
        else:
            try:
                server = smtplib.SMTP(
                    self.admin_config['email_smtp_server'],
                    int(self.admin_config['email_smtp_port'])
                )
                if self.admin_config['auth'] != '':
                    server.starttls()
                return server
            except (smtplib.socket.gaierror, smtplib.SMTPException) as ex:
                Event(
                    ExceptionMessage(
                        priority="debug",
                        publisher="alerting",
                        payload={
                            "message": 'Failed to fetch client for smtp'
                            '  server %s and smtp port %s' % (
                                self.admin_config['email_smtp_server'],
                                str(self.admin_config['email_smtp_port']),
                            ),
                            "exception": ex
                        }
                    )
                )
                raise ex

    def dispatch_notification(self, alert):
        server = None
        try:
            self.set_destinations()
            # TODO(gowtham): Pass user_id collected from 
            # set_destinations
            # For now notifications sent to all users
            self.get_alert_destinations()
            if (
                not self.user_configs or
                len(self.user_configs) == 0
            ):
                log(
                    "error",
                    "alerting",
                    {
                        "message": 'No destinations configured to send'
                        'alert notification'
                    }
                )
        except (
            AttributeError,
            EtcdException,
            ValueError,
            KeyError,
            SyntaxError
        ) as ex:
            Event(
                ExceptionMessage(
                    priority="debug",
                    publisher="alerting",
                    payload={
                        "message": 'Exception caught attempting to set'
                        ' %s email destinations' % str(alert.tags),
                        "exception": ex
                    }
                )
            )
            return
        try:
            msg = self.format_message(alert)
            if not self.admin_config:
                log(
                    "debug",
                    "alerting",
                    {
                        "message": 'Detected alert %s.'
                        'But, admin config is a must to send'
                        ' notification' % msg
                    }
                )
                return
            server = self.get_mail_client()
            server.ehlo()
            if self.admin_config['auth'] != "":
                server.login(
                    self.admin_config['email_id'],
                    self.admin_config['email_pass']
                )
            server.sendmail(
                self.admin_config['email_id'],
                self.user_configs,
                msg
            )
            log(
                "debug",
                "alerting",
                {
                    "message": 'Sent mail to %s to alert about %s'
                    % (self.user_configs, msg)
                }
            )
        except (
            error,
            smtplib.SMTPException,
            smtplib.SMTPAuthenticationError,
            smtplib.socket.gaierror,
            smtplib.SMTPSenderRefused,
            Exception
        ) as ex:
            Event(
                ExceptionMessage(
                    priority="debug",
                    publisher="alerting",
                    payload={
                        "message": 'Exception caught attempting to email'
                        '%s' % msg,
                        "exception": ex
                    }
                )
            )
            raise ex
        finally:
            if server:
                server.close()

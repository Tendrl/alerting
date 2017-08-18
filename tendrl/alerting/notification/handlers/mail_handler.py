from etcd import EtcdException
from etcd import EtcdKeyNotFound
import smtplib
from socket import error
from tendrl.alerting.handlers import AlertHandler
from tendrl.alerting.notification import NotificationPlugin
import tendrl.alerting.utils.central_store_util as central_store_util
from tendrl.commons.config import load_config
from tendrl.commons.event import Event
from tendrl.commons.message import ExceptionMessage
from tendrl.commons.message import Message


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
        # TODO(anmolbabu):User configuration will not just be destination email
        # but it would also include user level subscriptions the capability
        # underneath needs to be enhanced for that.
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

    def get_alert_destinations(self, alert):
        for alert_handler in AlertHandler.handlers:
            if alert.resource == alert_handler.handles:
                #ideally iterate per user and formulate
                #the list of eligible users
                if NS.notification_subscriptions['%s_%s' % (
                    self.name,
                    alert_handler.representive_name
                )] == "true":
                    # Ideally it should be list of applicable users
                    # but untill we enhance global config to user config_help
                    # the behaviour is if notification enabled globally its
                    # enabled for all users
                    return self.user_configs
                else:
                    return None
        return None

    def __init__(self):
        self.name = 'email'
        self.admin_config = load_config(
            'alerting',
            '/etc/tendrl/alerting/email.conf.yaml'
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
                Event(
                    Message(
                        "debug",
                        "alerting",
                        {
                            "message": 'Detected alert %s.'
                            'But, admin config is a must to send'
                            ' notification' % msg
                        }
                    )
                )
                return
            server = self.get_mail_client()
            server.ehlo()
            if self.admin_config['auth'] != "":
                server.login(
                    self.admin_config['email_id'],
                    self.admin_config['email_pass']
                )
            alert_destinations = self.get_alert_destinations(alert)
            if (
                not alert_destinations or
                len(alert_destinations) == 0
            ):
                Event(
                    Message(
                        "error",
                        "alerting",
                        {
                            "message": 'No destinations configured to send'
                            ' %s alert notification' % msg
                        }
                    )
                )
                return
            server.sendmail(
                self.admin_config['email_id'],
                self.user_configs,
                msg
            )
            Event(
                Message(
                    "debug",
                    "alerting",
                    {
                        "message": 'Sent mail to %s to alert about %s'
                        % (self.user_configs, msg)
                    }
                )
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
        finally:
            if server:
                server.close()

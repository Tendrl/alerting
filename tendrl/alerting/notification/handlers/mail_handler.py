import ast
from etcd import EtcdConnectionFailed
from etcd import EtcdKeyNotFound
from etcd import EtcdNotDir
import logging
import multiprocessing
import smtplib
from socket import error
from tendrl.alerting.notification.exceptions import InvalidHandlerConfig
from tendrl.alerting.notification.exceptions import NotificationDispatchError
from tendrl.alerting.notification.manager import NotificationPlugin

LOG = logging.getLogger(__name__)
SSL_AUTHENTICATION = 'ssl'
TLS_AUTHENTICATION = 'tls'


class EmailHandler(NotificationPlugin):
    def get_config_help(self):
        return {
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
                'type': "String(for '*') or List of cluster-ids"
            }
        }

    def validate_config(self, config):
        if config.get('email_id') is None:
            raise InvalidHandlerConfig('Email-id is a mandatory field')
        if config.get('is_admin') is None:
            raise InvalidHandlerConfig('is_admin is a mandatory field')
        if config.get('auth') is not None:
            if (
                config['auth'] != SSL_AUTHENTICATION and
                config['auth'] != TLS_AUTHENTICATION
            ):
                raise InvalidHandlerConfig(
                    "The permitted values for 'auth' are 'ssl' or 'tls' or ''"
                )
        if config.get('auth') is None:
            config['auth'] = ""
        if not config['is_admin']:
            if config.get('alert_subscriptions') is None:
                raise InvalidHandlerConfig(
                    'alert_subscriptions is a mandatory field it could be * to'
                    'receive all alerts'
                )
            if config.get('clusters') is None:
                raise InvalidHandlerConfig(
                    "'clusters' is manddatory attribute for non admin users"
                    "The possible values could be '*' or list of cluster ids"
                )
        else:
            if config.get('email_smtp_server') is None:
                raise InvalidHandlerConfig(
                    'email_smtp_server is a mandatory field'
                )
            if config['auth'] is '':
                return True
            else:
                if 'email_pass' not in config:
                    raise InvalidHandlerConfig(
                        'email_pass is a mandatory field if auth is chosen'
                    )
        return True

    def add_destination(self, conf):
        config = ast.literal_eval(conf)
        try:
            if self.validate_config(config):
                self.etcd_server.client.write(
                    '/alerting/notification_medium/email/config/%s' % config[
                        'email_id'],
                    config
                )
        except (
            NotificationDispatchError,
            InvalidHandlerConfig,
            EtcdConnectionFailed,
            EtcdNotDir,
            KeyError,
            SyntaxError,
            ValueError
        ) as ex:
            LOG.error(
                'Failed to add email config %s. Error %s' % (conf, str(ex))
            )
            raise NotificationDispatchError(str(ex))

    def set_destinations(self, alert):
        admin_config = {}
        user_configs = []
        try:
            configs = self.etcd_server.client.read(
                '/alerting/notification_medium/email/config',
                recursive=True
            )
            for config in configs._children:
                mail_config = ast.literal_eval(config['value'])
                if mail_config['is_admin']:
                    if mail_config.get('auth') is None:
                        mail_config['auth'] = ""
                    admin_config = mail_config
                else:
                    if (
                        mail_config['alert_subscriptions'] == '*' or
                        alert.resource in mail_config['alert_subscriptions']
                    ):
                        user_configs.append(mail_config)
            self.admin_config = admin_config
            self.user_configs = user_configs
        except EtcdKeyNotFound as ex:
            raise NotificationDispatchError(str(ex))
        except (
            EtcdConnectionFailed,
            EtcdNotDir,
            ValueError,
            KeyError,
            SyntaxError
        ) as ex:
            raise NotificationDispatchError(str(ex))

    def format_message(self, alert):
        return "Subject: [Alert] %s, %s threshold breached\n\n%s" % (
            alert.resource, alert.severity, alert.to_json_string())

    def get_alert_destinations(self, alert):
        recipients = []
        for config in self.user_configs:
            # TODO(anmol) Ideally even check the cluster part.
            if config['alert_subscriptions'] == '*' or\
                    alert.resource in config['alert_subscriptions']:
                recipients.append(config['email_id'])
        return recipients

    def __init__(self, etcd_server):
        self.name = 'email'
        try:
            self.etcd_server = etcd_server
            self.admin_config = {}
            self.user_configs = []
            self.complete = multiprocessing.Event()
        except NotificationDispatchError as ex:
            raise NotificationDispatchError(str(ex))

    def get_mail_client(self):
        if not self.admin_config:
            raise NotificationDispatchError(
                "Admin mail configuration is required for dispatching email"
                " notification"
            )
        if (
            self.admin_config.get('auth') is not None and
            self.admin_config['auth'] == SSL_AUTHENTICATION
        ):
            try:
                server = smtplib.SMTP_SSL(
                    self.admin_config['email_smtp_server'],
                    self.admin_config['email_smtp_port']
                )
                return server
            except (smtplib.socket.gaierror, smtplib.SMTPException) as ex:
                LOG.error('Failed to fetch client for smtp server %s and smtp\
                    port %s. Error %s' % (
                    self.admin_config['email_smtp_server'],
                    str(self.admin_config['email_smtp_port']),
                    ex
                ),
                    exc_info=True)
                raise NotificationDispatchError(str(ex))
        else:
            try:
                server = smtplib.SMTP(
                    self.admin_config['email_smtp_server'],
                    self.admin_config['email_smtp_port']
                )
                if self.admin_config['auth'] != '':
                    server.starttls()
                return server
            except (smtplib.socket.gaierror, smtplib.SMTPException) as ex:
                LOG.error('Failed to fetch client for smtp server %s and smtp\
                    port %s. Error %s' % (
                    self.admin_config['email_smtp_server'],
                    str(self.admin_config['email_smtp_port']),
                    ex
                ),
                    exc_info=True)
                raise NotificationDispatchError(str(ex))

    def dispatch_notification(self, alert):
        try:
            self.set_destinations(alert)
        except NotificationDispatchError as ex:
            LOG.error('Exception caught attempting to email %s.\
                Error %s' % (str(alert), str(ex)), exc_info=True)
            return
        try:
            msg = self.format_message(alert)
            server = self.get_mail_client()
            server.ehlo()
            if not self.admin_config:
                LOG.error(
                    'Detected alert %s.'
                    'But, admin config is a must to send notification'
                    % msg,
                    exc_info=True
                )
                return
            if self.admin_config['auth'] != "":
                server.login(
                    self.admin_config['email_id'],
                    self.admin_config['email_pass']
                )
            alert_destinations = self.get_alert_destinations(alert)
            if len(alert_destinations) == 0:
                LOG.error(
                    'No destinations configured to send %s alert notification'
                    % msg,
                    exc_info=True
                )
                return
            server.sendmail(
                self.admin_config['email_id'],
                alert_destinations,
                msg
            )
            LOG.debug(
                'Sent mail to %s to alert about %s'
                % (alert_destinations, msg),
                exc_info=True
            )
        except (
            NotificationDispatchError,
            error,
            smtplib.SMTPException,
            smtplib.SMTPAuthenticationError,
            smtplib.socket.gaierror,
            smtplib.SMTPSenderRefused,
            Exception
        ) as ex:
            LOG.error('Exception caught attempting to email %s.\
                Error %s' % (msg, ex), exc_info=True)
        finally:
            server.close()

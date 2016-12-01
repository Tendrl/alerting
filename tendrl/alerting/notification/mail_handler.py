import smtplib
import base64
from tendrl.common.config import TendrlConfig
import logging
from tendrl.common.etcdobj.etcdobj import Server as etcd_server
from etcd import EtcdKeyNotFound, EtcdConnectionFailed
from tendrl.common.config import ConfigNotFound
from socket import error
from ConfigParser import NoOptionError

config = TendrlConfig()
LOG = logging.getLogger(__name__)


class MailHandler():
    def get_users(self):
        admin_user = {}
        users = []
        # Fetch users from etcd.
        try:
            users = self.etcd_server.client.read(
                '/users', recursive=True).value
            for user in users:
                if user['is_admin']:
                    admin_user = user
                else:
                    users.append(user)
                    return admin_user, users
        except (EtcdKeyNotFound, EtcdConnectionFailed) as ex:
            try:
                email_id = config.get("tendrl_alerts", "admin_email_id")
                email_smtp_server = config.get(
                    "tendrl_alerts",
                    "admin_email_smtp_server"
                )
                email_smtp_port = int(config.get(
                    "tendrl_alerts",
                    "admin_email_smtp_port"
                )
                )
                recipient_email = config.get(
                    "tendrl_alerts",
                    "recipient_email_id"
                )
                recipient_subscriptions = config.get(
                    "tendrl_alerts",
                    "recipient_alert_subscriptions"
                )
            except (ConfigNotFound, NoOptionError) as ex:
                LOG.error('Error %s' % ex, exc_info=True)
                raise ex
            is_auth_enabled = False
            try:
                auth = config.get("tendrl_alerts", "admin_auth")
                try:
                    email_pass = base64.b64decode(config.get(
                        "tendrl_alerts",
                        "admin_email_pass"
                    )
                    )
                except (ConfigNotFound, NoOptionError, TypeError) as ex:
                    is_auth_enabled = True
                    LOG.error('User %s has chosen authentication but not \
                        provided the password' % email_id, exc_info=True)
                    raise ex
            except (ConfigNotFound, NoOptionError) as ex:
                if is_auth_enabled:
                    raise ex
                auth = ""
            admin_details = {
                'email_id': email_id,
                'email_smtp_port': email_smtp_port,
                'email_smtp_server': email_smtp_server,
                'auth': auth,
            }
            if admin_details['auth'] != "":
                admin_details['email_pass'] = email_pass
            return admin_details, [{
                'email_id': recipient_email,
                'alert_subscriptions': recipient_subscriptions,
            }]

    def format_message(self):
        return "Subject: [Alert] %s, %s threshold breached\n\n%s" % (
            self.alert['Plugin'], self.alert['Severity'], self.alert)

    def init_recipients(self):
        recipients = []
        for user in self.users:
            if user['alert_subscriptions'] == '*' or\
                    self.alert['Plugin'] in user['alert_subscriptions']:
                recipients.append(user['email_id'])
        return recipients

    def __init__(self, alert):
        try:
            etcd_kwargs = {
                'port': int(config.get("common", "etcd_port")),
                'host': config.get("common", "etcd_connection")
            }
            self.etcd_server = etcd_server(etcd_kwargs=etcd_kwargs)
            self.admin_user, self.users = self.get_users()
        except ConfigNotFound as ex:
            raise ex
        self.alert = alert
        self.recipients = self.init_recipients()
        self.msg = self.format_message()

    def get_mail_client(self):
        if self.admin_user['auth'] == 'ssl':
            try:
                server = smtplib.SMTP_SSL(
                    self.admin_user['email_smtp_server'],
                    self.admin_user['email_smtp_port']
                )
                return server
            except (smtplib.socket.gaierror, smtlib.SMTPException) as ex:
                LOG.error('Failed to fetch client for smtp server %s and smtp\
                    port %s. Error %s' % (
                    self.admin_user['email_smtp_server'],
                    str(self.admin_user['email_smtp_port']),
                    ex
                ),
                    exc_info=True)
        else:
            try:
                server = smtplib.SMTP(
                    self.admin_user['email_smtp_server'],
                    self.admin_user['email_smtp_port']
                )
                if self.admin_user['auth'] != '':
                    server.starttls()
                return server
            except (smtplib.socket.gaierror, smtlib.SMTPException) as ex:
                LOG.error('Failed to fetch client for smtp server %s and smtp\
                    port %s. Error %s' % (
                    self.admin_user['email_smtp_server'],
                    str(self.admin_user['email_smtp_port']),
                    ex
                ),
                    exc_info=True)

    def start(self):
        try:
            server = self.get_mail_client()
            server.ehlo()
            if self.admin_user['auth'] != "":
                server.login(
                    self.admin_user['email_id'],
                    self.admin_user['email_pass']
                )
            for to in self.recipients:
                server.sendmail(
                    self.admin_user['email_id'],
                    to,
                    self.msg
                )
                LOG.debug('Sent mail to %s to alert about %s' %
                          (to, self.msg), exc_info=True)
            server.close()
        except (error, smtplib.SMTPException,
                smtplib.SMTPAuthenticationError) as ex:
            LOG.debug('Exception caught attempting to send %s to %s.\
                Error %s' % (self.msg, self.recipients, ex), exc_info=True)

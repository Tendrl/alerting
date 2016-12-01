from mock import MagicMock
from tendrl.alerting.notification.mail_handler import MailHandler, config
from ConfigParser import NoOptionError
import pytest
import sys
sys.modules['tendrl.common.config'] = MagicMock()
del sys.modules['tendrl.common.config']


class Test_mail_handler():

    def test_mail_handler_constructor_success_with_auth(self, monkeypatch):
        def mock_config_get(package, parameter):
            if parameter == "admin_email_id":
                return 'admin@users.com'
            elif parameter == "admin_email_smtp_server":
                return "smtp.corp.users.com"
            elif parameter == 'admin_email_smtp_port':
                return '465'
            elif parameter == 'recipient_email_id':
                return 'user1@users.com'
            elif parameter == 'recipient_alert_subscriptions':
                return '*'
            elif parameter == 'admin_auth':
                return 'ssl'
            elif parameter == 'admin_email_pass':
                return 'bWFpbGhhbmRsZXI='
            elif parameter == 'etcd_connection':
                return '0.0.0.0'
            elif parameter == 'etcd_port':
                return '2379'

        monkeypatch.setattr(config, 'get', mock_config_get)
        admin_user = {
            "email_id": 'admin@users.com',
            'email_smtp_server': "smtp.corp.users.com",
            'email_smtp_port': 465,
            'auth': 'ssl',
            'email_pass': 'mailhandler',
        }
        recipient_user = {
            'email_id': 'user1@users.com',
            'alert_subscriptions': '*',
        }
        alert = {
            'Plugin': 'cpu',
            'Severity': 'Failure',
        }
        recipients = ['user1@users.com']
        mail_handler = MailHandler(alert)
        ret_admin, ret_users = mail_handler.get_users()
        assert ret_admin == admin_user
        assert ret_users == [recipient_user]
        message = "Subject: [Alert] %s, %s threshold breached\n\n%s" % (
            alert['Plugin'], alert['Severity'], alert)
        assert mail_handler.format_message() == message
        assert recipients == mail_handler.init_recipients()

    def test_mail_handler_constructor_success_without_auth(self, monkeypatch):

        def mock_config_get(package, parameter):
            if parameter == "admin_email_id":
                return 'admin@users.com'
            elif parameter == "admin_email_smtp_server":
                return "smtp.corp.users.com"
            elif parameter == 'admin_email_smtp_port':
                return '465'
            elif parameter == 'recipient_email_id':
                return 'user1@users.com'
            elif parameter == 'recipient_alert_subscriptions':
                return '*'
            elif parameter == 'etcd_connection':
                return '0.0.0.0'
            elif parameter == 'etcd_port':
                return '2379'
            elif parameter == 'admin_auth':
                raise NoOptionError('admin_auth', 'tendrl_alerts')

        monkeypatch.setattr(config, 'get', mock_config_get)
        admin_user = {
            "email_id": 'admin@users.com',
            'email_smtp_server': "smtp.corp.users.com",
            'email_smtp_port': 465,
            'auth': '',
        }
        recipient_user = {
            'email_id': 'user1@users.com',
            'alert_subscriptions': '*',
        }
        alert = {
            'Plugin': 'cpu',
            'Severity': 'Failure',
        }
        recipients = ['user1@users.com']
        mail_handler = MailHandler(alert)
        ret_admin, ret_users = mail_handler.get_users()
        assert ret_admin == admin_user
        assert ret_users == [recipient_user]
        message = "Subject: [Alert] %s, %s threshold breached\n\n%s" % (
            alert['Plugin'], alert['Severity'], alert)
        assert mail_handler.format_message() == message
        assert recipients == mail_handler.init_recipients()

    def test_mail_handler_constructor_auth_without_pass(self, monkeypatch):

        def mock_config_get(package, parameter):
            if parameter == "admin_email_id":
                return 'admin@users.com'
            elif parameter == "admin_email_smtp_server":
                return "smtp.corp.users.com"
            elif parameter == 'admin_email_smtp_port':
                return '465'
            elif parameter == 'recipient_email_id':
                return 'user1@users.com'
            elif parameter == 'recipient_alert_subscriptions':
                return '*'
            elif parameter == 'etcd_connection':
                return '0.0.0.0'
            elif parameter == 'etcd_port':
                return '2379'
            elif parameter == 'admin_auth':
                return 'ssl'
            elif parameter == 'admin_email_pass':
                raise NoOptionError('admin_email_pass', 'tendrl_alerts')

        monkeypatch.setattr(config, 'get', mock_config_get)
        alert = {
            'Plugin': 'cpu',
            'Severity': 'Failure',
        }
        pytest.raises(
            NoOptionError,
            MailHandler,
            alert
        )

    def test_mail_handler_constructor_Failure(self, monkeypatch):

        def mock_config_get(package, parameter):
            if parameter == "admin_email_id":
                return 'admin@users.com'
            elif parameter == "admin_email_smtp_server":
                return "smtp.corp.users.com"
            elif parameter == 'admin_email_smtp_port':
                return '465'
            elif parameter == 'etcd_connection':
                return '0.0.0.0'
            elif parameter == 'etcd_port':
                return '2379'
            elif parameter == 'admin_auth':
                return 'ssl'
            elif parameter == 'admin_email_pass':
                raise NoOptionError('admin_email_pass', 'tendrl_alerts')

        monkeypatch.setattr(config, 'get', mock_config_get)
        alert = {}
        pytest.raises(
            NoOptionError,
            MailHandler,
            alert
        )

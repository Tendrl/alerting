from mock import MagicMock
import multiprocessing
import pytest
import sys
sys.modules['tendrl.commons.config'] = MagicMock()
sys.modules['tendrl.common.log'] = MagicMock()
from tendrl.alerting.notification.handlers.mail_handler import EmailHandler
from tendrl.alerting.notification.handlers.mail_handler import \
    InvalidHandlerConfig
from tendrl.alerting.persistence.persister import AlertingEtcdPersister
from tendrl.commons.etcdobj.etcdobj import Server as etcd_server
del sys.modules['tendrl.common.log']
del sys.modules['tendrl.commons.config']


class Test_mail_handler(object):

    def get_etcd_server(self):
        return AlertingEtcdPersister()._store

    def test_config_help(self, monkeypatch):
        expected_config_help = {
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

        handler = EmailHandler(self.get_etcd_server())
        assert isinstance(handler.etcd_server, etcd_server)
        assert handler.get_config_help() == expected_config_help
        assert isinstance(handler.complete, multiprocessing.synchronize.Event)

    def test_mail_handler_constructor(self, monkeypatch):
        handler = EmailHandler(self.get_etcd_server())
        assert isinstance(handler.etcd_server, etcd_server)
        assert isinstance(handler.complete, multiprocessing.synchronize.Event)
        assert isinstance(handler.admin_config, dict)
        assert isinstance(handler.user_configs, list)

    def test_mail_handler_validate_admin_config_without_auth(
            self, monkeypatch):
        mail_config = {
            'email_id': 'admin@users.com',
            'email_smtp_server': 'smtp.corp.users.com',
            'email_smtp_port': '465',
            'is_admin': True,
        }

        mail_handler = EmailHandler(self.get_etcd_server())
        assert mail_handler.validate_config(mail_config)

    def test_mail_handler_validate_admin_config_without_auth_failure_condition(
            self, monkeypatch):
        mail_config = {
            'email_id': 'admin@users.com',
            'email_smtp_server': 'smtp.corp.users.com',
            'email_smtp_port': '465',
        }

        mail_handler = EmailHandler(self.get_etcd_server())
        pytest.raises(
            InvalidHandlerConfig,
            mail_handler.validate_config,
            mail_config
        )

    def test_mail_handler_validate_admin_with_auth(self, monkeypatch):
        mail_config = {
            'email_id': 'admin@users.com',
            'email_smtp_server': 'smtp.corp.users.com',
            'email_smtp_port': '465',
            'is_admin': True,
            'auth': 'ssl',
            'email_pass': 'XXXXXXXXXX'
        }

        mail_handler = EmailHandler(self.get_etcd_server())
        assert mail_handler.validate_config(mail_config)

    def test_mail_handler_validate_admin_with_auth_failure_condition(
            self, monkeypatch):
        mail_config = {
            'email_id': 'admin@users.com',
            'email_smtp_server': 'smtp.corp.users.com',
            'email_smtp_port': '465',
            'is_admin': True,
            'auth': 'ssl'
        }

        mail_handler = EmailHandler(self.get_etcd_server())
        pytest.raises(
            InvalidHandlerConfig,
            mail_handler.validate_config,
            mail_config
        )

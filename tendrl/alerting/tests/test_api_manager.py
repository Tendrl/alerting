from mock import MagicMock
import multiprocessing
import sys
sys.modules['tendrl.commons.config'] = MagicMock()
from tendrl.alerting.api.manager import APIManager
from tendrl.alerting.notification.manager import NotificationPluginManager
import tendrl.alerting.persistence.persister as persister
from tendrl.alerting.persistence.persister import AlertingEtcdPersister
del sys.modules['tendrl.commons.config']


class TestAPIManager(object):
    def get_persister(self):
        persister.load_config = MagicMock()
        persister.config = {
            'configuration': {
                'etcd_connection': '0.0.0.0',
                'etcd_port': '2379'
            }
        }
        return AlertingEtcdPersister()

    def get_notification_manager(self, monkeypatch):
        etcd_server = self.get_persister()._store

        def mock_etcd_server_write(path, data):
            return

        monkeypatch.setattr(
            etcd_server.client,
            'write',
            mock_etcd_server_write
        )
        return NotificationPluginManager(etcd_server)

    def test_manager_constructor(self, monkeypatch):
        manager = APIManager(
            '0.0.0.0',
            '5001',
            self.get_notification_manager(monkeypatch),
            self.get_persister()
        )
        assert manager.host == '0.0.0.0'
        assert isinstance(manager, APIManager)
        assert isinstance(manager._complete, multiprocessing.synchronize.Event)

    def test_manager_start(self, monkeypatch):
        manager = APIManager(
            '0.0.0.0',
            '5001',
            self.get_notification_manager(monkeypatch),
            self.get_persister()
        )

        def mock_start():
            return
        monkeypatch.setattr(manager, 'start', mock_start)

        manager.start()
        assert True

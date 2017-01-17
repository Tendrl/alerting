from mock import MagicMock
import sys
sys.modules['tendrl.commons.config'] = MagicMock()
sys.modules['tendrl.common.log'] = MagicMock()
from tendrl.alerting.notification.manager import NotificationPluginManager
from tendrl.alerting.persistence.persister import AlertingEtcdPersister
del sys.modules['tendrl.common.log']
del sys.modules['tendrl.commons.config']


class TestNotificationManager(object):
    def get_etcd_store(self):
        return AlertingEtcdPersister()._store

    def test_constructor(self, monkeypatch):
        etcd_server = self.get_etcd_store()

        def mock_write(path, value):
            assert True
            return

        monkeypatch.setattr(etcd_server.client, 'write', mock_write)
        NotificationPluginManager(etcd_server)

    def test_start(self, monkeypatch):
        etcd_server = self.get_etcd_store()

        def mock_start():
            assert True
            return

        def mock_write(path, value):
            return
        monkeypatch.setattr(etcd_server.client, 'write', mock_write)
        manager = NotificationPluginManager(etcd_server)
        monkeypatch.setattr(manager, 'start', mock_start)
        manager.start()

    def test_stop(self, monkeypatch):
        etcd_server = self.get_etcd_store()

        def mock_stop():
            assert True
            return

        def mock_write(path, value):
            return
        monkeypatch.setattr(etcd_server.client, 'write', mock_write)
        manager = NotificationPluginManager(etcd_server)
        monkeypatch.setattr(manager, 'stop', mock_stop)
        manager.stop()

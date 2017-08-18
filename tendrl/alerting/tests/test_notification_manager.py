from ConfigParser import SafeConfigParser
from mock import MagicMock
import sys
sys.modules['tendrl.common.log'] = MagicMock()
from tendrl.alerting.notification.manager import NotificationPluginManager
from tendrl.alerting.persistence.persister import AlertingEtcdPersister
del sys.modules['tendrl.common.log']


class TestNotificationManager(object):
    def get_etcd_store(self):
        cParser = SafeConfigParser()
        cParser.add_section('commons')
        cParser.set('commons', 'etcd_connection', '0.0.0.0')
        cParser.set('commons', 'etcd_port', '2379')
        return AlertingEtcdPersister(cParser).get_store()

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

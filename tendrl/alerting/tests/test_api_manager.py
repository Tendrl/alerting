from ConfigParser import SafeConfigParser
from mock import MagicMock
import multiprocessing
import sys
sys.modules['tendrl.common.log'] = MagicMock()
from tendrl.alerting.api.manager import APIManager
from tendrl.alerting.notification.manager import NotificationPluginManager
from tendrl.alerting.persistence.persister import AlertingEtcdPersister
del sys.modules['tendrl.common.log']


class TestAPIManager(object):
    def get_persister(self):
        cParser = SafeConfigParser()
        cParser.add_section('commons')
        cParser.set('commons', 'etcd_connection', '0.0.0.0')
        cParser.set('commons', 'etcd_port', '2379')
        return AlertingEtcdPersister(cParser)

    def get_notification_manager(self):
        return NotificationPluginManager(self.get_persister().get_store())

    def test_manager_constructor(self, monkeypatch):
        manager = APIManager('0.0.0.0', '5001', self.get_notification_manager(), self.get_persister())
        assert manager.host == '0.0.0.0'
        assert isinstance(manager, APIManager)
        assert isinstance(manager._complete, multiprocessing.synchronize.Event)

    def test_manager_start(self, monkeypatch):
        manager = APIManager('0.0.0.0', '5001', self.get_notification_manager(), self.get_persister())

        def mock_start():
            return
        monkeypatch.setattr(manager, 'start', mock_start)

        manager.start()
        assert True

from ConfigParser import SafeConfigParser
import etcd
from mock import MagicMock
import multiprocessing
import sys
sys.modules['tendrl.commons.log'] = MagicMock()
from tendrl.alerting.persistence.persister import AlertingEtcdPersister
from tendrl.alerting.watcher.manager import AlertsWatchManager
del sys.modules['tendrl.commons.log']


class TestAlertsWatcher(object):
    def get_etcd_client(self):
        cParser = SafeConfigParser()
        cParser.add_section('commons')
        cParser.set('commons', 'etcd_connection', '0.0.0.0')
        cParser.set('commons', 'etcd_port', '2379')
        return AlertingEtcdPersister(cParser)._store.client

    def test_constructor(self, monkeypatch):
        manager = AlertsWatchManager(
            multiprocessing.Queue(),
            self.get_etcd_client()
        )
        assert isinstance(manager, AlertsWatchManager)
        assert isinstance(manager.etcd_client, etcd.client.Client)

    def test_run(self, monkeypatch):
        manager = AlertsWatchManager(
            multiprocessing.Queue(),
            self.get_etcd_client()
        )

        def mock_run():
            return
        monkeypatch.setattr(manager, 'run', mock_run)
        manager.start()
        assert True

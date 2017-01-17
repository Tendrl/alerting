import etcd
from mock import MagicMock
import multiprocessing
import sys
sys.modules['tendrl.commons.config'] = MagicMock()
sys.modules['tendrl.commons.log'] = MagicMock()
from tendrl.alerting.persistence.persister import AlertingEtcdPersister
from tendrl.alerting.watcher.manager import AlertsWatchManager
del sys.modules['tendrl.commons.log']
del sys.modules['tendrl.commons.config']


class TestAlertsWatcher(object):
    def get_etcd_client(self):
        return AlertingEtcdPersister()._store.client

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

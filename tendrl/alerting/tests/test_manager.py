from mock import MagicMock
import multiprocessing
import sys
sys.modules['tendrl.commons.config'] = MagicMock()
sys.modules['tendrl.commons.log'] = MagicMock()
from tendrl.alerting.api.manager import APIManager
from tendrl.alerting.manager import manager
from tendrl.alerting.manager.manager import AlertingManager
from tendrl.alerting.watcher.manager import AlertsWatchManager
del sys.modules['tendrl.commons.config']
del sys.modules['tendrl.commons.log']


class TestManager(object):

    def test_constructor(self, monkeypatch):
        manager.load_config = MagicMock()
        aManager = AlertingManager()
        assert isinstance(aManager.api_manager, APIManager)
        assert isinstance(aManager.watch_manager, AlertsWatchManager)
        assert isinstance(aManager.alert_queue, multiprocessing.queues.Queue)

    def test_start(self, monkeypatch):
        manager.load_config = MagicMock()
        aManager = AlertingManager()

        def mock_start():
            return
        monkeypatch.setattr(aManager, 'start', mock_start)
        aManager.start()
        assert True

    def test_stop(self, monkeypatch):
        manager.load_config = MagicMock()
        aManager = AlertingManager()

        def mock_stop():
            return
        monkeypatch.setattr(aManager, 'stop', mock_stop)
        aManager.stop()
        assert True

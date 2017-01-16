from mock import MagicMock
import multiprocessing
import sys
sys.modules['tendrl.common.config'] = MagicMock()
sys.modules['tendrl.common.log'] = MagicMock()
from tendrl.alerting.api.manager import APIManager
from tendrl.alerting.manager.manager import Manager
from tendrl.alerting.watcher.manager import AlertsWatchManager
del sys.modules['tendrl.common.config']
del sys.modules['tendrl.common.log']


class TestManager(object):
    def test_constructor(self, monkeypatch):
        manager = Manager()
        assert isinstance(manager.api_manager, APIManager)
        assert isinstance(manager.watch_manager, AlertsWatchManager)
        assert isinstance(manager.alert_queue, multiprocessing.queues.Queue)

    def test_start(self, monkeypatch):
        manager = Manager()

        def mock_start():
            return
        monkeypatch.setattr(manager, 'start', mock_start)
        manager.start()
        assert True

    def test_stop(self, monkeypatch):
        manager = Manager()

        def mock_stop():
            return
        monkeypatch.setattr(manager, 'stop', mock_stop)
        manager.stop()
        assert True

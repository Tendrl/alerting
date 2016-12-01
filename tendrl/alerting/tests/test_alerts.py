from mock import MagicMock
from tendrl.alerting.alerts import AlertsManager, config
from multiprocessing import queues, Queue
from tendrl.common.etcdobj.etcdobj import Server as etcd_server
import sys
sys.modules['tendrl.common.config'] = MagicMock()
del sys.modules['tendrl.common.config']


class Test_alerts():

    def test_alerts_manager_constructor(self, monkeypatch):
        def mock_config_get(package, parameter):
            if parameter == 'etcd_connection':
                return '0.0.0.0'
            elif parameter == 'etcd_port':
                return '2379'

        monkeypatch.setattr(config, 'get', mock_config_get)
        manager = AlertsManager(Queue())
        assert isinstance(manager.alerts_queue, queues.Queue)
        assert isinstance(manager.etcd_server, etcd_server)

    def test_alerts_manager_start(self, monkeypatch):

        def mock_config_get(package, parameter):
            if parameter == 'etcd_connection':
                return '0.0.0.0'
            elif parameter == 'etcd_port':
                return '2379'

        monkeypatch.setattr(config, 'get', mock_config_get)
        manager = AlertsManager(Queue())

        def mock_start():
            return

        monkeypatch.setattr(manager, 'run', mock_start)

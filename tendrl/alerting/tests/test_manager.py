from mock import MagicMock
from tendrl.alerting.manager import TendrlManager, config
from multiprocessing import queues
from tendrl.alerting.alerts import AlertsManager
from tendrl.alerting.notification.alert_notification_manager \
    import AlertNotificationManager
import sys
sys.modules['tendrl.common.config'] = MagicMock()
del sys.modules['tendrl.common.config']


class Test_manager():

    def test_manager_constructor(self, monkeypatch):
        def mock_config_get(package, parameter):
            if parameter == 'etcd_connection':
                return '0.0.0.0'
            elif parameter == 'etcd_port':
                return '2379'

        monkeypatch.setattr(config, 'get', mock_config_get)
        manager = TendrlManager()
        assert isinstance(manager.alerts_queue, queues.Queue)
        assert isinstance(manager.alerts_manager, AlertsManager)
        assert isinstance(manager.notification_manager,
                          AlertNotificationManager)

    def test_manager_start(self, monkeypatch):

        def mock_config_get(package, parameter):
            if parameter == 'etcd_connection':
                return '0.0.0.0'
            elif parameter == 'etcd_port':
                return '2379'
        monkeypatch.setattr(config, 'get', mock_config_get)
        manager = TendrlManager()

        def mock_alerts_manager_start():
            return

        def mock_notification_manager_start():
            return

        monkeypatch.setattr(manager.alerts_manager, 'start',
                            mock_alerts_manager_start)
        monkeypatch.setattr(manager.notification_manager,
                            'start', mock_notification_manager_start)
        manager.start()

    def test_manager_stop(self, monkeypatch):

        def mock_config_get(package, parameter):
            if parameter == 'etcd_connection':
                return '0.0.0.0'
            elif parameter == 'etcd_port':
                return '2379'

        monkeypatch.setattr(config, 'get', mock_config_get)
        manager = TendrlManager()

        def mock_alerts_manager_stop():
            return

        def mock_notification_manager_stop():
            return

        monkeypatch.setattr(manager.alerts_manager, 'stop',
                            mock_alerts_manager_stop)
        monkeypatch.setattr(manager.notification_manager,
                            'stop', mock_notification_manager_stop)
        manager.stop()

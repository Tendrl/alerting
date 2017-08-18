from ConfigParser import SafeConfigParser
import etcd
import json
from mock import MagicMock
import sys
sys.modules['tendrl.common.log'] = MagicMock()
from tendrl.alerting.persistence.persister import AlertingEtcdPersister
import uuid
import yaml
del sys.modules['tendrl.common.log']


class TestNotificationManager(object):
    def get_persister(self):
        cParser = SafeConfigParser()
        cParser.add_section('commons')
        cParser.set('commons', 'etcd_connection', '0.0.0.0')
        cParser.set('commons', 'etcd_port', '2379')
        return AlertingEtcdPersister(cParser)

    def get_alert(self, resource, alert_id, node_id=None):
        alert = {
            "alert_type": "percent_bytes",
            "resource": "%s" % resource,
            "severity": "CRITICAL",
            "tags": {
                "message": 'Host XX.YY.ZZ, plugin %s'
                'type percent_bytes (instance used): Data '
                'source \"value\" is currently 2.650770. That is above the '
                'failure threshold of 2.000000.\\n' % resource,
                "warning_max": "1.000000e+00",
                "failure_max": "2.000000e+00"
            },
            "pid": "30033",
            "acked": False,
            "ackedby": "",
            "source": "collectd",
            "alert_id": "%s" % alert_id,
            "node_id": "05694096-0a59-4d34-835a-2595770b9e56",
            "significance": "HIGH",
            "current_value": "2.650770e+00",
            "time_stamp": "1482912389.914"
        }
        if node_id is not None:
            alert['node_id'] = node_id
        return alert

    def alert_to_etcd_alert(
        self, alert, modified_index, created_index, is_dir
    ):
        ret_val = {
            'key': "/alerts/%s" % alert['alert_id'],
            'value': json.dumps(alert),
            'expiration': None,
            'ttl': None,
            'modifiedIndex': modified_index,
            'createdIndex': created_index,
            'newKey': False,
            'dir': is_dir,
        }
        return ret_val

    def test_constructor(self, monkeypatch):
        self.get_persister()
        assert True

    def test_get_alerts_without_filter(self, monkeypatch):
        persister = self.get_persister()
        df_alert_id = str(uuid.uuid4())
        alert1_dict = self.get_alert('df', df_alert_id)
        etcd_alert1 = self.alert_to_etcd_alert(alert1_dict, 5, 1, False)
        memory_alert_id = str(uuid.uuid4())
        alert2_dict = self.get_alert('memory', memory_alert_id)
        etcd_alert2 = self.alert_to_etcd_alert(alert2_dict, 6, 2, False)
        cpu_alert_id = str(uuid.uuid4())
        alert3_dict = self.get_alert('cpu', cpu_alert_id)
        etcd_alert3 = self.alert_to_etcd_alert(alert3_dict, 7, 3, False)
        swap_alert_id = str(uuid.uuid4())
        alert4_dict = self.get_alert('swap', swap_alert_id)
        etcd_alert4 = self.alert_to_etcd_alert(alert4_dict, 8, 4, False)

        def get_etcd_alerts(path, recursive):
            etcd_tree = {
                "node": {
                    'key': "/alerts/",
                    'expiration': None,
                    'ttl': None,
                    'modifiedIndex': 5,
                    'createdIndex': 1,
                    'newKey': False,
                    'dir': True,
                    'nodes': [
                        etcd_alert1,
                        etcd_alert2,
                        etcd_alert3,
                        etcd_alert4
                    ]
                }
            }
            return etcd.EtcdResult(**etcd_tree)

        expected_alerts = sorted(
            [alert1_dict, alert2_dict, alert3_dict, alert4_dict]
        )

        monkeypatch.setattr(persister._store.client, 'read', get_etcd_alerts)
        assert sorted(persister.get_alerts()) == expected_alerts

    def test_get_alerts_with_filter(self, monkeypatch):
        persister = self.get_persister()
        df_alert_id = str(uuid.uuid4())
        alert1_dict = self.get_alert('df', df_alert_id)
        etcd_alert1 = self.alert_to_etcd_alert(alert1_dict, 5, 1, False)
        memory_alert_id = str(uuid.uuid4())
        alert2_dict = self.get_alert('memory', memory_alert_id)
        etcd_alert2 = self.alert_to_etcd_alert(alert2_dict, 6, 2, False)
        cpu_alert_id = str(uuid.uuid4())
        alert3_dict = self.get_alert('cpu', cpu_alert_id)
        etcd_alert3 = self.alert_to_etcd_alert(alert3_dict, 7, 3, False)
        swap_alert_id = str(uuid.uuid4())
        alert4_dict = self.get_alert('swap', swap_alert_id)
        etcd_alert4 = self.alert_to_etcd_alert(alert4_dict, 8, 4, False)

        def get_etcd_alerts(path, recursive):
            etcd_tree = {
                "node": {
                    'key': "/alerts/",
                    'expiration': None,
                    'ttl': None,
                    'modifiedIndex': 5,
                    'createdIndex': 1,
                    'newKey': False,
                    'dir': True,
                    'nodes': [
                        etcd_alert1,
                        etcd_alert2,
                        etcd_alert3,
                        etcd_alert4
                    ]
                }
            }
            return etcd.EtcdResult(**etcd_tree)

        expected_alerts = sorted(
            [alert4_dict]
        )

        monkeypatch.setattr(persister._store.client, 'read', get_etcd_alerts)
        assert persister.get_alerts(
            [['resource', 'swap']]) == expected_alerts

    def test_get_alerts_with_node_id_filter(self, monkeypatch):
        persister = self.get_persister()
        node1_id = str(uuid.uuid4())
        node2_id = str(uuid.uuid4())
        df_alert_id = str(uuid.uuid4())
        alert1_dict = self.get_alert('df', df_alert_id, node1_id)
        etcd_alert1 = self.alert_to_etcd_alert(alert1_dict, 5, 1, False)
        memory_alert_id = str(uuid.uuid4())
        alert2_dict = self.get_alert('memory', memory_alert_id, node2_id)
        etcd_alert2 = self.alert_to_etcd_alert(alert2_dict, 6, 2, False)
        cpu_alert_id = str(uuid.uuid4())
        alert3_dict = self.get_alert('cpu', cpu_alert_id, node1_id)
        etcd_alert3 = self.alert_to_etcd_alert(alert3_dict, 7, 3, False)
        swap_alert_id = str(uuid.uuid4())
        alert4_dict = self.get_alert('swap', swap_alert_id, node2_id)
        etcd_alert4 = self.alert_to_etcd_alert(alert4_dict, 8, 4, False)

        def get_etcd_alerts(path, recursive):
            etcd_tree = {
                "node": {
                    'key': "/alerts/",
                    'expiration': None,
                    'ttl': None,
                    'modifiedIndex': 5,
                    'createdIndex': 1,
                    'newKey': False,
                    'dir': True,
                    'nodes': [
                        etcd_alert1,
                        etcd_alert2,
                        etcd_alert3,
                        etcd_alert4
                    ]
                }
            }
            return etcd.EtcdResult(**etcd_tree)

        expected_alerts = sorted(
            [alert1_dict, alert3_dict]
        )

        monkeypatch.setattr(persister._store.client, 'read', get_etcd_alerts)
        node_ids = ['%s' % node1_id]
        assert sorted(persister.get_alerts([['node_id', str(node_ids)]]))\
            == sorted(expected_alerts)

    def test_get_alert_types(self, monkeypatch):
        persister = self.get_persister()
        expected_alert_types = {
            'node_agent': [
                'swap',
                'df',
                'memory',
                'cpu'
            ]
        }
        module1 = {
            'key': '/alerting/alert_types/node_agent',
            'value': "['swap', 'df', 'memory', 'cpu']",
            'expiration': None,
            'ttl': None,
            'modifiedIndex': 5,
            'createdIndex': 1,
            'newKey': False,
            'dir': False
        }
        types = {
            "node": {
                'key': "/alerting/alert_types/",
                'expiration': None,
                'ttl': None,
                'modifiedIndex': 5,
                'createdIndex': 1,
                'newKey': False,
                'dir': True,
                'nodes': [module1]
            }
        }

        def get_etcd_alert_types(path, recursive):
            return etcd.EtcdResult(**types)

        monkeypatch.setattr(
            persister._store.client,
            'read',
            get_etcd_alert_types
        )
        assert persister.get_alert_types() == expected_alert_types

    def test_write_configs(self, monkeypatch):
        persister = self.get_persister()

        def mock_write(path, config_str):
            confs = {
                'api_server_addr': '0.0.0.0',
                'api_server_port': '5001'
            }
            assert yaml.safe_dump(confs) == config_str
            return
        monkeypatch.setattr(
            persister._store.client,
            'write',
            mock_write
        )
        persister.write_configs('0.0.0.0', '5001')

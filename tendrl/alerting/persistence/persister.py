import ast
import etcd
import logging
from tendrl.alerting.manager.tendrl_definitions_alerting \
    import data as def_data
from tendrl.alerting.persistence.exceptions import EtcdError
from tendrl.alerting.persistence.tendrl_definitions \
    import TendrlDefinitions
from tendrl.commons.config import load_config
from tendrl.commons.etcdobj.etcdobj import Server as etcd_server
from tendrl.commons.persistence.etcd_persister import EtcdPersister
import time
import yaml


LOG = logging.getLogger(__name__)

config = load_config(
    'commons',
    '/etc/tendrl/commons/commons.conf.yaml'
)


class AlertingEtcdPersister(EtcdPersister):
    def __init__(self, config):
        etcd_kwargs = {
            'port': int(config["configuration"]["etcd_port"]),
            'host': config["configuration"]["etcd_connection"]
        }
        self._store = etcd_server(etcd_kwargs=etcd_kwargs)
        super(
            AlertingEtcdPersister,
            self
        ).__init__(self._store.client)

    def write_configs(self, api_server_addr, api_server_port):
        confs = {
            'api_server_addr': api_server_addr,
            'api_server_port': api_server_port
        }
        self._store.client.write(
            '/_tendrl/config/alerting',
            yaml.safe_dump(confs)
        )

    def get_alerts(self, filters=None):
        alerts_arr = []
        try:
            alerts = self._store.client.read('/alerts', recursive=True)
        except etcd.EtcdKeyNotFound:
            return alerts_arr
        except (
            etcd.EtcdConnectionFailed,
            ValueError,
            SyntaxError,
            TypeError
        ) as ex:
            LOG.error(
                'Failed to fetch alerts. Error %s' % str(ex),
                exc_info=True
            )
            raise EtcdError(str(ex))
        for child in alerts._children:
            alerts_arr.append(yaml.safe_load(child['value']))
        if filters is not None:
            filtered_alerts = {}
            for f in filters:
                for alert in alerts_arr:
                    if 'alert_id' not in alert:
                        raise KeyError(
                            "Alert %s doesn't have id" % str(alert)
                        )
                    key = alert['alert_id']
                    try:
                        criteria = ast.literal_eval(f[1])
                        if isinstance(criteria, list):
                            if alert[f[0]] in f[1]:
                                filtered_alerts[key] = alert
                        else:
                            raise EtcdError(
                                'Invalid parameter type passed'
                            )
                    except ValueError:
                        if alert[f[0]] == f[1]:
                            filtered_alerts[key] = alert
                    except (TypeError, SyntaxError, KeyError) as ex:
                        raise EtcdError(str(ex))
            alerts_arr = filtered_alerts.values()
        return alerts_arr

    def get_alert_types(self):
        try:
            alert_types = {}
            alert_type_etcd_result = self._store.client.read(
                '/alerting/alert_types/',
                recursive=True
            )
            for child in alert_type_etcd_result._children:
                component = child['key'][len('/alerting/alert_types/'):]
                component_alert_types = ast.literal_eval(child['value'])
                alert_types[component.encode(
                    'ascii',
                    'ignore'
                )] = component_alert_types
            return alert_types
        except (
            etcd.EtcdKeyNotFound,
            etcd.EtcdConnectionFailed,
            ValueError,
            SyntaxError,
            etcd.EtcdException,
            TypeError
        ) as ex:
            LOG.error(
                'Failed to fetch supported alert types',
                exc_info=True
            )
            raise EtcdError(str(ex))

    def update_defs(self):
        self._store.save(
            TendrlDefinitions(
                updated=str(time.time()),
                data=yaml.safe_dump(yaml.load(def_data))
            )
        )

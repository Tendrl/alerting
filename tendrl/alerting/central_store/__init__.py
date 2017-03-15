from tendrl.alerting.objects.alert import Alert
from tendrl.alerting.objects.alert_types import AlertTypes
from tendrl.commons import central_store


class AlertingEtcdPersister(central_store.EtcdCentralStore):
    def __init__(self):
        super(AlertingEtcdPersister, self).__init__()

    def save_config(self, config):
        tendrl_ns.etcd_orm.save(config)

    def save_definition(self, definition):
        tendrl_ns.etcd_orm.save(definition)

    def get_alert_types(self):
        return AlertTypes().load()

    def get_alert(self, alert_id):
        return Alert(alert_id).load()

    def get_alerts(self):
        alerts_arr = []
        alerts = tendrl_ns.etcd_orm.client.read('/alerting/alerts')
        for child in alerts._children:
            alert_id = (child['key'])[len('/alerting/alerts/'):]
            alerts_arr.append(
                Alert(alert_id=alert_id).load()
            )
        return alerts_arr

    def save_alert(self, alert):
        tendrl_ns.etcd_orm.save(alert)

    def save_nodealert(self, node_alert):
        tendrl_ns.etcd_orm.save(node_alert)

    def save_notificationmedia(self, notification_media):
        tendrl_ns.etcd_orm.save(notification_media)

    def save_alerttypes(self, alert_types):
        tendrl_ns.etcd_orm.save(alert_types)

    def save_notificationconfigfield(self, notification_config_field):
        tendrl_ns.etcd_orm.save(notification_config_field)

    def save_notificationconfig(self, notification_config):
        tendrl_ns.etcd_orm.save(notification_config)

    def save_clusteralert(self, cluster_alert):
        tendrl_ns.etcd_orm.save(cluster_alert)

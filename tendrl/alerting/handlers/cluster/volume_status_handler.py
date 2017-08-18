from tendrl.alerting.handlers import AlertHandler
from tendrl.alerting.objects.cluster_alert import ClusterAlert


class VolumeStatusHandler(AlertHandler):
    handles = 'volume_status'
    representive_name = 'volume_status_alert'

    def __init__(self):
        AlertHandler.__init__(self)

    def format_alert_message(self):
        return

    def classify_alert(self):
        ClusterAlert(
            alert_id=self.alert.alert_id,
            node_id=self.alert.node_id,
            time_stamp=self.alert.time_stamp,
            resource=self.alert.resource,
            current_value=self.alert.current_value,
            tags=self.alert.tags,
            alert_type=self.alert.alert_type,
            severity=self.alert.severity,
            significance=self.alert.significance,
            ackedby=self.alert.ackedby,
            acked=self.alert.acked,
            pid=self.alert.pid,
            source=self.alert.source,
        ).save(update=False)

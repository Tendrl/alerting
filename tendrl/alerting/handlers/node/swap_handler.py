from tendrl.alerting.handlers import AlertHandler
from tendrl.alerting.objects.node_alert import NodeAlert


class SwapHandler(AlertHandler):

    handles = 'swap'
    representive_name = 'swap_alert'

    def __init__(self):
        AlertHandler.__init__(self)

    def classify_alert(self):
        NodeAlert(
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
        ).save()

from tendrl.alerting.handlers import AlertHandler
from tendrl.alerting.objects.cluster_alert import ClusterAlert


class ClusterUtilizationHandler(AlertHandler):

    handles = 'cluster_utilization'
    representive_name = 'cluster_utilization_alert'

    def __init__(self):
        AlertHandler.__init__(self)

    def format_alert_message(self):
        if (
            'message' not in self.alert.tags and
            'cluster_name' not in self.alert.tags and
            'failure_max' not in self.alert.tags and
            'warning_max' not in self.alert.tags
        ):
            return
        if self.alert.severity == "INFO":
            self.alert.tags['message'] = "Cluster utilization of cluster %s is\
             back to normal. The current utilization is %s %%." % (
                self.alert.tags['cluster_name'],
                str(float(self.alert.current_value))
            )
            return
        threshold = ""
        if self.alert.severity == "WARNING":
            threshold = str(float(self.alert.tags['warning_max']))
        else:
            threshold = str(float(self.alert.tags['failure_max']))
        self.alert.tags['message'] = "Cluster utilization of cluster %s is\
         %s %% which is above the %s threshold (%s)." % (
            self.alert.tags['cluster_name'],
            str(float(self.alert.current_value)),
            self.alert.severity,
            threshold
        )
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

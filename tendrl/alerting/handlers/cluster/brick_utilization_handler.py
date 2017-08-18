from tendrl.alerting.handlers import AlertHandler
from tendrl.alerting.objects.cluster_alert import ClusterAlert


class BrickUtilizationHandler(AlertHandler):

    handles = 'brick_utilization'
    representive_name = 'brick_utilization_alert'

    def __init__(self):
        AlertHandler.__init__(self)

    def format_alert_message(self):
        if (
            'message' not in self.alert.tags and
            'cluster_name' not in self.alert.tags and
            'failure_max' not in self.alert.tags and
            'warning_max' not in self.alert.tags and
            'plugin_instance' not in self.alert.tags
        ):
            return
        vol_name, host_name, brick_path = self.alert.tags[
            'plugin_instance'
        ].split("|")
        vol_name = vol_name.split('volume_')[1]
        brick_path = brick_path.split('brick_')[1]
        host_name = host_name.split('host_')[1]
        host_name = host_name.replace('_', '.')
        if self.alert.severity == "INFO":
            self.alert.tags['message'] = "Brick utilization of %s of host %s in \
            volume %s in cluster %s is back normal.Current value is %s %%" % (
                brick_path,
                host_name,
                vol_name,
                self.alert.tags['cluster_name'],
                str(float(self.alert.current_value))
            )
            return
        threshold = ""
        if self.alert.severity == "WARNING":
            threshold = str(float(self.alert.tags['warning_max']))
        else:
            threshold = str(float(self.alert.tags['failure_max']))
        self.alert.tags['message'] = "Brick utilization of %s of host %s in \
        volume %s in cluster %s is %s %% which is above %s threshold %s" % (
            brick_path,
            host_name,
            vol_name,
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

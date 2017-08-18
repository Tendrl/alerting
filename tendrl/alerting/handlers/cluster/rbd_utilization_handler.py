from tendrl.alerting.handlers import AlertHandler
from tendrl.alerting.objects.cluster_alert import ClusterAlert


class RBDUtilizationHandler(AlertHandler):

    handles = 'rbd_utilization'
    representive_name = 'rbd_utilization_alert'

    def __init__(self):
        AlertHandler.__init__(self)

    def format_alert_message(self):
        if (
            'message' not in self.alert.tags or
            'cluster_name' not in self.alert.tags or
            'failure_max' not in self.alert.tags or
            'warning_max' not in self.alert.tags or
            'plugin_instance' not in self.alert.tags
        ):
            return
        pool, rbd = self.alert.tags['plugin_instance'].split('|')
        rbd = rbd.split('name_')[1]
        pool = pool.split('pool_')[1]
        if self.alert.severity == "INFO":
            self.alert.tags['message'] = "RBD utilization of %s in pool %s of\
            cluster %s is back normal. The current utilization is %s %%." % (
                rbd,
                pool,
                self.alert.tags['cluster_name'],
                str(float(self.alert.current_value))
            )
            return
        threshold = ""
        if self.alert.severity == "WARNING":
            threshold = str(float(self.alert.tags['warning_max']))
        else:
            threshold = str(float(self.alert.tags['failure_max']))
        self.alert.tags['message'] = "RBD utilization of %s in pool %s of\
        cluster %s is %s %% which is above the %s threshold (%s)." % (
            rbd,
            pool,
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

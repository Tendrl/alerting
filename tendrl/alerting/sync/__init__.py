from etcd import EtcdException
import gevent
import gevent.event
import tendrl.alerting.constants as alerting_consts
import tendrl.alerting.utils.central_store_util as central_store_util
from tendrl.alerting.objects.cluster_alert_counters import ClusterAlertCounters
from tendrl.alerting.objects.node_alert_counters import NodeAlertCounters
from tendrl.alerting.utils.util import parse_resource_alerts
from tendrl.commons.utils import log_utils as logger


class TendrlAlertingSync(gevent.greenlet.Greenlet):
    def __init__(self):
        super(TendrlAlertingSync, self).__init__()
        self.complete = gevent.event.Event()

    def update_nodes_alert_count(self):
        node_ids = central_store_util.get_node_ids()
        for node_id in node_ids:
            try:
                crit_alerts, warn_alerts = parse_resource_alerts(
                    None,
                    alerting_consts.NODE,
                    node_id=node_id,
                )
                NodeAlertCounters(
                    warn_count=len(warn_alerts),
                    crit_count=len(crit_alerts),
                    node_id=node_id
                ).save(update=False)
            except (
                AttributeError,
                EtcdException,
                ValueError,
                SyntaxError,
                TypeError
            ) as ex:
                logger.log(
                    "error",
                    NS.get(
                        "publisher_id",
                        None
                    ),
                    {
                        "message": 'Failed to update node alert counter.'
                        ' Exception %s' % str(ex)
                    }
                )
                continue

    def update_clusters_alert_count(self):
        try:
            integration_ids = central_store_util.get_integration_ids()
        except (EtcdException, AttributeError) as ex:
            logger.log(
                "error",
                NS.get(
                    "publisher_id",
                    None
                ),
                {
                    "message": 'Failed to update cluster alert counter.'
                    ' Exception %s' % str(ex)
                }
            )
        for integration_id in integration_ids:
            try:
                crit_alerts, warn_alerts = parse_resource_alerts(
                    None,
                    alerting_consts.CLUSTER,
                    integration_id=integration_id,
                )
                ClusterAlertCounters(
                    warn_count=len(warn_alerts),
                    crit_count=len(crit_alerts),
                    integration_id=integration_id
                ).save(update=False)
            except (
                EtcdException,
                AttributeError,
                KeyError,
                TypeError,
                ValueError,
                SyntaxError
            ) as ex:
                logger.log(
                    "error",
                    NS.get(
                        "publisher_id",
                        None
                    ),
                    {
                        "message": 'Failed to update cluster alert counter.'
                        ' Exception %s' % str(ex)
                    }
                )
                continue

    def _run(self):
        while not self.complete.is_set():
            self.update_nodes_alert_count()
            self.update_clusters_alert_count()
            gevent.sleep(30)

    def stop(self):
        self.complete.set()

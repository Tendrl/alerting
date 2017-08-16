from etcd import EtcdException
from etcd import EtcdKeyNotFound
from tendrl.notifier.objects.alert import Alert
from tendrl.notifier.objects.cluster_alert import ClusterAlert
from tendrl.notifier.objects.node_alert import NodeAlert


def read_key(key):
    try:
        return NS._int.client.read(key, quorum=True)
    except (AttributeError, EtcdException) as ex:
        if type(ex) == EtcdKeyNotFound:
            raise ex
        else:
            try:
                NS._int.reconnect()
                return NS._int.client.read(key, quorum=True)
            except (AttributeError, EtcdException) as ex:
                raise ex


def read(key):
    result = {}
    job = {}
    job = read_key(key)
    if hasattr(job, 'leaves'):
        for item in job.leaves:
            if key == item.key:
                result[item.key.split("/")[-1]] = item.value
                return result
            if item.dir is True:
                result[item.key.split("/")[-1]] = read(item.key)
            else:
                result[item.key.split("/")[-1]] = item.value
    return result


def get_alerts():
    alerts_arr = []
    alerts = read('/alerting/alerts')
    for alert_id, alert in alerts.iteritems():
        alerts_arr.append(Alert(**alert))
    return alerts_arr


def update_alert_delivery(alert):
    alert.delivery = True
    # update alert
    alert.save()
    if "integration_id" in alert.tags:
        # cluster alert
        cluster_alert = read(
            "/alerting/clusters/%s/%s" % (
                alert.tags['integration_id'],
                alert.alert_id
            )
        )
        cluster_alert['delivery'] = alert.delivery
        ClusterAlert(**cluster_alert).save()
    else:
        # node alert
        node_alert = read(
            "/alerting/nodes/%s/%s" % (
                alert.node_id,
                alert.alert_id
            )
        )
        node_alert['delivery'] = alert.delivery
        NodeAlert(**node_alert).save()

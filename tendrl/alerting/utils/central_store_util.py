from etcd import EtcdException
from etcd import EtcdKeyNotFound
from string import Template

import tendrl.alerting.constants as alerting_consts
from tendrl.alerting.objects.alert import Alert
from tendrl.alerting.objects.alert import AlertUtils
from tendrl.alerting.objects.alert_types import AlertTypes


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


# this function can return json for any etcd key
def read(key):
    result = {}
    job = {}
    try:
        job = read_key(key)
    except EtcdKeyNotFound:
        pass
    except (AttributeError, EtcdException) as ex:
        raise ex
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


def get_node_ids():
    try:
        node_ids = []
        nodes_etcd = read_key('/nodes')
        for node in nodes_etcd.leaves:
            node_key_contents = node.key.split('/')
            if len(node_key_contents) == 3:
                node_ids.append(node_key_contents[2])
        return node_ids
    except EtcdKeyNotFound:
        return []
    except (
        AttributeError,
        EtcdException,
        ValueError,
        SyntaxError,
        TypeError
    ) as ex:
        raise ex


def get_integration_ids():
    try:
        integration_ids = []
        clusters_etcd = read_key('/clusters')
        for cluster in clusters_etcd.leaves:
            cluster_key_contents = cluster.key.split('/')
            if len(cluster_key_contents) == 3:
                integration_ids.append(cluster_key_contents[2])
        return integration_ids
    except EtcdKeyNotFound:
        return []
    except (
        AttributeError,
        EtcdException,
        ValueError,
        SyntaxError,
        TypeError
    ) as ex:
        raise ex


def get_event_ids():
    event_ids = []
    try:
        etcd_events = read_key(
            '/messages/events'
        )
    except EtcdKeyNotFound:
        return event_ids
    except (AttributeError, EtcdException) as ex:
        raise ex
    for event in etcd_events.leaves:
        event_parts = event.key.split('/')
        if len(event_parts) >= 4:
            event_ids.append(event_parts[3])
    return event_ids


def get_alert_types():
    return AlertTypes().load()


def get_alert(alert_id):
    return Alert(alert_id).load()


def get_alerts():
    # TODO: Revert to using object#load instead of etcd read
    # once the issue in object#load is found and fixed.
    alerts_arr = []
    try:
        alerts = read('/alerting/alerts')
    except EtcdKeyNotFound:
        return alerts_arr
    except (EtcdException, AttributeError) as ex:
        raise ex
    for alert_id, alert in alerts.iteritems():
        alerts_arr.append(AlertUtils().to_obj(alert))
    return alerts_arr


def get_entity_alert_path(entity_type, **kwargs):
    # TODO(Anmol Babu): Explore the possibility of getting the below info
    # from definitions instead of hard coding here and if that works
    # Implement it in all other above functions where etcd path is hardcoded.
    entity_alert_path_map = {
        alerting_consts.CLUSTER: '/alerting/clusters/$integration_id',
        alerting_consts.NODE: '/alerting/nodes/$node_id'
    }
    return Template(
        entity_alert_path_map.get(
            entity_type,
            alerting_consts.NOT_AVAILABLE
        )
    ).substitute(kwargs)


def get_entity_alerts(entity_type, **kwargs):
    alerts = []
    try:
        alert_path = get_entity_alert_path(entity_type, **kwargs)
    except (KeyError, TypeError) as ex:
        raise ex
    try:
        entity_alerts = read(
            alert_path
        )
    except EtcdKeyNotFound:
        return alerts
    except (AttributeError, EtcdException) as ex:
        raise ex
    for alert_id, alert in entity_alerts.iteritems():
        alerts.append(alert)
    return alerts

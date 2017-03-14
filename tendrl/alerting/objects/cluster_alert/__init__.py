from tendrl.alerting.objects \
    import AlertingBaseObject
from tendrl.alerting.objects.alert import Alert
from tendrl.commons.etcdobj import EtcdObj


class ClusterAlert(Alert, AlertingBaseObject):
    def __init__(
        self,
        alert_id=None,
        node_id=None,
        time_stamp=None,
        resource=None,
        current_value=None,
        tags=None,
        alert_type=None,
        severity=None,
        significance=None,
        ackedby=None,
        acked=None,
        ack_comment=[],
        acked_at=None,
        pid=None,
        source=None,
        *args,
        **kwargs
    ):
        super(ClusterAlert, self).__init__(
            alert_id,
            node_id,
            time_stamp,
            resource,
            current_value,
            tags,
            alert_type,
            severity,
            significance,
            ackedby,
            acked,
            ack_comment,
            acked_at,
            pid,
            source,
            *args,
            **kwargs
        )
        self.value = 'alerting/clusters/%s/%s' % (
            self.tags['cluster_id'],
            alert_id
        )
        self._etcd_cls = _ClusterAlert


class _ClusterAlert(EtcdObj):
    __name__ = 'alerting/clusters/%s/%s'
    _tendrl_cls = ClusterAlert

    def render(self):
        self.__name__ = self.__name__ % (
            self.tags['cluster_id'],
            self.alert_id
        )
        return super(_ClusterAlert, self).render()

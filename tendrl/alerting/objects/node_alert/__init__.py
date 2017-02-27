from tendrl.alerting.objects \
    import AlertingBaseObject
from tendrl.alerting.objects.alert import Alert
from tendrl.commons.etcdobj import EtcdObj


class NodeAlert(Alert, AlertingBaseObject):
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
        pid=None,
        source=None,
        *args,
        **kwargs
    ):
        super(NodeAlert, self).__init__(
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
            pid,
            source,
            *args,
            **kwargs
        )
        self.value = 'alerting/nodes/%s/%s' % (
            node_id,
            alert_id
        )
        self._etcd_cls = _NodeAlert


class _NodeAlert(EtcdObj):
    __name__ = 'alerting/nodes/%s/%s'
    _tendrl_cls = NodeAlert

    def render(self):
        self.__name__ = self.__name__ % (
            self.node_id,
            self.alert_id
        )
        return super(_NodeAlert, self).render()

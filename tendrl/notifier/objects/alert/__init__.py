from tendrl.commons import objects


class Alert(objects.BaseObject):
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
        delivery=None,
        *args,
        **kwargs
    ):
        super(Alert, self).__init__(*args, **kwargs)
        self.alert_id = alert_id
        self.node_id = node_id
        self.time_stamp = time_stamp
        self.resource = resource
        self.current_value = current_value
        self.tags = tags
        self.alert_type = alert_type
        self.severity = severity
        self.significance = significance
        self.ackedby = ackedby
        self.acked = acked
        self.ack_comment = ack_comment
        self.acked_at = acked_at
        self.pid = pid
        self.source = source
        self.delivery = delivery
        self.value = 'alerting/alerts/{0}'
        self.list = 'alerting/alerts'

    def render(self):
        self.value = self.value.format(self.alert_id)
        return super(Alert, self).render()

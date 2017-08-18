from tendrl.commons import TendrlNS


class AlertingNS(TendrlNS):
    def __init__(
        self,
        ns_name='alerting',
        ns_src='tendrl.alerting'
    ):
        super(AlertingNS, self).__init__(ns_name, ns_src)

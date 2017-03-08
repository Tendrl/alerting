try:
    from gevent import monkey
except ImportError:
    pass
else:
    monkey.patch_all()

from tendrl.commons import etcdobj
from tendrl.commons import log
from tendrl.commons import CommonNS

from tendrl.alerting.objects.alert import Alert
from tendrl.alerting.objects.alert_types import AlertTypes
from tendrl.alerting.objects.config import Config
from tendrl.alerting.objects.definition import Definition
from tendrl.alerting.objects.node_context import NodeContext
from tendrl.alerting.objects.tendrl_context import TendrlContext


class AlertingNS(CommonNS):
    def __init__(self):

        # Create the "tendrl_ns.alerting" namespace
        self.to_str = "tendrl.alerting"
        super(AlertingNS, self).__init__()


AlertingNS()

from tendrl.commons import TendrlNS


class NotifierNS(TendrlNS):
    def __init__(
        self,
        ns_name='notifier',
        ns_src='tendrl.notifier'
    ):
        super(NotifierNS, self).__init__(ns_name, ns_src)

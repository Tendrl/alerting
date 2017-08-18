from tendrl.commons import config as cmn_config
from tendrl.commons import objects


class Config(objects.BaseObject):
    internal = True

    def __init__(self, config=None, *args, **kwargs):
        self._defs = {}
        super(Config, self).__init__(*args, **kwargs)

        if config is None:
            config = cmn_config.load_config(
                'alerting',
                "/etc/tendrl/alerting/alerting.conf.yaml"
            )
        self.data = config
        self.value = '_NS/alerting/config'

import json

from acss_core.simple_service import SimpleService
from acss_core.logger import logging
from adapter.petra.utils import set_service_by_env_values

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class ConfigToFileService(SimpleService):
    def __init__(self, name, read):
        super().__init__(name, read)

    def reconfig_event(self, msg):
        with open(f"/tmp/{self.name}.json", "w") as f:
            json.dump(msg, f)

    def proposal(self, params):
        pass


if __name__ == '__main__':
    name, read, mode = set_service_by_env_values()
    agent = ConfigToFileService(name,  None)
    agent.init_local()

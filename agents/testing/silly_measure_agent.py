
import numpy as np

from adapter.petra.TineSimAdapter import TineSimReader
from acss_core.simple_service import SimpleService
from acss_core.logger import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class SillyMeasureAgent(SimpleService):
    def __init__(self, name, read):
        super().__init__(name, read=read)

    def info(self):
        return "This Agent just return some data and does not set sth."

    def reconfig_event(self, msg):
        pass

    def proposal(self, params):
        _logger.debug(f"send some data...")
        return ({'some_data': np.array([i for i in range(3)])}, 1, "error message")


if __name__ == '__main__':
    agent = SillyMeasureAgent('silly_measure_agent',  TineSimReader.create_for_petra())
    agent.init_local()

import at

import numpy as np

from adapter.petra.TineSimAdapter import TineSimAdapter
from acss_core.messages.agent_result_message import AgentResultMessage
from acss_core.simple_service import SimpleService
from acss_core.logger import init_logger
from acss_core.simulation.physics_based.p3_elements_v24_c4l import *

_logger = init_logger(__name__)


class OpticAgent(SimpleService):
    def __init__(self, name, read, lat):
        super().__init__(name, read=read)
        self.lat = lat
        self.parameters = {}
        opt = at.linopt(ring, refpts=np.array(range(len(ring))), get_chrom=True)
        self.parameters['tune'] = opt[1]
        self.parameters['chrom'] = opt[2]
        tws = opt[3]  # optics functions
        self.s = tws.s_pos
        self.beta_x = tws.beta[:, 0]
        self.beta_y = tws.beta[:, 1]
        self.Dx = tws.dispersion[:, 0]
        self.Dy = tws.dispersion[:, 1]

    def proposal(self, params):
        self.publish_result(AgentResultMessage(error_code=0, error_message='', result={'s': self.s, 'beta_x': self.beta_x, 'beta_y': self.beta_y, 'Dx': self.Dx, 'Dy': self.Dy}))


if __name__ == '__main__':
    agent = OpticAgent('optic_agent', TineSimAdapter(), ring)
    agent.init_local()

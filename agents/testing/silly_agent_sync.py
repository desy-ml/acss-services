from acss_core.simple_service import SimpleService
from acss_core.logger import logging
from adapter.petra.PetraMachineAdapter import PetraMachineAdapter
from adapter.petra.TineSimAdapter import TineSimReader

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class SillyAgent(SimpleService):
    def __init__(self, name, read, simulations):
        super().__init__(name, read, simulations=simulations)
        self.factor = 2.0
        self.machine_adapter = PetraMachineAdapter.create_for_sync_agent(self)  # set sync write

    def info(self):
        return "Agent reads horizontal corrector currents and multiply a factor to each current. The factor can be reconfigured."

    def reconfig_event(self, msg):
        factor = msg.get('factor')
        if factor is None:
            _logger.error("reconfig message doesn't have 'factor' as a key.")
        else:
            _logger.debug(f"set new factor to: {factor}")
            self.factor = factor

    def proposal(self, params):
        _logger.debug(f"use factor: {self.factor}")
        names = self.machine_adapter.get_hcor_device_names()
        self.machine_adapter.set_hcors(names, [1.0 for _ in names])
        for i in range(3):
            _logger.debug(f"ITERATION NO: {i}")
            hcors = self.machine_adapter.get_hcors(names=self.machine_adapter.get_hcor_device_names(), is_group_call=True)

            self.machine_adapter.set_hcors(self.machine_adapter.get_hcor_device_names(), [val * self.factor for val in hcors])


if __name__ == '__main__':
    agent = SillyAgent('silly_agent',  read=TineSimReader.create_for_petra(), simulations=["PetraOrbitSimulation"])
    agent.init_local()

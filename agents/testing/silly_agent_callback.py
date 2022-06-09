from acss_core.simple_service import SimpleService
from acss_core.logger import logging
from adapter.petra.PetraMachineAdapter import PetraMachineAdapter
from adapter.petra.TineSimAdapter import TineSimReader

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class SillyAgentCallback(SimpleService):
    def __init__(self, name, read):
        super().__init__(name, read)
        self.factor = 1.0
        self.machine_adapter = PetraMachineAdapter.create_for_agent(self)
        self.count = 0

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

        hcors = self.machine_adapter.get_hcors(names=self.machine_adapter.get_hcor_device_names(), is_group_call=True)
        self.init_hcor_meadian = sum(hcors) / len(hcors)

        def callback():
            self.count += 1
            _logger.debug("Callback is called")
            hcor = self.machine_adapter.get_hcors(names=self.machine_adapter.get_hcor_device_names(), is_group_call=True)
            if self.count > self.max_runs:
                _logger.debug("stop calling callback func.")
                return
            self.machine_adapter.set_hcors(self.machine_adapter.get_hcor_device_names(), [val/2.0 for val in hcor], callback=callback)

        self.machine_adapter.set_hcors(self.machine_adapter.get_hcor_device_names(), [val/2.0 for val in hcors], callback=callback)


if __name__ == '__main__':
    agent = SillyAgentCallback('silly_agent_callback',  read=TineSimReader.create_for_petra())
    agent.init_local()

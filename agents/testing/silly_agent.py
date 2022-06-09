from acss_core.simple_service import SimpleService
from acss_core.logger import logging
from adapter.petra.PetraMachineAdapter import PetraMachineAdapter
from adapter.petra.TineSimAdapter import TineSimReader

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class SillyAgent(SimpleService):
    def __init__(self, name, read):
        super().__init__(name, read)
        self.factor = 1.0
        self.machine_adapter = PetraMachineAdapter.create_for_agent(self)

    def info(self):
        return "Agent reads horizontal corrector currents and multiply a factor to each current. The factor can be reconfigured."

    def reconfig_event(self, msg):
        factor = msg.get('factor')

        if factor is None:
            _logger.error("reconfig message doesn't have 'factor' as a key.")
        else:
            _logger.debug(f"set new factor to: {factor}")
            self.factor = factor

        exclude_cor = msg.get('exclude_cor')
        if exclude_cor != None:
            self.machine_adapter.ignore_hcors(exclude_cor)
            self.machine_adapter.ignore_vcors(exclude_cor)

    def proposal(self, params):
        _logger.debug(f"use factor: {self.factor}")

        hcors = self.machine_adapter.get_hcors(names=self.machine_adapter.get_hcor_device_names(), is_group_call=True)
        vcors = self.machine_adapter.get_vcors(names=self.machine_adapter.get_vcor_device_names(), is_group_call=True)
        self.machine_adapter.set_hcors(self.machine_adapter.get_hcor_device_names(), [val * self.factor for val in hcors])
        self.machine_adapter.set_vcors(self.machine_adapter.get_vcor_device_names(), [val * self.factor for val in vcors])

        self.machine_adapter.commit()


if __name__ == '__main__':
    agent = SillyAgent('silly_agent',  read=TineSimReader.create_for_petra())
    agent.init_local()

from adapter.petra.TineSimAdapter import TineSimWriter
from adapter.petra.TineSimAdapter import TineSimReader
from adapter.petra.PetraMachineAdapter import PetraMachineAdapter
from acss_core.simulation.SimulationService import SimulationService
from acss_core.logger import init_logger

_logger = init_logger(__name__)


class SillySimulation(SimulationService):
    def __init__(self, name, write, read):

        super().__init__(name, write=write, read=read)
        self.adapter = PetraMachineAdapter(write=self.write, read=self.read)
        self.hcor_names = self.adapter.get_hcor_device_names()
        self.vcor_names = self.adapter.get_vcor_device_names()

    def simulate(self):
        hcors = self.adapter.get_hcors(self.hcor_names)
        vcors = self.adapter.get_vcors(self.vcor_names)
        self.adapter.set_bpms()


if __name__ == "__main__":
    sim = SillySimulation('silly_sim', write=TineSimWriter.create_for_petra(), read=TineSimReader.create_for_petra())
    sim.init_local()

import time

from adapter.petra.TineSimAdapter import TineSimWriter
from adapter.petra.TineSimAdapter import TineSimReader
from adapter.petra.PetraMachineAdapter import PetraMachineAdapter
from optics_sim import OpticsSimulation
from acss_core.simulation.SimulationService import SimulationService
from acss_core.logger import init_logger

_logger = init_logger(__name__)


class PetraOrbitSimulation(SimulationService):
    def __init__(self, name, optic: str, write, read):

        super().__init__(name, write=write, read=read)
        self.optic_sim = OpticsSimulation(PetraMachineAdapter.create_for_simulation(), optic)

    def simulate(self):
        start = time.time()
        self.optic_sim.simulate()
        end = time.time()
        t = end - start
        _logger.debug(f"simulation takes: {t} secs.")


if __name__ == "__main__":
    sim = PetraOrbitSimulation('petra_III_sim', 'v24', write=TineSimWriter.create_for_petra(), read=TineSimReader.create_for_petra())
    sim.init_local()

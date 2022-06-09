import sys

from adapter.petra.TineSimAdapter import TineSimWriter
from adapter.petra.TineSimAdapter import TineSimReader
from adapter.petra.PetraMachineAdapter import PetraMachineAdapter
from acss_core.simulation.TimedSimService import TimedSimService
from acss_core.logger import init_logger

_logger = init_logger(__name__)


class TimedSillySimulation(TimedSimService):
    def __init__(self, name, write, read, time):

        super().__init__(name, write=write, read=read, time=time)
        self.adapter = PetraMachineAdapter(write=self.write, read=self.read)
        names = self.adapter.get_hcor_device_names()
        vals = self.adapter.get_hcors(names)
        vals = [1.0 for val in vals]
        self.adapter.set_hcors(names, vals)

    def simulate(self):
        names = self.adapter.get_hcor_device_names()
        vals = self.adapter.get_hcors(names)
        vals = [val*2 for val in vals]
        self.adapter.set_hcors(names, vals)


if __name__ == "__main__":
    sim = TimedSillySimulation('timed_silly_sim', write=TineSimWriter.create_for_petra(), read=TineSimReader.create_for_petra(), time=1.0)
    sim.init_local()

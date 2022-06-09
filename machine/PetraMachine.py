from adapter.petra.TineAdapter import TineReader, TineWriter
from acss_core.simulation.MachineService import MachineService

if __name__ == "__main__":
    machine = MachineService('petra_III_machine', write=TineWriter(), read=TineReader())
    machine.init_local()

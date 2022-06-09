from adapter.petra.TineSimAdapter import TineSimWriter, TineSimReader
from acss_core.simulation.MachineService import MachineService

if __name__ == "__main__":
    machine = MachineService('petra_III_machine', write=TineSimWriter.create_for_petra(), read=TineSimReader.create_for_petra())
    machine.init_local()

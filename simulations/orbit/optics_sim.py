import numpy as np

import at
from at import elements

from adapter.petra.PetraMachineAdapter import PetraMachineAdapter
from acss_core.logger import logging
from acss_core.simulation.utils import load_at_optic

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class OpticsSimulation():
    def __init__(self, machine_adapter: PetraMachineAdapter, optic='v24') -> None:
        _logger.debug(f"Load optic model {optic}.")
        self.optic = load_at_optic(optic)
        self.lat = at.Lattice(self.optic, energy=6.e9)
        self.lat.radiation_off()
        self.opt = self.lat.linopt(refpts=range(len(self.optic)), get_chrom=True)
        self.lengths = self.get_bpm_lengths()
        bpms, cors = self._get_bpm_cor_name_to_id()
        self.bpm_names_to_id = bpms
        self.cor_names_to_id = cors
        self.machine_adapter = machine_adapter

        self.bpm_names = self.machine_adapter.get_bpm_device_names()
        self.hcor_names = self.machine_adapter.get_hcor_device_names()
        self.vcor_names = self.machine_adapter.get_vcor_device_names()

    def get_bpm_lengths(self):
        name_length_pairs = []
        total_length = 0.0
        for r in self.optic:
            if r.__class__ == elements.Monitor:
                name_length_pairs.append((r.FamName, total_length))
            total_length += r.Length
        return name_length_pairs

    def _get_bpm_cor_name_to_id(self):
        e_id = 0
        bpms = {}
        cors = {}

        for r in self.optic:
            if r.__class__ == elements.Monitor:
                bpms[r.FamName] = e_id
            if r.__class__ == elements.Corrector:
                cors[r.FamName] = e_id
            e_id += 1
        return bpms, cors

    def _is_hcor(self, name):
        return name.startswith('PKH_')

    def _is_vcor(self, name):
        return name.startswith('PKV_')

    def set_cors(self, names, vals):
        ignored_names = []
        for name, val in zip(names, vals):
            if self._is_hcor(name):
                self.lat.get_elements(name)[0].KickAngle = [val, 0.0]
            elif self._is_vcor(name):
                self.lat.get_elements(name)[0].KickAngle = [0.0, val]
            else:
                ignored_names.append(name)
                self.lat.get_elements(name)[0].KickAngle = [0.0, 0.0]
        _logger.warning(f"Set {','.join(ignored_names)} to x=0 y=0. Only vertical an horizontal correctors can be set.")

    def get_bpms(self, bpm_names):
        ids = []
        names = []
        for name in bpm_names:
            id = self.bpm_names_to_id.get(name)
            if id == None:
                _logger.warning(f"BPM name '{name}' is unknown")
                continue
            ids.append(id)
            names.append(name)

        orb = self.lat.find_orbit4(refpts=ids)
        x = orb[1][:, 0]
        y = orb[1][:, 3]
        return names, np.array([x, y]).T

    def simulate(self):
        _logger.debug("update simulation...")
        self.set_cors(self.hcor_names, self.machine_adapter.get_hcors(self.hcor_names))
        self.set_cors(self.vcor_names, self.machine_adapter.get_vcors(self.vcor_names))

        names, bpm_coord = self.get_bpms(self.bpm_names)

        # if simulation returns nan set bpms to zero and total current to 0.0
        if all(np.isnan(bpm_coord.reshape(-1))):
            _logger.warning("Simulation return 'nan' for bmp coordinates. Set all bpms to x=0.0 y=0.0 and I_total=0.0")
            bpm_coord = np.zeros(bpm_coord.shape)
            self.machine_adapter.set_machine_params(['I_total'], [0.0])
        _logger.debug(f"bpm corrds: {bpm_coord}")
        self.machine_adapter.set_bpms(names, bpm_coord)


if __name__ == "__main__":
    adapter = OpticsSimulation(machine_adapter=PetraMachineAdapter())
    print(adapter.cor_names_to_id)

import numpy as np
import time
import csv
from typing import Dict, Tuple

from adapter.petra.bpm_fit import correct_bpm
from acss_core.logger import logging


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class BPM:
    def __init__(self, bpm_type, path_to_calibr_files):
        bpm_file = bpm_type+'.par'
        calibr_file = path_to_calibr_files / "common" / bpm_file
        colmat = np.loadtxt(calibr_file)
        self.cx = [r[0] for r in colmat]
        self.cy = [r[1] for r in colmat]

    def correct_x(self, x):
        x_ = 0.0
        for i in range(len(self.cx)):
            x_ += self.cx[i] * x**i
        return x_

    def correct_y(self, y):
        y_ = 0.0
        for i in range(len(self.cy)):
            y_ += self.cy[i] * y**i
        return y_


class BPMAdapter:
    def __init__(self, read, path_to_calibr_files, path_to_constants_file):
        self.path_to_calibr_files = path_to_calibr_files
        self.read = read

        self.bpm_names = self.get_bpm_names()
        self.bpm_names = [p.upper() for p in self.bpm_names]

        # Constants to calculate the bpm beam current
        self.constants: Dict[str, Tuple[int, int]] = {}
        if path_to_constants_file:
            with open(path_to_constants_file) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.constants[row['name']] = (row['c0'], row['c1'])
            _logger.debug(f"Constants loaded: length {len(self.constants)}")

        with open(self.path_to_calibr_files / "BPMsettings.csv") as csvfile:
            reader = csv.DictReader(csvfile)
            devices = []
            bpm_types = []
            for row in reader:
                devices.append(row['Device'])
                bpm_types.append(row['BPMTYP'])

        self.bpm_info = {device: bpm_type for device, bpm_type in zip(devices, bpm_types)}

        self.load_calibration(set(bpm_types))

    def get_bpm_names(self):
        return self.read("/PETRA/LBRENV", "BPM_SWR_13", "DEVICES")

    def load_calibration(self, bpm_types):
        self.PQ = {}

        for bpm_t in bpm_types:
            bpm = BPM(bpm_t, path_to_calibr_files=self.path_to_calibr_files)
            self.PQ[bpm_t] = (bpm.cx, bpm.cy)

        return

    def get_names(self, start_with):
        start_i = self.bpm_names.index(start_with)
        names = self.bpm_names[start_i:]+self.bpm_names[:start_i]  # realign names to start from start_with
        return start_i, names

    def _read(self, n_turns=10, start_with="BPM_SOR_61", is_corrected=True):
        start_i, names = self.get_names(start_with)

        res = np.zeros((len(names), n_turns, 2))

        for i, name in enumerate(names):
            for k in range(3):
                try:
                    res[i, :, 0] = np.array(self.read('/PETRA/LBRENV', name, 'DD_X', size=n_turns, mode='SYNC'))
                    res[i, :, 1] = np.array(self.read('/PETRA/LBRENV', name, 'DD_Y', size=n_turns, mode='SYNC'))
                    break
                except Exception as e:
                    print(f'attempt {k}:', e)
                    time.sleep(1)

        if is_corrected:
            res = self.correct(res, names)
        return res, names

    def read_sum(self, n_turns=10, start_with="BPM_SOR_61", is_corrected=True):
        start_i, names = self.get_names(start_with)

        res = np.zeros((len(names), n_turns, 1))

        for i, name in enumerate(names):
            for k in range(3):
                try:
                    res[i, :, 0] = np.array(self.read('/PETRA/LBRENV', name, 'DD_SUM', size=n_turns, mode='SYNC'))
                    break
                except Exception as e:
                    print(f'attempt {k}:', e)
                    time.sleep(1)

        return res, names

    def correct(self, res, names, scale=1e-6):
        res *= scale
        print(res.shape)
        res_cor = np.empty_like(res)
        for i, name in enumerate(names):
            PQ = self.PQ[self.bpm_info[name]]
            x, y = correct_bpm(res[i, :, 0], res[i, :, 1], PQ[0], PQ[1])
            res_cor[i, :, 0] = x
            res_cor[i, :, 1] = y
        return res_cor/scale

    def get_offsets(self, start_with="BPM_SOR_61"):
        name0 = self.bpm_names[0]
        x = np.array(self.read('/PETRA/REFORBIT', name0, 'CORR_X_BBA'))
        y = np.array(self.read('/PETRA/REFORBIT', name0, 'CORR_Y_BBA'))
        res = np.vstack((x, y)).T
        res = res[:-2]

        start_i, names = self.get_names(start_with)
        return np.roll(res, -start_i, axis=0), names

    def get_offsets_go(self, start_with="BPM_SOR_61"):
        name0 = self.bpm_names[0]
        x = np.array(self.read('/PETRA/REFORBIT', name0, 'CORR_X_BBAGO'))
        y = np.array(self.read('/PETRA/REFORBIT', name0, 'CORR_Y_BBAGO'))
        res = np.vstack((x, y)).T
        res = res[:-2]
        start_i, names = self.get_names(start_with)
        return np.roll(res, -start_i, axis=0), names

    def get_orbit(self, start_with="BPM_SOR_61"):
        """ In meter

        :param start_with: _description_, defaults to "BPM_SOR_61"
        :type start_with: str, optional
        :return: _description_
        :rtype: _type_
        """
        name0 = self.bpm_names[0]
        x = np.array(self.read('/PETRA/REFORBIT', name0, 'SA_X'))
        y = np.array(self.read('/PETRA/REFORBIT', name0, 'SA_Y'))
        res = np.vstack((x, y)).T
        res = res[:-2]
        start_i, names = self.get_names(start_with)
        return np.roll(res, -start_i, axis=0), names

    def get_bpm_beam_currents(self, n_turns=10):
        if self.c0 == None or self.c1 == None:
            _logger.error(f"Constants c0, c1 are not set. c0={self.c0} and c1={self.c1}")
            return None, None
        sum_signal, names = self.read_sum(n_turns=n_turns)
        n_bpms = len(names)
        currents = np.zeros([n_bpms, n_turns])

        for i, name in enumerate(names):
            c0, c1 = self.constants.get(name)
            currents[i] = c0 + c1 * sum_signal[i, :, 0]
        return currents, names


if __name__ == "__main__":
    adapter = BPMAdapter()
    data, names = adapter.get_orbit()

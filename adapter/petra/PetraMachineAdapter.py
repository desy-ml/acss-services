from pathlib import Path

from typing import List, Tuple, Optional, Dict, Any

import numpy as np

from adapter.petra.BPMAdapter import BPMAdapter
from acss_core.logger import init_logger
from adapter.petra.simulation_db_types import TABLE_NAMES
from acss_core.simple_service import SimpleService
from acss_core.config import PATH_TO_ACSS_SERVICES_ROOT

_logger = init_logger(__name__)


def find_index_in_list(l: List[str], elements: List[str]) -> Tuple[str, Optional[int]]:
    """[summary]
    Iterates over elements and yield a Tuple with element, True and index in list , if the current element is l. If not is returns (None, False, None)
        Example:
            find_index_in_list(['a','c','b'], ['a', 'b', 'c', 'd'])
            (('a', 0), ('b', 2), ('c', 1), ('d', None))
    :param l: List in which the elements will be searched. Have to be a subset of elements
    :type l: List[str]
    :param elements: elements that should be found.
    :type elements: List[str]
    :raises ValueError: If l is not a subset of elements
    :return: Yields a tuple at each step. The first element is the name of the element. The second element is a index in elements which is None if the current name is not in l.
    :rtype: Tuple[str, bool, Optional[int]]
    :yield: Yields a tuple at each step. The first element is the element which should be found, . The second element is a index in elements which is None if the current name is not in l.
    :rtype: Iterator[str, Optional[int]]]
    """
    names_indices = {k: v for v, k in enumerate(l)}
    found_idx_count = 0
    for name in elements:
        found_idx = names_indices.get(name)
        if found_idx != None:
            found_idx_count += 1
            yield name, found_idx
        else:
            yield name, None
    if found_idx_count != len(l):
        raise ValueError("l is not a subset of elements")


class PetraMachineAdapter():
    def __init__(self, write, read, energy=6.063):

        rpath_to_bpm_calibr_files = Path(PATH_TO_ACSS_SERVICES_ROOT) / Path("adapter/petra/config")
        path_to_bpm_calibr_files = rpath_to_bpm_calibr_files / "bpm_settings"
        filepath_to_constants_file = rpath_to_bpm_calibr_files / "constants.csv"
        self.bpm_adapter = BPMAdapter(read=read, path_to_calibr_files=path_to_bpm_calibr_files, path_to_constants_file=filepath_to_constants_file)
        self.debug_mode = False
        self.energy = energy
        self.get_property = 'Strength.Soll'
        self.read = read
        self.write = write
        self._ignore_hcors = {}
        self._ignore_vcors = {}

    @classmethod
    def create_for_agent(cls, agent: SimpleService, energy=6.063):
        return cls(write=agent.write, read=agent.read, energy=energy)

    @classmethod
    def create_for_simulation(cls, energy=6.063):
        from .TineSimAdapter import TineSimReader, TineSimWriter, PetraSimDatabase
        return cls(write=TineSimWriter(PetraSimDatabase()), read=TineSimReader(PetraSimDatabase()), energy=energy)

    def get_bpm_device_names(self):
        return self.bpm_adapter.get_bpm_names()

    def get_values_by_group(self, group: str):
        group_res = self.read("/PETRA/Cms.PsGroup", group, self.get_property, size=len(self.get_hcor_device_names()) if 'PeCorH' else len(self.get_vcor_device_names()))
        print(f'read {group}: {len(group_res)} values')
        return group_res

    def get_value(self, name):
        return self.read("/PETRA/Cms.MagnetPs", name, self.get_property)

    def get_values_by_names(self, names):
        result = []
        for name in names:
            try:
                res = self.get_value(name)
                result.append(res)
            except Exception as e:
                print(name, e)
        return result

    def ignore_hcors(self, names: List[str]):
        all_hcor_names = self.get_hcor_device_names()
        self._ignore_hcors = set()
        for name in names:
            for hcor_name in all_hcor_names:
                if hcor_name.startswith(name):
                    self._ignore_hcors.add(hcor_name)

    def ignore_vcors(self, names: List[str]):
        all_vcor_names = self.get_vcor_device_names()
        self._ignore_vcors = set()
        for name in names:
            for vcor_name in all_vcor_names:
                if vcor_name.startswith(name):
                    self._ignore_vcors.add(vcor_name)

    def get_hcor_device_names(self) -> List[str]:
        device = 'PeCorH'
        cor_group_size = self.read("/PETRA/Cms.PsGroup", device, "GroupSize")
        names = self.read("/PETRA/Cms.PsGroup", device, "GroupDevices", size=cor_group_size)
        return names

    def get_vcor_device_names(self):
        device = 'PeCorV'
        cor_group_size = self.read("/PETRA/Cms.PsGroup", device, "GroupSize")
        names = self.read("/PETRA/Cms.PsGroup", device, "GroupDevices", size=cor_group_size)
        return names

    def _sort_by_hash_table(self, names: List[str], hash: Dict[str, int]):
        """[summary]
        Sorts a list of names by a index hash table.
        :param names: List of names in uppercase. Note: The names have to be in the hash table
        :type names: List[str]
        :param hash: name to idx hash table
        :type hash: Dict[str, int]
        :raises KeyError: If names are not in the group
        :return: A list of indices
        :rtype: [type]
        """
        indices = []
        for name in names:
            found_idx = hash.get(name)
            if found_idx == None:
                raise KeyError(f"name {name} is not in {hash} group.")
            indices.append(found_idx)
        return indices

    def get_cor_parallel(self, names: List[str], group='PeCorH') -> List[float]:
        all_corr_names = self.get_hcor_device_names() if group == 'PeCorH' else self.get_vcor_device_names()
        indices = self._sort_by_hash_table(names=names, hash={name: idx for idx, name in enumerate(all_corr_names)})

        currents = self.get_values_by_group(group)
        filtered_currents = [currents[idx] for idx in indices]
        print(f"names: len {len(names)} curr len {len(filtered_currents)}")
        return filtered_currents

    def get_cor_serial(self, names: List[str]) -> List[float]:
        currents = []
        for name in names:
            currents.append(self.get_value(name))
        return currents

    def get_hcors(self, names: List[str], is_group_call=True) -> List[float]:
        strengths = []
        if is_group_call:
            strengths = self.get_cor_parallel(names, group='PeCorH')
        else:
            strengths = self.get_cor_serial(names)

        return strengths

    def get_vcors(self, names: List[str], is_group_call=True) -> List[float]:
        strengths = []
        if is_group_call:
            strengths = self.get_cor_parallel(names, group='PeCorV')
        else:
            strengths = self.get_cor_serial(names)
        return strengths

    def set_all_cors_random(self, min, max):
        self.write("/PETRA/Cms.PsGroup", "CORS", "Strength.Random", input=(min, max))

    def set_group_values(self, name, values):
        if self.debug_mode:
            print(f"Debug Mode set_group_value: name: {name} values: {values}")
        else:
            self.write("/PETRA/Cms.PsGroup", name, self.get_property,
                       input=values,
                       format='FLOAT',
                       size=len(values),
                       mode='WRITE')
        return

    def set_value(self, name, value):
        if self.debug_mode:
            print(f"Debug Mode set_value: name: {name} value: {value}")
        else:
            self.write(f"/PETRA/Cms.MagnetPs", name, self.get_property, index=value)

    def set_cor_parallel(self, names: List[str], in_strengths: List[float], current_offsets: List[float] = None, group='PeCorV'):
        cor_names = self.get_vcor_device_names() if group == 'PeCorV' else self.get_hcor_device_names()
        print(f"names: len {len(names)} current len {len(in_strengths)}")
        strenghts_of_all_magnets = []
        for name, found_idx in find_index_in_list(l=names, elements=cor_names):
            if found_idx is not None and not name.startswith(('PKPDA', 'PKPDD')) and name not in self._ignore_hcors and name not in self._ignore_vcors:
                strenghts_of_all_magnets.append(in_strengths[found_idx])
                #print(f"name: {name}, current: {in_strengths[found_idx]}. use new value")
            else:  # magnet is not set
                curr = self.get_value(name)
                strenghts_of_all_magnets.append(curr)  # use current value of magnet
                print(f"name: {name}, current: {curr}. use old value")
        self.set_group_values(group, strenghts_of_all_magnets)

    def set_cor_serial(self, names: List[str], in_strengths: List[float], current_offsets: List[float] = None):

        for name, current in zip(names, in_strengths):
            print(f"name: {name}, current: {current}.")
            self.set_value(name, current)

    def set_vcors(self, names: List[str], in_strengths: List[float], current_offsets: List[float] = None, is_group_call=True):
        if is_group_call:
            self.set_cor_parallel(names, in_strengths, current_offsets=current_offsets, group='PeCorV')
        else:
            self.set_cor_serial(names, in_strengths)

    def set_hcors(self, names: List[str], in_strengths: List[float], current_offsets: List[float] = None, is_group_call=True):
        if is_group_call:
            self.set_cor_parallel(names, in_strengths, current_offsets=current_offsets, group='PeCorH')
        else:
            self.set_cor_serial(names, in_strengths)

    def get_bpms(self) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        data, names = self.bpm_adapter.get_orbit(start_with='BPM_SWR_13')
        x = data[:, 0]
        y = data[:, 1]
        return x, y, names

    def set_machine_params(self, params: List[str], values: List[Any]):
        self.write("/SIMULATION/PETRA/DB", TABLE_NAMES.MACHINE_PARMS, 'SQL', input=[[('param', param), ('value', val)] for param, val in zip(params, values)], where_key='param')

    def get_machine_params(self):
        col_names = ['param', 'value']
        param_values_pairs = self.read("/SIMULATION/PETRA/DB", TABLE_NAMES.MACHINE_PARMS, "SQL", col_names=col_names)
        return {param_values_pair[0]: param_values_pair[1] for param_values_pair in param_values_pairs}

    def set_twiss(self, names: List[str], mat: List[List[float]]):
        """[summary]
        :param names: Names of the diffrent twiss parameters
        :type names: List[str]
        :param mat: 2D Matrix each row contains a diffrent twiss parameter. Order [beta_x, beta_y, D_x, D_y]
        :type mat: List[List[float]]
        """
        self.write("/SIMULATION/PETRA/DB", TABLE_NAMES.TWISS, 'SQL', input=[[('name', param), ('beta_x', row[0]),
                                                                             ('beta_y', row[1]), ('D_x', row[2]), ('D_y', row[3])] for param, row in zip(names, mat)], where_key='name')

    def get_twiss(self, names: List[str]) -> List[List[float]]:
        """[summary]

        :param names: Names of the requested twiss paramters
        :type names: List[str]
        :return: 2D Matrix each row contains a diffrent twiss parameter. Order [beta_x, beta_y, D_x, D_y]
        :rtype: List[List[float]]
        """
        col_names = ['name', 'beta_x', 'beta_y', 'D_x', 'D_y']
        query_mat = self.read("/SIMULATION/PETRA/DB", TABLE_NAMES.TWISS, "SQL", col_names=col_names)
        # sort by names
        mat = [[0.0 for _ in range(4)] for _ in range(len(names))]
        idx_hash = {name: idx for idx, name in enumerate(names)}
        for row in query_mat:  # ignore last to BPM because BPM adapter is ignoring this BPMs
            name = row[0]
            found_idx = idx_hash.get(name)
            if found_idx is not None:
                mat[found_idx] = list(row[1:])

        return mat

    def set_bpms(self, names, xy_arr: np.ndarray):
        ordered_indices = self._sort_by_hash_table(names, {name: idx for idx, name in enumerate(self.get_bpm_device_names())})

        curr_x, curr_y, _ = self.get_bpms()
        new_x = list(curr_x)
        new_y = list(curr_y)
        _logger.debug(f"length new_x: {len(new_x)}, length xy_arr: {xy_arr.shape}, length names: {len(names)}")
        _logger.debug(f"ordered_indices: {ordered_indices}")
        for idx, ordered_idx in enumerate(ordered_indices):
            new_x[ordered_idx] = xy_arr[idx, :][0]
            new_y[ordered_idx] = xy_arr[idx, :][1]

        xy = [[x_val, y_val] for x_val, y_val in zip(new_x, new_y)]
        self.write("/SIMULATION/PETRA/LBRENV", "ALL", "XY", input=xy)

    def get_ddxy(self, n_turns=10) -> Tuple[np.ndarray, List[str]]:
        return self.bpm_adapter.read(n_turns=n_turns)

    def get_dd_sum(self, n_turns=10) -> Tuple[np.ndarray, List[str]]:
        return self.bpm_adapter.read_sum(n_turns=n_turns)

    def commit(self):
        self.write.commit()

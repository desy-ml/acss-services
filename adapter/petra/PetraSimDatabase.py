import pickle
import mysql
import numpy as np
from pathlib import Path

from adapter.petra.simulation_db_types import TABLE_NAMES, MAGNET_TABLE_TYPES
from acss_core.config import MYSQL_USER, MYSQL_PW, MYSQL_HOST, MYSQL_PORT
from acss_core.utils.SqlDBConnector import SqlDBConnector
from acss_core.logger import init_logger
from acss_core.config import PATH_TO_ACSS_SERVICES_ROOT


_logger = init_logger(__name__)


def load_sim_data(filename):
    with open(filename, 'rb') as fs:
        data = pickle.load(fs)
    return data


class PetraSimDatabase():

    HCOR_NAMES = load_sim_data(Path(PATH_TO_ACSS_SERVICES_ROOT) / Path('adapter/petra/config/sim-data/all-hcor-names-3-5-22'))

    VCOR_NAMES = load_sim_data(Path(PATH_TO_ACSS_SERVICES_ROOT) / Path('adapter/petra/config/sim-data/all-vcor-names-3-5-22'))

    BPM_NAMES = ['BPM_SWR_13', 'BPM_SWR_31', 'BPM_SWR_46', 'BPM_SWR_61', 'BPM_SWR_75', 'BPM_SWR_90', 'BPM_SWR_104', 'BPM_SWR_118', 'BPM_SWR_133', 'BPM_WL_140', 'BPM_WL_126', 'BPM_WL_111', 'BPM_WL_97', 'BPM_WL_82', 'BPM_WL_68', 'BPM_WL_53', 'BPM_WL_36', 'BPM_WL_30', 'BPM_WL_24', 'BPM_WL_18', 'BPM_WL_12', 'BPM_WL_6', 'BPM_WR_0', 'BPM_WR_7', 'BPM_WR_13', 'BPM_WR_19', 'BPM_WR_25', 'BPM_WR_31', 'BPM_WR_37', 'BPM_WR_56', 'BPM_WR_68', 'BPM_WR_82', 'BPM_WR_97', 'BPM_WR_111', 'BPM_WR_126', 'BPM_WR_140', 'BPM_NWL_133', 'BPM_NWL_118', 'BPM_NWL_104', 'BPM_NWL_90', 'BPM_NWL_75', 'BPM_NWL_61', 'BPM_NWL_46', 'BPM_NWL_31', 'BPM_NWL_13', 'BPM_NWL_1', 'BPM_NWR_13', 'BPM_NWR_31', 'BPM_NWR_46', 'BPM_NWR_61', 'BPM_NWR_75', 'BPM_NWR_90', 'BPM_NWR_104', 'BPM_NWR_118', 'BPM_NWR_133', 'BPM_NL_140', 'BPM_NL_126', 'BPM_NL_111', 'BPM_NL_97', 'BPM_NL_82', 'BPM_NL_68', 'BPM_NL_53', 'BPM_NL_36', 'BPM_NL_30', 'BPM_NL_24', 'BPM_NL_18', 'BPM_NL_12', 'BPM_NL_6', 'BPM_NR_0', 'BPM_NR_7', 'BPM_NR_13', 'BPM_NR_19', 'BPM_NR_25', 'BPM_NR_31', 'BPM_NR_37', 'BPM_NR_56', 'BPM_NR_62', 'BPM_NR_65', 'BPM_NR_69', 'BPM_NR_74', 'BPM_NR_79', 'BPM_NR_83', 'BPM_NR_87', 'BPM_NR_90', 'BPM_NR_96', 'BPM_NR_100', 'BPM_NR_104', 'BPM_NR_111', 'BPM_NR_126', 'BPM_NR_140', 'BPM_NOL_133', 'BPM_NOL_118', 'BPM_NOL_104', 'BPM_NOL_90', 'BPM_NOL_75', 'BPM_NOL_61', 'BPM_NOL_46', 'BPM_NOL_31', 'BPM_NOL_10', 'BPM_NOR_6', 'BPM_NOR_11', 'BPM_NOR_23', 'BPM_NOR_32', 'BPM_NOR_39', 'BPM_NOR_40', 'BPM_NOR_44', 'BPM_NOR_47', 'BPM_NOR_50', 'BPM_NOR_52', 'BPM_NOR_55', 'BPM_NOR_58', 'BPM_NOR_62', 'BPM_NOR_63', 'BPM_NOR_67', 'BPM_NOR_70', 'BPM_NOR_73', 'BPM_NOR_78', 'BPM_NOR_81', 'BPM_NOR_85', 'BPM_NOR_86', 'BPM_NOR_90', 'BPM_NOR_93', 'BPM_NOR_96',
                 'BPM_NOR_98', 'BPM_NOR_101', 'BPM_NOR_104', 'BPM_NOR_108', 'BPM_NOR_109', 'BPM_NOR_113', 'BPM_NOR_116', 'BPM_NOR_119', 'BPM_NOR_124', 'BPM_NOR_127', 'BPM_NOR_131', 'BPM_NOR_132', 'BPM_OL_152', 'BPM_OL_149', 'BPM_OL_146', 'BPM_OL_144', 'BPM_OL_141', 'BPM_OL_138', 'BPM_OL_134', 'BPM_OL_133', 'BPM_OL_129', 'BPM_OL_126', 'BPM_OL_123', 'BPM_OL_118', 'BPM_OL_115', 'BPM_OL_111', 'BPM_OL_110', 'BPM_OL_106', 'BPM_OL_103', 'BPM_OL_100', 'BPM_OL_98', 'BPM_OL_95', 'BPM_OL_92', 'BPM_OL_88', 'BPM_OL_87', 'BPM_OL_83', 'BPM_OL_80', 'BPM_OL_77', 'BPM_OL_75', 'BPM_OL_72', 'BPM_OL_69', 'BPM_OL_65', 'BPM_OL_64', 'BPM_OL_60', 'BPM_OL_58', 'BPM_OL_48', 'BPM_OL_37', 'BPM_OL_24', 'BPM_OL_13', 'BPM_OL_0', 'BPM_OR_8', 'BPM_OR_17', 'BPM_OR_22', 'BPM_OR_26', 'BPM_OR_32', 'BPM_OR_37', 'BPM_OR_44', 'BPM_OR_53', 'BPM_OR_62', 'BPM_OR_65', 'BPM_OR_69', 'BPM_OR_74', 'BPM_OR_79', 'BPM_OR_83', 'BPM_OR_87', 'BPM_OR_90', 'BPM_OR_96', 'BPM_OR_100', 'BPM_OR_104', 'BPM_OR_111', 'BPM_OR_126', 'BPM_OR_140', 'BPM_SOL_133', 'BPM_SOL_118', 'BPM_SOL_104', 'BPM_SOL_90', 'BPM_SOL_75', 'BPM_SOL_61', 'BPM_SOL_54', 'BPM_SOL_46', 'BPM_SOL_31', 'BPM_SOL_13', 'BPM_SOL_1', 'BPM_SOR_13', 'BPM_SOR_31', 'BPM_SOR_46', 'BPM_SOR_61', 'BPM_SOR_75', 'BPM_SOR_90', 'BPM_SOR_104', 'BPM_SOR_118', 'BPM_SOR_133', 'BPM_SL_140', 'BPM_SL_126', 'BPM_SL_111', 'BPM_SL_97', 'BPM_SL_82', 'BPM_SL_68', 'BPM_SL_53', 'BPM_SL_36', 'BPM_SL_24', 'BPM_SL_6', 'BPM_SR_6', 'BPM_SR_24', 'BPM_SR_36', 'BPM_SR_53', 'BPM_SR_68', 'BPM_SR_82', 'BPM_SR_97', 'BPM_SR_111', 'BPM_SR_126', 'BPM_SR_140', 'BPM_SWL_133', 'BPM_SWL_118', 'BPM_SWL_104', 'BPM_SWL_90', 'BPM_SWL_75', 'BPM_SWL_61', 'BPM_SWL_46', 'BPM_SWL_39', 'BPM_SWL_31', 'BPM_SWL_13', 'BPM_SWL_1', 'BPM_SOR_67', 'BPM_SOL_24']

    def __init__(self, sql_connector=None) -> None:
        self.db_connector = SqlDBConnector(user=MYSQL_USER, pw=MYSQL_PW, host=MYSQL_HOST, port=MYSQL_PORT, database="sim_db") if sql_connector is None else sql_connector

    def wait_until_table_created(table):
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except mysql.connector.errors.ProgrammingError as mysql_error:
                    if mysql_error.errno == mysql.connector.errorcode.ER_NO_SUCH_TABLE:
                        args[0].db_connector.wait_until_table_is_created(table)
                        return func(*args, **kwargs)
            return wrapper
        return decorator

    def create_petra_tables(self):
        self.create_magnets_table()
        self.insert_magnets_table(self.HCOR_NAMES, [MAGNET_TABLE_TYPES.HCOR for _ in range(len(self.HCOR_NAMES))], [0.0 for _ in range(len(self.HCOR_NAMES))])
        self.insert_magnets_table(self.VCOR_NAMES, [MAGNET_TABLE_TYPES.VCOR for _ in range(len(self.VCOR_NAMES))], [0.0 for _ in range(len(self.VCOR_NAMES))])

        self.create_twiss_table()
        self.insert_twiss(self.BPM_NAMES, [[0.0 for _ in range(4)] for _ in range(len(self.BPM_NAMES))])

        self.create_machine_params_table()
        param_names = ['Q_x', 'Q_y', 'I_total']
        values = [0.0, 0.0, 100.0]
        self.insert_default_machine_params(param_names, values)

        self.create_bpm_table()
        self.insert_bpms(self.BPM_NAMES)

        self.create_multi_turn_bpm_table()
        self.insert_multi_turn_bpms(self.BPM_NAMES)

    def create_magnets_table(self):
        cursor = self.db_connector.sql_con.cursor()
        cursor.execute(f"CREATE TABLE " + TABLE_NAMES.MAGNETS + " (name varchar(255) PRIMARY KEY, type varchar(255), time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, value FLOAT, pos INT)")
        self.db_connector.sql_con.commit()

    def create_twiss_table(self):
        cursor = self.db_connector.sql_con.cursor()
        cursor.execute(f"CREATE TABLE {TABLE_NAMES.TWISS} (name varchar(255) PRIMARY KEY, time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, beta_x FLOAT, beta_y FLOAT, D_x FLOAT, D_y FLOAT)")
        self.db_connector.sql_con.commit()
        cursor.close()

    def create_machine_params_table(self):
        cursor = self.db_connector.sql_con.cursor()
        cursor.execute(f"CREATE TABLE {TABLE_NAMES.MACHINE_PARMS} (param varchar(255) PRIMARY KEY, time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, value FLOAT)")
        self.db_connector.sql_con.commit()
        cursor.close()

    def create_bpm_table(self):
        cursor = self.db_connector.sql_con.cursor()
        cursor.execute(f"CREATE TABLE {TABLE_NAMES.BPM} (name varchar(255) PRIMARY KEY, time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, x FLOAT, y FLOAT, length Float, pos INT)")
        self.db_connector.sql_con.commit()
        cursor.close()

    def create_multi_turn_bpm_table(self):
        cursor = self.db_connector.sql_con.cursor()
        cursor.execute(f"CREATE TABLE {TABLE_NAMES.MULTI_TURN_BPM} (name varchar(255) PRIMARY KEY, time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, x BLOB, y BLOB, length Float, pos INT)")
        self.db_connector.sql_con.commit()
        cursor.close()

    def insert_multi_turn_bpms(self, names):
        cursor = self.db_connector.sql_con.cursor()
        x_default = np.array([0, 0, 0])
        y_default = np.array([0, 0, 0])
        query = '''INSERT INTO bpm_multiturn (name, x, y, length, pos) VALUES (%s, %s, %s, %s, %s)'''
        for idx, name in enumerate(names):
            cursor.execute(query, (name, x_default.tobytes(), y_default.tobytes(), '-1.0', idx))
        self.db_connector.sql_con.commit()
        cursor.close()

    def insert_bpms(self, names):
        cursor = self.db_connector.sql_con.cursor()
        for idx, name in enumerate(names):
            cursor.execute(f"INSERT INTO {TABLE_NAMES.BPM} (name, x, y, length, pos) VALUES ('{name}','0.0', '0.0', '-1.0', '{idx}')")
        cursor = self.db_connector.sql_con.cursor()
        self.db_connector.sql_con.commit()
        cursor.close()

    def insert_magnets_table(self, names, types, values):
        cursor = self.db_connector.sql_con.cursor()
        for idx, t in enumerate(zip(names, types, values)):
            name, type, value = t
            cursor.execute(f"INSERT INTO {TABLE_NAMES.MAGNETS} (name, type, value, pos) VALUES ('{name}','{type}', '{value}', '{idx}')")
        self.db_connector.sql_con.commit()
        cursor.close()

    def insert_twiss(self, names, value_mat):
        cursor = self.db_connector.sql_con.cursor()
        for name, row in zip(names, value_mat):
            beta_x, beta_y, D_x, D_y = row
            cursor.execute(f"INSERT INTO {TABLE_NAMES.TWISS} (name, beta_x, beta_y, D_x, D_y) VALUES ('{name}','{beta_x}', '{beta_y}', '{D_x}', '{D_y}')")
        self.db_connector.sql_con.commit()
        cursor.close()

    def insert_random_values_for_magnets(self, names, multiply_factor=1e-4):
        self.insert_magnets_table(names, [multiply_factor*random() for _ in range(len(names))])

    def insert_default_machine_params(self, param_names, values):
        cursor = self.db_connector.sql_con.cursor()
        for name, value in zip(param_names, values):
            cursor.execute(f"INSERT INTO {TABLE_NAMES.MACHINE_PARMS} (param, value) VALUES ('{name}','{value}')")
        self.db_connector.sql_con.commit()
        cursor.close()

    @wait_until_table_created(TABLE_NAMES.BPM)
    def set_xy_bpms(self, val):
        try:
            data = []
            for idx, val in enumerate(val):
                data.append((val[0], val[1], idx))
            cursor = self.db_connector.sql_con.cursor()
            cursor.executemany("Update " + TABLE_NAMES.BPM + " set x=%s, y=%s where pos=%s", data)
            self.db_connector.sql_con.commit()
            cursor.close()
        except mysql.connector.Error as error:
            _logger.error(f"Rollback: error while setting bpms: {error}")
            self.db_connector.sql_con.rollback()

    @wait_until_table_created(TABLE_NAMES.MAGNETS)
    def set_correctors_randomly(self, _max, _min):
        def func(_min, _max):
            if _min == 0 and _max == 0:
                return 0
            return np.random.uniform(_min, _max)/100.0
        vcor_ref_val = load_sim_data(Path(PATH_TO_ACSS_SERVICES_ROOT) / Path('adapter/petra/config/sim-data/all-vcor-strengths-3-5-22'))
        vcor_ref_val = [val*(1 + func(_min, _max)) for val in vcor_ref_val]
        hcor_ref_val = load_sim_data(Path(PATH_TO_ACSS_SERVICES_ROOT) / Path('adapter/petra/config/sim-data/all-hcor-strengths-3-5-22'))
        hcor_ref_val = [val*(1 + func(_min, _max)) for val in hcor_ref_val]
        self.set_magnet_values_as_group(MAGNET_TABLE_TYPES.HCOR, hcor_ref_val, len(hcor_ref_val))
        self.set_magnet_values_as_group(MAGNET_TABLE_TYPES.VCOR, vcor_ref_val, len(vcor_ref_val))

    @wait_until_table_created(TABLE_NAMES.MAGNETS)
    def set_magnet_values_as_group(self, group, values, size):
        try:
            data = []
            for pos, value in zip(range(size), values):
                data.append((value, pos, group))
            cursor = self.db_connector.sql_con.cursor()
            cursor.executemany("Update magnets set value = %s where pos=%s and type=%s", data)
            self.db_connector.sql_con.commit()
            cursor.close()
            return True
        except mysql.connector.Error as error:
            _logger.error(f"Rollback: error while setting bpms: {error}")
            self.db_connector.sql_con.rollback()
        return False

    @wait_until_table_created(TABLE_NAMES.MAGNETS)
    def set_magnet_value(self, device, value):
        try:
            query = f"Update magnets set value ={value} where name='{device.upper()}'"
            cursor = self.db_connector.sql_con.cursor()
            cursor.execute(query)
            self.db_connector.sql_con.commit()
            cursor.close()
            return True
        except mysql.connector.Error as error:
            _logger.error(f"Rollback: error while setting bpms: {error}")
            self.db_connector.sql_con.rollback()
        return False

    @wait_until_table_created(TABLE_NAMES.MACHINE_PARMS)
    def set_machine_params(self, names, values):
        try:
            data = [(value, name) for name, value in zip(names, values)]
            cursor = self.db_connector.sql_con.cursor()
            cursor.executemany("Update machine_params set value = %s where param = %s", data)
            cursor.close()
        except mysql.connector.Error as error:
            _logger.error(f"Rollback: error while setting bpms: {error}")
            self.db_connector.sql_con.rollback()

    def _create_update_queries(self, table, where_key, rows):
        queries = []
        for row in rows:
            found_where_key_val_pair = next(
                (key_val_pair for key_val_pair in row if key_val_pair[0] == where_key), None
            )
            if found_where_key_val_pair is None:
                _logger.debug(f"update table {table} failed because key {where_key} is not in input.")
                return []
            ",".join([f"{key_val_pair[0]}={key_val_pair[1]}" for key_val_pair in row if key_val_pair[0] != where_key])
            set_clauses = []
            for key_val_pair in row:
                if key_val_pair[0] != where_key:
                    if type(key_val_pair[1]) == str:
                        set_clauses.append(f"{key_val_pair[0]}='{key_val_pair[1]}'")
                    else:
                        set_clauses.append(f"{key_val_pair[0]}={key_val_pair[1]}")

            query = f"Update {table} set {','.join(set_clauses)} where {found_where_key_val_pair[0]}='{found_where_key_val_pair[1]}'"
            queries.append(query)
        return queries

    @wait_until_table_created(TABLE_NAMES.BPM)
    def get_bpm(self, axes: str, bpm: str):
        sql_select_Query = f"select {axes}, name from {TABLE_NAMES.BPM} order by pos"
        cursor = self.db_connector.sql_con.cursor()
        cursor.execute(sql_select_Query)
        result = cursor.fetchall()
        self.db_connector.sql_con.commit()
        cursor.close()
        values = [res[0] for res in result]
        bpm_names = [res[1] for res in result]
        start_i = bpm_names.index(bpm)
        values = values[start_i:] + values[:start_i]  # realign names to start from bpm
        return values

    @wait_until_table_created(TABLE_NAMES.BPM)
    def get_bpm_names(self, axes: str, bpm: str):
        sql_select_Query = f"select name from {TABLE_NAMES.BPM} order by pos"
        cursor = self.db_connector.sql_con.cursor()
        cursor.execute(sql_select_Query)
        result = cursor.fetchall()
        self.db_connector.sql_con.commit()
        cursor.close()
        bpm_names = [res[0] for res in result]
        return bpm_names

    @wait_until_table_created(TABLE_NAMES.MACHINE_PARMS)
    def get_machine_params(self):
        sql_select_Query = f"select param, value from {TABLE_NAMES.MACHINE_PARMS}"
        cursor = self.db_connector.sql_con.cursor()
        cursor.execute(sql_select_Query)
        res = {res[0]: res[1] for res in cursor.fetchall()}
        self.db_connector.sql_con.commit()
        cursor.close()
        return res

    @wait_until_table_created(TABLE_NAMES.BPM)
    def get_ref_orbit(self):
        sql_select_Query = f"select count(*) from {TABLE_NAMES.BPM}"
        cursor = self.db_connector.sql_con.cursor()
        cursor.execute(sql_select_Query)
        result = cursor.fetchall()
        self.db_connector.sql_con.commit()
        cursor.close()
        count = result[0][0]
        return [0.0 for _ in range(count)]

    @wait_until_table_created(TABLE_NAMES.MAGNETS)
    def get_magnets(self, device):
        query = f"select value from {TABLE_NAMES.MAGNETS} where name = '{device.upper()}'"
        cursor = self.db_connector.sql_con.cursor()
        cursor.execute(query)
        res = cursor.fetchone()[0]
        self.db_connector.sql_con.commit()
        return res

    @wait_until_table_created(TABLE_NAMES.MAGNETS)
    def get_magnets_by_group(self, group, size=None):
        query = f"select value from {TABLE_NAMES.MAGNETS} where type = '{group}' order by pos"
        if size is not None:
            query += f" Limit {size}"  # TODO: is this the right behavior of Tine?
        cursor = self.db_connector.sql_con.cursor()
        cursor.execute(query)
        res = [res[0] for res in cursor.fetchall()]
        self.db_connector.sql_con.commit()
        return res

    @wait_until_table_created(TABLE_NAMES.MAGNETS)
    def get_magnet_names(self, device, size=None):
        query = f"select name from {TABLE_NAMES.MAGNETS} where type='{device}' order by pos"
        if size is not None:
            query += f" Limit {size}"  # TODO: is this the right behavior of Tine?
        cursor = self.db_connector.sql_con.cursor()
        cursor.execute(query)
        res = [res[0] for res in cursor.fetchall()]
        self.db_connector.sql_con.commit()
        cursor.close()
        return res

    @wait_until_table_created(TABLE_NAMES.MAGNETS)
    def get_num_of_magnets(self, device, size=None):
        query = f"select COUNT(*) from {TABLE_NAMES.MAGNETS} where type='{device}' order by pos"
        if size is not None:
            query += f" Limit {size}"  # TODO: is this the right behavior of Tine?
        cursor = self.db_connector.sql_con.cursor()
        cursor.execute(query)
        res = cursor.fetchall()[0][0]
        self.db_connector.sql_con.commit()
        cursor.close()
        return res

    def get_table(self, table, where_key_value_pair=None, col_names=None):
        col_names_str = '*' if col_names is None else ','.join(col_names)
        query = f"select {col_names_str} from {table}" if where_key_value_pair is None else f"select {col_names_str} from {table} where {where_key_value_pair[0]}='{where_key_value_pair[1]}'"
        cursor = self.db_connector.sql_con.cursor()
        cursor.execute(query)
        return [res for res in cursor.fetchall()]

    def set_table(self, where_key, table, rows):
        try:
            cursor = self.db_connector.sql_con.cursor()
            queries = self._create_update_queries(table, where_key, rows)
            for query in queries:
                cursor.execute(query)
            self.db_connector.sql_con.commit()
            cursor.close()
            return True
        except mysql.connector.Error as error:
            _logger.error(f"Rollback: error while setting bpms: {error}")
            self.db_connector.sql_con.rollback()
            return False

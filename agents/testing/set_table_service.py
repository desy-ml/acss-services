from adapter.petra.utils import set_service_by_env_values
from acss_core.simple_service import SimpleService
from acss_core.logger import logging
from adapter.petra.simulation_db_types import TABLE_NAMES

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class SetTableService(SimpleService):
    def __init__(self, name, read):
        super().__init__(name, read)

    def proposal(self, params):
        if params == None:
            _logger.error(f"params is empty.")
            return

        set_data = {}
        params_data = params.get('data')
        if type(params_data) != list:
            _logger.error(f"params have to be a list.")
            return

        for data in params_data:
            if type(data) != dict:
                _logger.error(f"params have to be a dict")
                return

            names = data.get('names')
            if names == None:
                _logger.error(f"names are not set for service {self.name}")
                return
            values = data.get('values')
            if values == None:
                _logger.error(f"values are not set for service {self.name}")
                return
            set_type = data.get('type')
            if set_type == None:
                _logger.error(f"type is not set for service {self.name}")
                return

            if set_type == 'hcor':
                self.write("/SIMULATION/PETRA/DB", TABLE_NAMES.MAGNETS, "SQL", where_key='name', input=[[('name', name), ("value", strength)] for name, strength in zip(names, values)])
            if set_type == 'vcor':
                self.write("/SIMULATION/PETRA/DB", TABLE_NAMES.MAGNETS, "SQL", where_key='name', input=[[('name', name), ("value", strength)] for name, strength in zip(names, values)])
            if set_type == 'machine_params':
                self.write("/SIMULATION/PETRA/DB", TABLE_NAMES.MACHINE_PARMS, "SQL", where_key='param',
                           input=[[('param', name), ("value", strength)] for name, strength in zip(names, values)])
            if set_type == 'twiss':
                raise NotImplementedError
        self.write.commit()
        print(set_data)


if __name__ == '__main__':
    name, read, mode = set_service_by_env_values()
    agent = SetTableService(name,  read=None)
    agent.init_local()

from acss_core.logger import init_logger
from adapter.petra.PetraSimDatabase import PetraSimDatabase

_logger = init_logger(__name__)


class TineSimAdapter:
    def __init__(self, sim_database) -> None:
        self.db = sim_database
        self.corrector_prefixes = {"pkpda", "pkhw", "pch", "pkpdd", "pkh", "pkdk"}

    @classmethod
    def create_for_petra(cls):
        return cls(PetraSimDatabase())

    def _is_corrector(self, device):
        prefix = device.split("_")[0].lower()
        return prefix in self.corrector_prefixes

    def raiseNotImplError(self, channel: str, device: str, _property: str, **kwargs):
        raise NotImplementedError(
            f"Channel {channel} with device {device}, property {_property} and kwargs: {kwargs} isn't implemented"
        )


class TineSimWriter(TineSimAdapter):
    def __init__(self, sim_database):
        super().__init__(sim_database=sim_database)

    def simulation_write(self, channel: str, device: str, _property: str, **kwargs):
        if channel == "/SIMULATION/PETRA/LBRENV":
            if _property == "XY" and device == "ALL":
                values = kwargs["input"]
                self.db.set_xy_bpms(values)
                return
        elif channel == "/SIMULATION/PETRA/DB":
            if _property == "SQL":
                where_key = kwargs.get('where_key')
                rows = kwargs["input"]
                table = device
                if where_key is None:
                    _logger.error("'where_key' have to be defined in **kwargs.")
                    return False
                return self.db.set_table(where_key, table, rows)

        self.raiseNotImplError(channel, device, _property, **kwargs)

    def __call__(self, channel: str, device: str, _property: str, **kwargs):
        if channel.split("/")[1] == "SIMULATION":
            self.simulation_write(channel, device, _property, **kwargs)
            return
        if channel == "/PETRA/Cms.PsGroup":
            values = kwargs["input"]
            size = kwargs.get("size")
            if _property == "Strength.Soll":
                self.db.set_magnet_values_as_group(device, values, size)
                return
            if _property == "Strength.Random":
                _min, _max = values
                if device == "CORS":
                    self.db.set_correctors_randomly(_min, _max)
                    return
        elif channel == "/PETRA/Cms.MagnetPs":
            val = kwargs["input"]
            if _property == "Strength.Soll":
                self.db.set_magnet_value(device, val)
                return
        self.raiseNotImplError(channel, device, _property, **kwargs)

    def commit():
        pass


class TineSimReader(TineSimAdapter):
    def __init__(self, sim_database):
        super().__init__(sim_database=sim_database)

    def simulation_read(self, channel: str, device: str, _property: str, **kwargs):
        if channel == "/SIMULATION/PETRA/DB":
            if _property == "SQL":
                table = device
                where_key_value_pair = kwargs.get('where_key_value_pair', None)
                col_names = kwargs.get('col_names', None)
                return self.db.get_table(table, where_key_value_pair, col_names)

        self.raiseNotImplError(channel, device, _property, **kwargs)

    def __call__(self, channel: str, device: str, _property: str, **kwargs):
        if channel.split("/")[1] == "SIMULATION":
            return self.simulation_read(channel, device, _property, **kwargs)

        if channel == "/PETRA/Cms.MagnetPs":
            if _property == "Strength.Soll":
                return self.db.get_magnets(device)
            else:
                self.raiseNotImplError(channel, device, _property, **kwargs)
        elif channel == "/PETRA/LBRENV":
            if _property == "SA_X":
                return self.db.get_bpm("x", device)
            elif _property == "SA_Y":
                return self.db.get_bpm("y", device)
            elif _property == "DEVICES":
                return self.db.get_bpm_names("y", device)
            else:
                self.raiseNotImplError(channel, device, _property, **kwargs)
        elif channel == "/PETRA/REFORBIT":
            if _property == "SA_X":
                return self.db.get_bpm("x", device)
            elif _property == "SA_Y":
                return self.db.get_bpm("y", device)
            else:
                self.raiseNotImplError(channel, device, _property, **kwargs)
        elif channel == "/PETRA/Cms.PsGroup":
            if _property == "GroupDevices":
                return self.db.get_magnet_names(device)
            elif _property == "GroupSize":
                return self.db.get_num_of_magnets(device)
            elif _property == "Strength.Soll":
                return self.db.get_magnets_by_group(device)
            else:
                self.raiseNotImplError(channel, device, _property, **kwargs)
        else:
            self.raiseNotImplError(channel, device, _property, **kwargs)

import numpy as np
import PyTine as pt
from K2I2K_os import K2I2K_os
from typing import List


class TineAdapter():
    def __init__(self, energy=6.063) -> None:
        self.energy = energy

    def find_latest_server(prefix, servers):
        latest_server = None
        latest_version = 0
        for server in servers:
            if server.startswith(prefix):
                version = int(server[len(prefix):])
                if version > latest_version:
                    latest_version = version
                    latest_server = server
        return latest_server

    def find_latest_optic_server():
        servers = pt.list('Common')['servers']
        return TineAdapter.find_latest_server('K2I2KL', servers), TineAdapter.find_latest_server('OPTICL', servers)

    def strength2current(self, names: List, strengths: List) -> np.ndarray:
        kk = K2I2K_os(names, psStrength=strengths, energy=self.energy, debug=None)
        return kk.psCurrent

    def current2strength(self, names: List, currents: List) -> np.ndarray:
        kk = K2I2K_os(names, psCurrent=currents, energy=self.energy, debug=None)
        return kk.psStrength


class TineWriter(TineAdapter):
    def __init__(self, energy=6.063):
        super().__init__(energy=6.063)

    def __call__(self, channel: str, device: str, _property, **kwargs):
        addr = f"{channel}/{device}"

        if _property == "Strength.Soll":
            strengths = kwargs.get("input")
            if strengths is None:
                raise ValueError("input is not set.")

            filtered_kwargs = {key: value for key, value in kwargs.items() if key != 'input'}
            if channel == "/PETRA/Cms.PsGroup":
                size = pt.get(addr, "GroupSize")['data']
                names = pt.get(addr, "GroupDevices", size=size)['data']
                currents = self.strength2current(names, strengths)
                print("New Currents:")
                print(*list(zip(names,currents)), sep='\n')                


                pt.set(addr, "Strom.Soll", input=list(currents), **filtered_kwargs)
                return
            elif channel == "/PETRA/Cms.MagnetPs":
                current = self.strength2current([device], [strengths])[0]
                pt.set(addr, "Strom.Soll", input=current, **filtered_kwargs)
                return
            else:
                raise NotImplemented()

        pt.set(addr, _property, **kwargs)

    def commit():
        pass


class TineReader(TineAdapter):
    def __init__(self, energy=6.063):
        super().__init__(energy=6.063)

    def __call__(self, channel: str, device: str, _property: str, **kwargs):
        addr = f"{channel}/{device}"

        if _property == "Strength.Soll":
            if channel == "/PETRA/Cms.PsGroup":
                #size = kwargs.get('size', pt.get(addr, "GroupSize")['data'])
                size = pt.get(addr, "GroupSize")['data']

                names = pt.get(addr, "GroupDevices", size=size)['data']
                currents = pt.get(addr, "Strom.Soll", size=size)['data']
                return self.current2strength(names, currents)
            elif channel == "/PETRA/Cms.MagnetPs":
                current = pt.get(addr, 'Strom.Soll', **kwargs)['data']
                return self.current2strength([device], [current])[0]

        return pt.get(addr, _property, **kwargs)['data']

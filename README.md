# ACSS Services
Collection of Agents and Simulations for ACSS. 
Note: To run the project on you locally you need to install ACSS Core on your machine which can be found at github (https://github.com/desy-ml/ml-pipeline).


# Start an Agent
If you want to start an Agent on your local machine, your machine have to have access to the ACCS Core Services (https://github.com/desy-ml/ml-pipeline).

Additionally you have to set the config.yaml file to tell the Agent where to find the ACSS Core Services.

Here is an example of config.yaml file. 

Notes: You have to replace localhost with the real server name if the ACSS Core Services aren't running on your local machine.
```yml
observer:
  # used to check if jbb is done
  url: localhost:5003
  event_db_pw: xxxxx
  # event_db_url:
  event_db_usr: xxxxx
register:
  # registers all services
  url: localhost:5004
simulation:
  # sql database which maps the machine parameter
  sim_db_pw: xxxxx
  sim_db_usr: xxxxx
  sim_db_url: localhost:3306
msg_bus:
  # message bus
  broker_urls: localhost:9094,localhost:9096
```

Afterwards, set the path to the config yaml file in the environment value ACSS_CONFIG_FILEPATH.

```bash
ACSS_CONFIG_FILEPATH = /path/to/ml-pipe-config.yaml
```

To run an Agent you need to activate the python env.
```
pipenv shell
```
Afterwards you can run the Agent inside the environment
```
python agents/testing/silly_agent.py
```
To interact with ACSS (e.g trigger, start, list, stop Agents) you can used KafkaPipeClient which is a part of the acss_core lib that can be installed with pip. 
```python
from acss_core.client.utils import get_services
agts, sims = get_services()
agts['SillyAgent'].run()
```

# How to create and run an Agent?
To create an Agent you need to clone the ml-pipe-service repository and install ml-pipe-core.
```
mkdir .venv
```
```
pipenv install .
```

Afterwards you create a class which inherits form SimpleService.
```python
class SillyAgent(SimpleService):
    def __init__(self, name, read):
        super().__init__(name, read)
        self.factor = 1.0
        self.machine_adapter = PetraMachineAdapter.create_for_agent(self)

    def info(self):
        return "Agent reads horizontal corrector currents and multiply a factor to each current. The factor can be reconfigured."

    def reconfig_event(self, msg):
        factor = msg.get('factor')

        if factor is None:
            _logger.error("reconfig message doesn't have 'factor' as a key.")
        else:
            _logger.debug(f"set new factor to: {factor}")
            self.factor = factor

        exclude_cor = msg.get('exclude_cor')
        if exclude_cor != None:
            self.machine_adapter.ignore_hcors(exclude_cor)
            self.machine_adapter.ignore_vcors(exclude_cor)

    def proposal(self, params):
        _logger.debug(f"use factor: {self.factor}")

        hcors = self.machine_adapter.get_hcors(names=self.machine_adapter.get_hcor_device_names(), is_group_call=True)
        vcors = self.machine_adapter.get_vcors(names=self.machine_adapter.get_vcor_device_names(), is_group_call=True)
        self.machine_adapter.set_hcors(self.machine_adapter.get_hcor_device_names(), [val * self.factor for val in hcors])
        self.machine_adapter.set_vcors(self.machine_adapter.get_vcor_device_names(), [val * self.factor for val in vcors])

        self.machine_adapter.commit()
```
Inside this class you need to overload 
```python
def proposal(self, params)
``` 
which will be called when the Agent is triggered.

To read and write the Machine/Simulation parameter you can use the read and write member functions of the Agent. Here is an example for Petra:
```python
def proposal(self, params):
    vcors = self.read('/PETRA/Cms.PsGroup', 'PeCorV', 'GroupDevices')
    self.write("/PETRA/Cms.PsGroup", 'PeCorV', 'Strength.Soll', input=vcors)
``` 
The read callable have to be set while initializing the Agent. Currently only a Reader for the "Tine" Control System is implemented. 
```python
if __name__ == '__main__':
    agent = SillyAgent('silly_agent',  read=TineSimReader.create_for_petra())
    agent.init_local()
```
It is possible to write your own Reader and Writer for an other Control System by defining a read and write callable which fullfil the read/write interface:
```python
def __call__(self, channel: str, device: str, _property: str, **kwargs):
    #custom code 
```

Optionally you can overload 
```python
def reconfig_event(self, msg):
    #custom code 
```
which give you the possibility to reset internal parameters without restarting your Agent.

# How to create and run a Simulation?

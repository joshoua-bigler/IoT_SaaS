import concurrent.futures
import json
import time
from dataclasses import dataclass, field
from threading import Event
from google.protobuf.timestamp_pb2 import Timestamp
from iot_libs.proto.enums import StubMethod
from iot_libs.proto.hub_pb2 import NumericScalarValues
from pathlib import Path
# local
from edge_device.gls.gls import logger
from edge_device.gls.const import SENSOR_TYPES
from edge_device.api.grpc_client import GrpcClient
from edge_device.device import Device
from edge_device.sensors.sensor_simulator import DisturbanceSimulator, SensorSimulator


def create_sensor(sensor_identifier: str,
                  sensor_type: str,
                  path: str,
                  sampling_interval: int = None,
                  data: dict = None) -> SensorSimulator:
  sensor = SENSOR_TYPES.get(sensor_type)
  if data is None:
    data = {}
  if sensor:
    return sensor(sensor_identifier=sensor_identifier, path=path, sampling_interval=sampling_interval, data=data)
  else:
    raise ValueError(f'Unknown sensor type: {sensor_type}')


@dataclass
class SensorManager:
  sensors: dict[str, SensorSimulator] = field(default_factory=dict)
  storage_file: Path = Path('storage/sensors.json')

  def add_sensor(self, sensor: DisturbanceSimulator):
    '''Add a sensor to the manager.'''
    if sensor.metric_identifier not in self.sensors:
      self.sensors[sensor.metric_identifier] = sensor
      self.save_sensors()
      logger.info(f'Sensor {sensor.metric_identifier} added successfully.')
    else:
      raise ValueError(f'Sensor {sensor.metric_identifier} already exists.')
    return f'Sensor {sensor.metric_identifier} added successfully.'

  def get_sensors(self) -> list[dict]:
    '''Get all sensors in the manager. '''
    data = []
    for key, value in self.sensors.items():
      data.append({
          'sensor_identifier': value.sensor_identifier,
          'path': value.path,
          'sensor_type': value.sensor_type,
          'sample_interval': value.sampling_interval,
          'data': value.data
      })
    return data

  def remove_sensor(self, metric_identifier: str):
    '''Remove a sensor from the manager.'''
    if metric_identifier in self.sensors:
      self.sensors.pop(metric_identifier)
      self.save_sensors()
      logger.info(f'Sensor {metric_identifier} removed successfully.')
    else:
      raise ValueError(f'Sensor {metric_identifier} does not exist.')
    return f'Sensor {metric_identifier} removed successfully.'

  def list_sensors(self) -> list[str]:
    return list(self.sensors.keys())

  def save_sensors(self):
    '''Save sensors to a JSON file.'''
    with open(self.storage_file, 'w') as doc:
      json.dump([sensor.save() for sensor in self.sensors.values()], doc, indent=2)

  def load_sensors(self):
    '''Load sensors from a JSON file.'''
    if not self.storage_file.exists():
      self.storage_file.parent.mkdir(parents=True, exist_ok=True)
      self.storage_file.touch()
      logger.info(f'Created new storage file at {self.storage_file}')
      return
    if self.storage_file.stat().st_size == 0:
      logger.info(f'Storage file {self.storage_file} is empty. No sensors loaded.')
      return
    with open(self.storage_file, 'r') as doc:
      sensors_data = json.load(doc)
      for data in sensors_data:
        sensor = create_sensor(sensor_identifier=data['sensor_identifier'],
                               sensor_type=data['sensor_type'],
                               path=data['path'],
                               sampling_interval=data['sampling_interval'],
                               data=data['data'])
        self.add_sensor(sensor)


def handle_future(future: concurrent.futures.Future):
  try:
    future.result()
  except Exception as exc:
    logger.error(f'Exception in future: {exc}')


@dataclass
class SimulationManager:
  device: Device
  grpc_client: GrpcClient
  sensor_manager: SensorManager
  executor: concurrent.futures.ThreadPoolExecutor = field(default=None, init=False)
  restart_executor: concurrent.futures.ThreadPoolExecutor = field(default=None, init=False)
  stop_event: Event = field(default_factory=Event)
  timestamp: Timestamp = field(default_factory=Timestamp)

  def __post_init__(self):
    self.restart_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

  def start_simulations(self):
    ''' Start simulations for all sensors using a ThreadPoolExecutor. '''
    self.running = True
    if not self.sensor_manager.sensors:
      logger.warning('No sensors available to simulate.')
      self.running = False
      return
    self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(self.sensor_manager.sensors))
    for sensor in self.sensor_manager.sensors.values():
      try:
        future = self.executor.submit(self.run_simulation, sensor)
        future.add_done_callback(handle_future)
      except Exception as exc:
        logger.error(f'Failed to start simulation for sensor {sensor.sensor_identifier} with exception\n{exc}')

  def stop_simulations(self):
    ''' Stop all running simulations. '''
    if not self.executor:
      logger.warning('Simulations already stopped.')
      return
    self.stop_event.set()
    logger.info('Stopping simulations...')
    self.executor.shutdown(wait=True)
    self.executor = None
    self.stop_event.clear()

  def run_simulation(self, sensor: SensorSimulator):
    ''' Run the simulation for a single sensor. '''
    while not self.stop_event.is_set():
      try:
        value = sensor.simulate()
        self.timestamp.GetCurrentTime()
        metrics = []
        if isinstance(value, dict):
          for key, val in value.items():
            metrics.append(
                NumericScalarValues(tenant_identifier=self.device.tenant_identifier,
                                    device_identifier=self.device.device_identifier,
                                    metric_identifier=f'{sensor.metric_identifier}.{key}',
                                    path=sensor.path,
                                    value=val,
                                    timestamp=self.timestamp))
        else:
          metrics.append(
              NumericScalarValues(tenant_identifier=self.device.tenant_identifier,
                                  device_identifier=self.device.device_identifier,
                                  metric_identifier=sensor.metric_identifier,
                                  path=sensor.path,
                                  value=value,
                                  timestamp=self.timestamp))
      except Exception as exc:
        logger.critical(f'Failed to simulate sensor {sensor.sensor_identifier} with exception\n{exc}')
        return
      try:
        self.grpc_client.send(data=metrics, stub_method=StubMethod.SEND_NUMERIC_SCALAR_VALUES)
      except Exception as exc:
        logger.error(f'Failed to send metric: {metrics} with exception\n{exc}')
      if self.stop_event.wait(sensor.sampling_interval):
        break

  def _restart_simulations(self):
    ''' Restart all simulations. '''
    self.stop_simulations()
    self.start_simulations()

  def schedule_restart(self):
    ''' Schedule a restart without waiting for ongoing tasks to complete. '''
    logger.info('Scheduling simulation restart...')
    self.restart_executor.submit(self._restart_simulations)

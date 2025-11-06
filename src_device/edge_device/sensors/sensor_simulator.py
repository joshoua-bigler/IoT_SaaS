from abc import ABC, abstractmethod
# local
from edge_device.disturbances.disturbance import parse_disturbances
from edge_device.gls.gls import logger


class SensorSimulator(ABC):

  def __init__(self,
               sensor_type: str,
               sensor_identifier: str,
               path: str = None,
               sampling_interval: int = 10,
               digit: int = 2,
               data: dict = None):
    self.sensor_identifier = sensor_identifier
    self.sensor_type = sensor_type
    self.metric_identifier = f'{sensor_type}.{sensor_identifier}'
    self.path = path
    self.sampling_interval = sampling_interval
    self.data = data or {}
    self.digit = digit

  def save(self) -> dict:
    ''' Save sensor information for storage. '''
    return {
        'sensor_identifier': self.sensor_identifier,
        'sensor_type': self.sensor_type,
        'path': self.path,
        'sampling_interval': self.sampling_interval,
        'data': self.data
    }

  @abstractmethod
  def simulate(self) -> float | dict[str, float]:
    pass

  def __str__(self) -> str:
    return f'{self.__class__.__name__}(metric_identifier={self.metric_identifier}, path={self.path}, sampling_interval={self.sampling_interval})'


class DisturbanceSimulator(SensorSimulator):
  ''' Sensor class to simulate sensor data. '''

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.disturbance = parse_disturbances(self.data)

  def simulate(self, log: bool = True) -> float:
    disturbance_value = 0
    disturbance_logs = []
    for disturbance in self.disturbance:
      try:
        value = disturbance.simulate()
        disturbance_logs.append(f'{disturbance.disturbance_type}={value}')
        disturbance_value += value
      except Exception as exc:
        logger.error(f'Failed to simulate disturbance {disturbance.disturbance_type}: {exc}')
        continue
    try:
      value = round(self.model.simulate(nsimulations=1).iloc[0] + self.offset + disturbance_value, self.digit)
    except Exception as exc:
      logger.error(f'Failed to simulate model value: {exc}')
      return 0.0
    if log:
      values_txt = ', '.join(disturbance_logs)
      logger.info(f'{self.sensor_type}(metric_identifier={self.metric_identifier}, value={value}, offset={self.offset}, {values_txt})') # yapf: disable
    return value

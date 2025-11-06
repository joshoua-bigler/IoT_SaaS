import os
import pandas as pd
from pathlib import Path
from iot_libs.const.edge_device import FaultTypes
# local
from edge_device.sensors.sensor_simulator import SensorSimulator
from edge_device.gls.gls import logger


def load_data(path: Path) -> pd.DataFrame:
  df = pd.read_csv(path)
  df.rename(columns={'sensor1': 'x_axis'}, inplace=True)
  df.rename(columns={'sensor2': 'y_axis'}, inplace=True)
  df.rename(columns={'time_x': 'timestamp'}, inplace=True)
  df.rename(columns={'gear_fault_desc': 'fault'}, inplace=True)
  df.rename(columns={'load_value': 'load'}, inplace=True)
  df.rename(columns={'speedSet': 'speed'}, inplace=True)
  df['speed'] = df['speed'].round(2)
  df['timestamp'] = pd.to_datetime(df['timestamp'])
  df = df.dropna()
  df.set_index('timestamp', inplace=True)
  df = df.dropna().reset_index()
  df = df.sort_values(by='timestamp').reset_index(drop=True)
  df = df.sort_values(by='timestamp').reset_index(drop=True)
  return df


class Vibration(SensorSimulator):
  sensor_type = 'vibration'

  def __init__(self, **kwags):
    super().__init__(sensor_type=self.sensor_type, **kwags)
    self._load_model()
    self._sample_iter = self.sample_generator()

  def sample_generator(self):
    if self.df is None:
      raise ValueError('Model not loaded!')
    if self.df.empty:
      raise ValueError('Gear vibration DataFrame is empty!')
    while True:
      for _, row in self.df.iterrows():
        yield row.drop(['timestamp', 'fault']).to_dict()

  def simulate(self, log: bool = True) -> float:
    values = next(self._sample_iter)
    if log:
      logger.info(f'{self.sensor_type}(identifier={self.metric_identifier}, value={values}, fault_type={self.data.get("fault_type")})') # yapf: disable
    return values

  def _load_model(self):
    try:
      model_path = os.getenv('SENSOR_MODELS_PATH', 'sensor_models')
      fault_type = self.data.get('fault_type')
      if fault_type is None:
        raise ValueError('"fault_type" not specified in data!')
      elif fault_type not in FaultTypes:
        raise ValueError(f'Invalid fault type: {fault_type}')
      self.df = load_data(path=Path(f'{model_path}/gear_vibration/{fault_type}.csv'))
    except FileNotFoundError:
      raise FileNotFoundError(f'Gear vibration model file not found at {model_path}/gear_vibration/{self.data.get("fault_type")}') # yapf: disable

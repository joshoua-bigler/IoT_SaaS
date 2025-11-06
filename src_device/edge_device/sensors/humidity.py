import os
from statsmodels.tsa.arima.model import ARIMAResults, ARIMA
# local
from edge_device.sensors.sensor_simulator import DisturbanceSimulator


class Humidity(DisturbanceSimulator):
  sensor_type = 'humidity'

  def __init__(self, model: ARIMA = None, **kwargs):
    super().__init__(sensor_type=self.sensor_type, **kwargs)
    self.offset = self.data.get('offset', 0)
    self._load_model(model)

  def _load_model(self, model: ARIMAResults = None):
    try:
      model_path = os.getenv('SENSOR_MODELS_PATH', 'sensor_models')
      self.model = model if model else ARIMAResults.load(f'{model_path}/humidity_model_v2.pkl')
    except FileNotFoundError:
      raise FileNotFoundError(f'Temperature model file not found at {model_path}/humidity_model_v2.pkl')

# local
from edge_device.sensors.temperature import Temperature
from edge_device.sensors.humidity import Humidity
from edge_device.sensors.vibration import Vibration

SENSOR_TYPES = {'temperature': Temperature, 'humidity': Humidity, 'vibration': Vibration}

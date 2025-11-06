import requests
# local
from edge_device.device import Device
from edge_device.gls.gls import logger
from edge_device.utils.decorators import retry


@retry((requests.exceptions.HTTPError, requests.exceptions.Timeout, requests.exceptions.RequestException), delay=10)
def register_device(uri: str,
                    device: Device,
                    timezone: str,
                    endpoint: str = '/api/v1/tenants/devices/register',
                    description: str = 'edge device') -> dict:
  url = f'{uri}{endpoint}'
  payload = {
      'device_identifier': device.device_identifier,
      'tenant_identifier': device.tenant_identifier,
      'description': description,
      'timezone': timezone,
      'long': device.long,
      'lat': device.lat,
      'country': device.country,
  }
  response = requests.post(url, json=payload)
  response.raise_for_status()
  message = response.json()
  logger.info(f'Device registered successfully: {message}')
  return message

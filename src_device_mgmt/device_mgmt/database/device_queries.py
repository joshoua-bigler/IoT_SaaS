from sqlalchemy.orm import scoped_session
from iot_libs.postgres import execute_query, execute_select_query, dict_row
from iot_libs.proto.enums import DeviceHealthStatus
# local
from device_mgmt.schemas.http_request_schemas import DeviceTypeSchema


def select_devices(conn: scoped_session, device_identifiers: str | list[str]) -> str:
  if isinstance(device_identifiers, list):
    formatted_string = ', '.join(f':d_{index}' for index in range(len(device_identifiers)))
    query = f''' select device_identifier from devices where device_identifier IN({formatted_string}) '''
    params = {f'd_{index}': device for index, device in enumerate(device_identifiers)}
  else:
    query = ''' select device_identifier from devices where device_identifier = :device_identifier '''
    params = {'device_identifier': device_identifiers}
  result = execute_select_query(conn=conn, query=query, params=params, row_factory=dict_row)
  return result


def register_device(conn: scoped_session,
                    device_identifier: str,
                    timezone: str,
                    description: str = None,
                    longitude: float = None,
                    latitude: float = None,
                    country: str = None) -> str:
  result = select_devices(conn=conn, device_identifiers=device_identifier)
  if result:
    return f'Device {device_identifier} already exists'
  query = ''' insert into devices (device_identifier, description, long, lat, country, timezone, status, latest_alive) 
              values(:device_identifier, :description, :long, :lat, :country, :timezone, :status, :latest_alive)
              returning device_identifier
          '''
  params = {
      'device_identifier': device_identifier,
      'description': description,
      'long': longitude,
      'lat': latitude,
      'country': country,
      'timezone': timezone,
      'status': None,
      'latest_alive': None
  }
  execute_query(conn=conn, query=query, params=params)
  return f'Device {device_identifier} registered successfully'


def remove_devices(conn: scoped_session, device_identifiers: list[str]) -> str:
  existing_devices = select_devices(conn=conn, device_identifiers=device_identifiers)
  existing_device_ids = {d['device_identifier'] for d in existing_devices}
  non_existing_device_ids = set(device_identifiers) - existing_device_ids
  if existing_device_ids:
    formatted_string = ', '.join(f':d_{index}' for index in range(len(existing_device_ids)))
    query = f''' delete from devices where device_identifier in({formatted_string}) '''
    params = {f'd_{index}': device for index, device in enumerate(existing_device_ids)}
    execute_query(conn=conn, query=query, params=params)
    message = f'Devices {", ".join(existing_device_ids)} removed successfully'
  if non_existing_device_ids and existing_device_ids:
    message += f', devices {", ".join(non_existing_device_ids)} do not exist'
  elif non_existing_device_ids:
    message = f'Devices {", ".join(non_existing_device_ids)} do not exist'
  return message


def get_device_status(conn: scoped_session, device_identifiers: list[str]) -> dict[str, any]:
  existing_devices = select_devices(conn=conn, device_identifiers=device_identifiers)
  existing_device_ids = {d['device_identifier'] for d in existing_devices}
  non_existing_device_ids = list(set(device_identifiers) - existing_device_ids)
  successful_devices = []
  if existing_device_ids:
    formatted_string = ', '.join(f':d_{index}' for index in range(len(existing_device_ids)))
    query = f''' select device_identifier, status from devices where device_identifier in ({formatted_string}) '''
    params = {f'd_{index}': device for index, device in enumerate(existing_device_ids)}
    result = execute_select_query(conn=conn, query=query, params=params, row_factory=dict_row)
    successful_devices = [{
        'device_identifier': device['device_identifier'],
        'status': DeviceHealthStatus(int(device['status'])).name.lower()
    } for device in result]
  return {'devices': successful_devices, 'non_existing_devices': non_existing_device_ids}


def update_device(conn: scoped_session, device_type: DeviceTypeSchema) -> str:
  existing_devices = select_devices(conn=conn, device_identifiers=device_type.device_identifier)
  if not existing_devices:
    return f'Device {existing_devices} does not exist'
  query = ''' update devices set description = :description, timezone = :timezone, long = :long, lat = :lat, country = :country where device_identifier = :device_identifier'''
  params = {
      'device_identifier': device_type.device_identifier,
      'description': device_type.description,
      'timezone': device_type.timezone,
      'long': device_type.long,
      'lat': device_type.lat,
      'country': device_type.country
  }
  execute_query(conn=conn, query=query, params=params)
  return f'Device {device_type.device_identifier} updated successfully'

import pandas as pd
from datetime import datetime
from sqlalchemy.orm import scoped_session
from iot_libs.proto.hub_pb2 import DeviceStatus
from iot_libs.postgres import execute_query, execute_select_query
# local
from hub.gls.gls import logger


def get_device_status(conn: scoped_session):
  query = '''select device_identifier, status, latest_alive from devices'''
  return execute_select_query(conn=conn, query=query)


def set_device_status(status: dict[str, int] | list[dict[str, int]], conn: scoped_session):
  ''' Set the device status in the database. 

      Parameters
      ----------
      status: The status of the device.
      conn: The database connection.

  '''
  if isinstance(status, dict):
    status = [status]
  query = '''update devices set status = :status, where device_identifier = :device_identifier '''
  params = status
  try:
    execute_query(conn=conn, query=query, params=params)
  except Exception as exc:
    logger.error(f'Failed to write to database: {exc}')
    raise


def update_device_status(batch: DeviceStatus | list[DeviceStatus] | dict[str, int] | list[dict[str, int]] |
                         pd.DataFrame, conn: scoped_session):
  ''' Update the device status in the database.

      Parameters
      ----------
      batch: The device status to update.
      conn: The database connection.
  '''
  if isinstance(batch, DeviceStatus):
    batch = [batch]
  elif isinstance(batch, dict):
    batch = [batch]
  elif isinstance(batch, pd.DataFrame):
    batch = batch.to_dict(orient='records')
  if isinstance(batch, list):
    if isinstance(batch[0], DeviceStatus):
      params = [{
          'device_identifier': d.device_identifier,
          'status': d.status,
          'latest_alive': datetime.fromtimestamp(d.timestamp.ToDatetime().timestamp())
      } for d in batch]
    else:
      params = batch
  update_fields = ', '.join([f'{key} = :{key}' for key in params[0].keys() if key != 'device_identifier'])
  query = f'''update devices set {update_fields} where device_identifier = :device_identifier'''
  try:
    execute_query(conn=conn, query=query, params=params)
  except Exception as exc:
    logger.error(f'Failed to write to database: {exc}')
    raise

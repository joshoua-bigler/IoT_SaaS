from sqlalchemy.orm import scoped_session
from iot_libs.postgres import execute_select_query, dict_row


def select_all_devices(conn: scoped_session):
  query = '''select * from devices'''
  return execute_select_query(conn=conn, query=query)


def select_device_timezone(device_identifier: str, conn: scoped_session) -> str:
  query = '''select timezone from devices where device_identifier = :device_identifier'''
  params = {'device_identifier': device_identifier}
  result = execute_select_query(conn=conn, query=query, params=params, row_factory=dict_row)
  if not result:
    raise ValueError(f'Device with identifier {device_identifier} not found')
  return result[0]['timezone']

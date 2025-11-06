from datetime import datetime
from dataclasses import dataclass
from google.protobuf.timestamp_pb2 import Timestamp
from iot_libs.postgres import execute_query, execute_select_query, dict_row
from sqlalchemy.orm import scoped_session
from iot_libs.proto.hub_pb2 import NumericScalarValues
# local
from hub.gls.gls import logger


class TimestampTypeError(Exception):
  pass


@dataclass
class ScalarNumericMetric:
  device_identifier: str
  metric_id: str
  value: float
  timestamp: Timestamp


def select_metrics_id(metric: NumericScalarValues, conn: scoped_session) -> str | None:
  ''' Check if the metric exists in the database and return the metric id if it exist. '''
  query = "select id from metrics where device_identifier = :device_identifier and metric_identifier = :metric_identifier and metric_type = 'numeric_scalar'"
  params = {'device_identifier': metric.device_identifier, 'metric_identifier': metric.metric_identifier}
  try:
    result = execute_select_query(conn=conn, query=query, params=params, row_factory=dict_row)
  except Exception as exc:
    logger.error(f'Failed to check if metric exists: {exc}')
    raise
  if not result:
    return
  return result[0]['id']


def get_metric_id(metric: NumericScalarValues, conn: scoped_session, path_id: str = None) -> str | None:
  ''' Get the metric id from the database. '''
  metrics_id = select_metrics_id(metric=metric, conn=conn)
  if metrics_id:
    return metrics_id
  query = "insert into metrics (device_identifier, path_id, metric_identifier, unit, display_name, metric_type) values(:device_identifier, :path_id, :metric_identifier, :unit, :display_name, :metric_type)"
  params = {
      'device_identifier': metric.device_identifier,
      'metric_identifier': metric.metric_identifier,
      'path_id': path_id,
      'unit': metric.unit,
      'display_name': metric.display_name,
      'metric_type': 'numeric_scalar'
  }
  try:
    execute_query(conn=conn, query=query, params=params)
    metrics_id = select_metrics_id(metric=metric, conn=conn)
    if not metrics_id:
      raise Exception(f'Failed to create metric with metric identifier {metric.metric_identifier}')
    return metrics_id
  except Exception as exc:
    logger.error(f'Failed to create metric with exception: {exc}')
    raise


def insert_metrics(metrics: ScalarNumericMetric | list[ScalarNumericMetric], conn: scoped_session):
  ''' Insert metrics into the database. '''
  if isinstance(metrics, ScalarNumericMetric):
    metrics = [metrics]
  query = "insert into numeric_scalar_values (metric_id, value, timestamp) values(:metric_id, :value, :timestamp)"
  params = [{'metric_id': metric.metric_id, 'value': metric.value, 'timestamp': metric.timestamp} for metric in metrics]
  try:
    execute_query(conn=conn, query=query, params=params)
  except Exception as exc:
    logger.error(f'Failed to write to database: {exc}')
    raise


def select_path_id(metric: NumericScalarValues, conn: scoped_session) -> str | None:
  ''' Check if the path exists in the database and return the path id if it exist. '''
  query = "select id from paths where device_identifier = :device_identifier and path = :path"
  params = {'device_identifier': metric.device_identifier, 'path': metric.path}
  try:
    result = execute_select_query(conn=conn, query=query, params=params, row_factory=dict_row)
  except Exception as exc:
    logger.error(f'Failed to check if path exists: {exc}')
    raise
  if not result:
    return
  return result[0]['id']


def get_path_id(metric: NumericScalarValues, conn: scoped_session) -> str | None:
  ''' Get the path id from the database. '''
  path_id = select_path_id(metric=metric, conn=conn)
  if path_id:
    return path_id
  query = "insert into paths (device_identifier, path) values(:device_identifier, :path) on conflict do nothing"
  params = {'device_identifier': metric.device_identifier, 'path': metric.path}
  try:
    execute_query(conn=conn, query=query, params=params)
    path_id = select_path_id(metric=metric, conn=conn)
    if not path_id:
      raise Exception(f'Failed to create path with path {metric.path}')
    return path_id
  except Exception as exc:
    logger.error(f'Failed to create path with exception: {exc}')
    raise


def update_metrics(batch: NumericScalarValues | list[NumericScalarValues], conn: scoped_session):
  ''' Update the metrics in the database. '''
  if isinstance(batch, NumericScalarValues):
    batch = [batch]
  metrics_list: list[ScalarNumericMetric] = []
  for metric in batch:
    if not isinstance(metric.timestamp, Timestamp):
      raise TimestampTypeError(f'Timestamp is not of type Timestamp')
    path_id = None
    if metric.path:
      path_id = get_path_id(metric=metric, conn=conn)
    metric_id = get_metric_id(metric=metric, conn=conn, path_id=path_id)
    metrics_list.append(
        ScalarNumericMetric(device_identifier=metric.device_identifier,
                            metric_id=metric_id,
                            value=metric.value,
                            timestamp=datetime.fromtimestamp(metric.timestamp.ToDatetime().timestamp())))
  insert_metrics(metrics=metrics_list, conn=conn)

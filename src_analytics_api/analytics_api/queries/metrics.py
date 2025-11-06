from sqlalchemy.orm import scoped_session
from iot_libs.postgres import execute_select_query
from zoneinfo import ZoneInfo
from datetime import datetime
# local
from analytics_api.queries.devices import select_device_timezone
from analytics_api.graphql.types.metrics import NumericScalarInput
from analytics_api.graphql.enums import GROUPING_SQL, AGGREGATION_SQL


def local_range_to_utc(start: str, end: str, timezone: str) -> tuple[datetime, datetime]:
  tz = ZoneInfo(timezone)
  start_utc = datetime.fromisoformat(start).replace(tzinfo=tz).astimezone(ZoneInfo('UTC'))
  end_utc = datetime.fromisoformat(end).replace(tzinfo=tz).astimezone(ZoneInfo('UTC'))
  return start_utc.strftime('%Y-%m-%d %H:%M:%S'), end_utc.strftime('%Y-%m-%d %H:%M:%S')


def select_numeric_scalar_metrics(body: NumericScalarInput, conn: scoped_session) -> list:
  timezone = select_device_timezone(device_identifier=body.device_identifier, conn=conn)
  # start, end = local_range_to_utc(start=body.start, end=body.end, timezone=timezone)
  select_fields = ['d.device_identifier', 'm.metric_identifier', 'm.unit', 'm.display_name', 'p.path', 'm.metric_type', 'd.timezone'] # yapf: disable
  group_by_fields = select_fields.copy()
  # Add time bucket if grouping is provided
  if body.grouping:
    time_bucket_expr = GROUPING_SQL[body.grouping.value]
    select_fields.append(f"{time_bucket_expr} as timestamp")
    group_by_fields.append(f"{time_bucket_expr}")
  else:
    select_fields.append("n.timestamp")
  # Add aggregation
  if body.aggregation:
    agg_expr = AGGREGATION_SQL[body.aggregation.value]
    select_fields.append(f"{agg_expr} as value")
  else:
    select_fields.append("n.value")
  # Base query
  query = f'''
    select {', '.join(select_fields)}
    from numeric_scalar_values as n
    join metrics as m on n.metric_id = m.id
    join paths as p on m.path_id = p.id
    join devices as d on m.device_identifier = d.device_identifier
    where d.device_identifier = :device_identifier 
    and n.timestamp between :start and :end
  '''
  # optinal path filter
  params = {'start': body.start, 'end': body.end, 'device_identifier': body.device_identifier}
  if body.path:
    query += ' and p.path <@ :path'
    params['path'] = body.path
  if body.metric_identifier:
    query += ' and m.metric_identifier = any(:metric_identifier)'
    params['metric_identifier'] = body.metric_identifier
  # Optional group by
  if body.aggregation or body.grouping:
    query += f' group by {", ".join(group_by_fields)}'
    query += ' order by timestamp desc'
  else:
    query += ' order by n.timestamp desc'
  return execute_select_query(conn=conn, query=query, params=params)

import strawberry
import math
from strawberry.fastapi import GraphQLRouter
# local
from analytics_api.graphql.types.metrics import NumericScalarInput, NumericScalarModelInput, MetricsBase, MetricsModel
from analytics_api.graphql.types.devices import Device
from analytics_api.graphql.types.common import TenantInput
from analytics_api.graphql.formatters.metrics_formatter import format_base_metrics, format_model_metrics
from analytics_api.gls.gls import db_manager
from analytics_api.queries.devices import select_all_devices, select_device_timezone
from analytics_api.queries.metrics import select_numeric_scalar_metrics
from analytics_api.utils.timezone import convert_to_local_time
from analytics_api.ml.models import load_model
from analytics_api.ml.models import create_prediction, voting_prediction
from analytics_api.graphql.enums import status_map, DeviceStatus
from analytics_api.gls.gls import logger


@strawberry.type
class Query:

  @strawberry.field(name='devices')
  def devices(self, body: TenantInput) -> list[Device]:
    body.validate()
    logger.info(f'Received request for devices: {body}')
    with db_manager(f'tenant_{body.tenant_identifier}') as conn:
      df = select_all_devices(conn=conn)
    df['latest_alive_local'] = convert_to_local_time(timestamp=df['latest_alive'], timezone=df['timezone'])
    return [
        Device(device_identifier=row.device_identifier,
               description=row.description if row.description else None,
               long=row.long if not (row.long is None or math.isnan(row.long)) else None,
               lat=row.lat if not (row.lat is None or math.isnan(row.lat)) else None,
               country=row.country if row.country else None,
               timezone=row.timezone,
               status=status_map.get(row.status, DeviceStatus.UNKNOWN),
               latest_alive_local=row.latest_alive_local.to_pydatetime()) for row in df.itertuples(index=False)
    ]

  @strawberry.field(name='numericScalar')
  def numeric_scalar_metrics(self, body: NumericScalarInput) -> list[MetricsBase]:
    if body.grouping and not body.aggregation:
      raise ValueError('aggregation is required when grouping is used.')
    logger.info(f'Received request for numeric scalar metrics: {body}')
    with db_manager(f'tenant_{body.tenant_identifier}') as conn:
      df = select_numeric_scalar_metrics(conn=conn, body=body)
    if df.empty:
      return []
    timezone = select_device_timezone(device_identifier=body.device_identifier, conn=conn)
    df['timestamp_local'] = convert_to_local_time(timestamp=df['timestamp'], timezone=timezone)
    return format_base_metrics(df=df)

  @strawberry.field(name='numericScalarModel')
  def numeric_scalar_model_prediction(self, body: NumericScalarModelInput) -> list[MetricsModel]:
    if body.grouping and not body.aggregation:
      raise ValueError('aggregation is required when grouping is used.')
    logger.info(f'Received request for numeric scalar model metrics: {body}')
    with db_manager(f'tenant_{body.tenant_identifier}') as conn:
      df = select_numeric_scalar_metrics(conn=conn, body=body)
    if df.empty:
      return []
    timezone = select_device_timezone(device_identifier=body.device_identifier, conn=conn)
    df['timestamp_local'] = convert_to_local_time(timestamp=df['timestamp'], timezone=timezone)
    df = df.sort_values(by='timestamp_local')
    # df['daily_date_local'] = df['timestamp_local'].dt.strftime('%A, %Y-%m-%d')
    model_metrics = set(body.metric_identifier) if body.model else set()
    model = load_model(model_input=body.model)
    if model is None:
      raise ValueError(f'Model {body.model.name} not found.')
    model_result = create_prediction(df=df, model=model, model_input=body.model, model_metrics=model_metrics)
    return format_model_metrics(df=df, model_metrics=model_metrics, model_result=model_result)


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema=schema, graphiql=True)

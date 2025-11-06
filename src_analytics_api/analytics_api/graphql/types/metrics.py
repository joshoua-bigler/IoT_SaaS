import strawberry
from datetime import datetime
from typing import Optional
# local
from analytics_api.graphql.types.ml import ModelResult, ModelInput
from analytics_api.graphql.enums import Grouping, Aggregation, Analysis
from analytics_api.graphql.types.common import TenantInput


@strawberry.input
class NumericScalarBase(TenantInput):
  device_identifier: str
  metric_identifier: Optional[list[str]] = None
  start: str
  end: str
  path: Optional[str] = None
  grouping: Optional[Grouping] = None
  aggregation: Optional[Aggregation] = None


@strawberry.input
class NumericScalarInput(NumericScalarBase):
  analysis: Optional[Analysis] = None


@strawberry.input
class NumericScalarModelInput(NumericScalarBase):
  model: ModelInput


@strawberry.type
class Value:
  value: float
  timestamp_local: str


@strawberry.type
class MetricsBase:
  device_identifier: str
  metric_identifier: str
  unit: str
  # analysis: str
  # daily_date_local: str
  values: list[Value]


@strawberry.type
class MetricsModel(MetricsBase):
  model: ModelResult

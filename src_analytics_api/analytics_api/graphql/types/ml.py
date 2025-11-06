import strawberry
from typing import Optional
# local
from analytics_api.graphql.enums import ModelType


@strawberry.input
class ModelInput:
  name: str
  model_type: ModelType
  window_size: int
  version: str


@strawberry.type
class ModelResult:
  name: Optional[str] = None
  predicted: Optional[str] = None
  probability: Optional[float] = None

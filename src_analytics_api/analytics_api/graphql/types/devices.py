import strawberry
from datetime import datetime
from typing import Optional
# local
from analytics_api.graphql.enums import DeviceStatus


@strawberry.type
class Device:
  device_identifier: str
  description: Optional[str] = None
  long: Optional[float] = None
  lat: Optional[float] = None
  country: Optional[str] = None
  timezone: str
  status: Optional[DeviceStatus] = None
  latest_alive_local: Optional[datetime] = None

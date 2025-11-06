from pydantic import BaseModel, field_validator
from typing import Optional


class Devices(BaseModel):
  device_identifier: str | list[str]
  tenant_identifier: str

  @field_validator('device_identifier', mode='before')
  def normalize_device_identifier(cls, device_identifier: str | list[str]) -> list[str]:
    if isinstance(device_identifier, str):
      if len(device_identifier) != 6:
        raise ValueError('device_identifier must be exactly 6 characters')
      return [device_identifier]
    elif isinstance(device_identifier, list):
      for device_id in device_identifier:
        if len(device_id) != 6:
          raise ValueError('device_identifier must be exactly 6 characters')
      return device_identifier
    else:
      raise ValueError('device_identifier must be a string or a list of strings')

  @field_validator('tenant_identifier', mode='before')
  def validate_tenant_identifier(cls, tenant_identifier: str) -> str:
    if len(tenant_identifier) != 6:
      raise ValueError('tenant_identifier must be exactly 6 digits')
    return tenant_identifier


class BaseSchema(BaseModel):
  device_identifier: str
  tenant_identifier: str

  @field_validator('device_identifier', mode='before')
  def validate_device_identifier(cls, device_identifier: str) -> str:
    if not isinstance(device_identifier, str):
      raise ValueError('device_identifier must be a string')
    if len(device_identifier) != 6:
      raise ValueError('device_identifier must be exactly 6 characters')
    return device_identifier

  @field_validator('tenant_identifier', mode='before')
  def validate_tenant_identifier(cls, tenant_identifier: str) -> str:
    if len(tenant_identifier) != 6:
      raise ValueError('tenant_identifier must be exactly 6 characters')
    return tenant_identifier


class DeviceTypeSchema(BaseSchema):
  description: Optional[str] = None
  timezone: Optional[str] = None
  long: Optional[float] = None
  lat: Optional[float] = None
  country: Optional[str] = None


class SensorSchema(BaseSchema):
  sensor_type: str
  sensor_identifier: str
  path: Optional[str] = None
  sampling_interval: Optional[int] = None
  data: Optional[dict] = None

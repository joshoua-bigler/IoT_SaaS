from pydantic import BaseModel, field_validator
from typing import List, Optional


class BaseResponse(BaseModel):
  status: str
  message: str


class SuccessResponse(BaseModel):
  status: str
  message: str
  data: Optional[dict | list[dict]] = None


class ErrorResponse(BaseResponse):
  data: Optional[dict | list[dict]] = None


class SuccessfulDevice(BaseModel):
  device_identifier: str
  status: str


class FailedDevice(BaseModel):
  device_identifier: str
  error: str


class DeviceStatusResponse(BaseModel):
  status: str
  message: str
  devices: list[SuccessfulDevice]
  failed_devices: list[FailedDevice]

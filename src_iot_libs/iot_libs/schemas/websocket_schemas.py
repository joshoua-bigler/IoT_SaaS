from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
# local
from iot_libs.const.edge_device import WsMessageTypes, WsGeneralCommands


class RequestConnectMessage(BaseModel):
  message_type: str = 'connect'
  tenant_identifier: str
  device_identifier: str


class ConnectAckMessage(BaseModel):
  message_type: str = WsMessageTypes.CONNECT_ACK.value
  status: str
  message: str


class BaseCommandMessage(BaseModel):
  message_type: str
  command: str
  tenant_identifier: str
  device_identifier: str
  message_id: UUID = uuid4()
  timestamp: datetime = datetime.now()
  data: Optional[dict | list[dict]] = None


class CommandMessage(BaseCommandMessage):
  message_type: str = WsMessageTypes.COMMAND.value


class SensorManagementMessage(BaseCommandMessage):
  message_type: str = WsMessageTypes.SENSOR_MANAGEMENT.value


class SensorCommandMessage(SensorManagementMessage):
  sensor_identifier: str
  sensor_type: str
  path: Optional[str] = None
  sampling_interval: Optional[int] = None


class CommandResponseMessage(BaseModel):
  message_type: str = 'command_response'
  status: str
  message: str
  message_id: UUID
  data: Optional[dict | list[dict]] = None
  timestamp: datetime = datetime.now()

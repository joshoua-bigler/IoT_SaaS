from enum import Enum


class StubMethod(Enum):
  SEND_NUMERIC_SCALAR_VALUES = ('SendNumericScalarValues', 'stream')
  SEND_DEVICE_STATUS = ('SendDeviceStatus', 'unary')


class DeviceHealthStatus(Enum):
  ONLINE = 10
  OFFLINE = 20
  ERROR = 30
  UNKNOWN = 40

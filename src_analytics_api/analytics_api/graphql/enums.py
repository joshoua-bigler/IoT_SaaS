import strawberry
from enum import Enum
# local
from iot_libs.proto.enums import DeviceHealthStatus


@strawberry.enum
class Grouping(Enum):
  SECOND = 'second'
  MINUTE = 'minute'
  HOURLY = 'hourly'
  DAILY = 'daily'
  WEEKLY = 'weekly'


@strawberry.enum
class Aggregation(Enum):
  MIN = 'min'
  MAX = 'max'
  AVG = 'avg'
  SUM = 'sum'
  COUNT = 'count'


AGGREGATION_SQL = {
    'MIN': 'min(n.value)',
    'MAX': 'max(n.value)',
    'AVG': 'avg(n.value)',
    'SUM': 'sum(n.value)',
    'COUNT': 'count(n.value)'
}


@strawberry.enum
class Analysis(Enum):
  GEAR_VIBRATION = 'gear_vibration'


@strawberry.enum
class DeviceStatus(Enum):
  ONLINE = 'online'
  OFFLINE = 'offline'
  ERROR = 'error'
  UNKNOWN = 'unknown'


@strawberry.enum
class ModelType(Enum):
  SKLEARN = 'sklearn'
  TENSORFLOW = 'tensorflow'
  PYTORCH = 'pytorch'
  LIGHTGBM = 'lightgbm'
  XGBOOST = 'xgboost'
  CATBOOST = 'catboost'


status_map = {
    DeviceHealthStatus.ONLINE.value: DeviceStatus.ONLINE,
    DeviceHealthStatus.OFFLINE.value: DeviceStatus.OFFLINE,
    DeviceHealthStatus.ERROR.value: DeviceStatus.ERROR,
    DeviceHealthStatus.UNKNOWN.value: DeviceStatus.UNKNOWN
}

GROUPING_SQL = {
    Grouping.SECOND.value: "date_trunc('second', n.timestamp)",
    Grouping.MINUTE.value: "date_trunc('minute', n.timestamp)",
    Grouping.HOURLY.value: "date_trunc('hour', n.timestamp)",
    Grouping.DAILY.value: "date_trunc('day', n.timestamp)",
    Grouping.WEEKLY.value: "date_trunc('week', n.timestamp)"
}

AGGREGATION_SQL = {
    Aggregation.MIN.value: 'min(n.value)',
    Aggregation.MAX.value: 'max(n.value)',
    Aggregation.AVG.value: 'avg(n.value)',
    Aggregation.SUM.value: 'sum(n.value)',
    Aggregation.COUNT.value: 'count(n.value)'
}

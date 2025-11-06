from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SUCCESS: _ClassVar[Status]
    FAILED: _ClassVar[Status]
    PENDING: _ClassVar[Status]
SUCCESS: Status
FAILED: Status
PENDING: Status

class DeviceStatus(_message.Message):
    __slots__ = ("tenant_identifier", "device_identifier", "status", "timestamp")
    TENANT_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    DEVICE_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    tenant_identifier: str
    device_identifier: str
    status: int
    timestamp: _timestamp_pb2.Timestamp
    def __init__(self, tenant_identifier: _Optional[str] = ..., device_identifier: _Optional[str] = ..., status: _Optional[int] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class NumericScalarValues(_message.Message):
    __slots__ = ("tenant_identifier", "device_identifier", "metric_identifier", "path", "value", "unit", "display_name", "timestamp")
    TENANT_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    DEVICE_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    METRIC_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    tenant_identifier: str
    device_identifier: str
    metric_identifier: str
    path: str
    value: float
    unit: str
    display_name: str
    timestamp: _timestamp_pb2.Timestamp
    def __init__(self, tenant_identifier: _Optional[str] = ..., device_identifier: _Optional[str] = ..., metric_identifier: _Optional[str] = ..., path: _Optional[str] = ..., value: _Optional[float] = ..., unit: _Optional[str] = ..., display_name: _Optional[str] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ("status", "message")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status: Status
    message: str
    def __init__(self, status: _Optional[_Union[Status, str]] = ..., message: _Optional[str] = ...) -> None: ...

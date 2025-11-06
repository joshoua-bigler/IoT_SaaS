import time
from threading import Event
from dataclasses import dataclass, field
from iot_libs.proto.hub_pb2 import DeviceStatus
from iot_libs.proto.enums import StubMethod, DeviceHealthStatus
from google.protobuf.timestamp_pb2 import Timestamp
# local
from edge_device.api.grpc_client import GrpcClient
from edge_device.gls.gls import logger


@dataclass
class Device:
  device_identifier: str
  tenant_identifier: str
  name: str = None
  long: float = None
  lat: float = None
  description: str = None
  timezone: str = None
  timestamp: Timestamp = field(default_factory=Timestamp)
  country: str = None
  stop_event: Event = field(default_factory=Event)

  def get_device_status(self, status: DeviceHealthStatus = DeviceHealthStatus.ONLINE) -> DeviceStatus:
    self.timestamp.GetCurrentTime()
    return DeviceStatus(device_identifier=self.device_identifier,
                        tenant_identifier=self.tenant_identifier,
                        status=status.value,
                        timestamp=self.timestamp)

  def send_device_state(self, grpc_client: GrpcClient, interval: int = 10, log: bool = False):
    while not self.stop_event.is_set():
      device_status = self.get_device_status(status=DeviceHealthStatus.ONLINE)
      grpc_client.send(data=device_status, stub_method=StubMethod.SEND_DEVICE_STATUS, log=False)
      logger.info(f'Sent device status: {device_status}') if log else None
      time.sleep(interval)

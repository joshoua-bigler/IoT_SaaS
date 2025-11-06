import grpc
import threading
from iot_libs.proto.hub_pb2 import NumericScalarValues, DeviceStatus
from iot_libs.proto.hub_pb2_grpc import HubStub
from iot_libs.proto.enums import StubMethod
# local
from edge_device.gls.gls import logger
from edge_device.utils.decorators import retry


def log_metrics(metrics: list[NumericScalarValues] | NumericScalarValues | DeviceStatus) -> None:
  if isinstance(metrics, list):
    for metric in metrics:
      logger.info(f'Send metric: {metric}')
  else:
    logger.info(f'Send metric: {metrics}')


class GrpcClient:

  def __init__(self, host: str = 'localhost', port: int | str = 50051):
    self.host = host
    self.port = port
    self.channel = None
    self.stub = None
    self.lock = threading.Lock()

  def send(self,
           data: NumericScalarValues | DeviceStatus | list[NumericScalarValues],
           stub_method: StubMethod,
           log: bool = False):
    ''' Send metrics to the gRPC server. '''
    try:
      with self.lock:
        method_name, method_type = stub_method.value
        stub_method = getattr(self.stub, method_name, None)
        if not stub_method:
          raise AttributeError(f'Stub method {method_name} does not exist')
        if isinstance(data, NumericScalarValues):
          data = [data]
        log_metrics(metrics=data) if log else None
        if method_type == 'unary':
          stub_method(data)
        elif method_type == 'stream':
          stub_method(iter(data))
        else:
          raise ValueError(f'Unsuported method type: {method_type}')
    except grpc.RpcError as exc:
      logger.error(f'Failed to send metrics: with exception\n{exc}')
      self.connect()

  @retry((grpc.RpcError, grpc.FutureTimeoutError), delay=10)
  def connect(self):
    ''' Establish a connection to the gRPC server. '''
    with self.lock:
      self.channel = grpc.insecure_channel(f'{self.host}:{self.port}')
      self.stub = HubStub(self.channel)
      grpc.channel_ready_future(self.channel).result(timeout=10)
      logger.info(f'Connected to gRPC server at {self.host}:{self.port}')

  def close(self):
    with self.lock:
      if self.channel:
        logger.info(f'Closing gRPC channel: {self.channel}')
        self.channel.close()

  def __str__(self):
    return f'{self.__class__.__name__}(channel={self.channel})'

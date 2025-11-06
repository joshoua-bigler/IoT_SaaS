import grpc
import queue
import os
import threading
from dotenv import load_dotenv
from concurrent import futures
from google.protobuf.empty_pb2 import Empty
from iot_libs.proto.hub_pb2_grpc import HubServicer, add_HubServicer_to_server
# local
from hub.gls.gls import logger
from hub.buffer import NumericScalarMetricsBuffer, DeviceStatusBuffer
from hub.processes import check_device_status


class HubService(HubServicer):
  ''' Service for receiving metrics from devices. '''

  def __init__(self, metrics_buffer: queue.Queue, device_status_buffer: queue.Queue):
    super().__init__()
    self.metrics_buffer = metrics_buffer
    self.device_status_buffer = device_status_buffer

  def SendNumericScalarValues(self, request_iterator, context) -> Empty:
    try:
      for request in request_iterator:
        logger.info(f'Received metrics: \n{request}')
        self.metrics_buffer.queue.put(request)
      return Empty()
    except Exception as exc:
      logger.error(f'Error in SendNumericData: {exc}')
      context.set_details(f'Error processing data: {str(exc)}')
      context.set_code(grpc.StatusCode.INTERNAL)
      return Empty()

  def SendDeviceStatus(self, request, context) -> Empty:
    try:
      logger.info(f'Received Device Status: \n{request}')
      self.device_status_buffer.queue.put(request)
      return Empty()
    except Exception as exc:
      logger.error(f'Error in SendDeviceStatus: {exc}')
      context.set_details(f'Error processing device status: {str(exc)}')
      context.set_code(grpc.StatusCode.INTERNAL)
      return Empty()


def main(host: str, port: str | int) -> None:
  metrics_buffer = NumericScalarMetricsBuffer(batch_size=int(os.getenv('BATCH_SIZE', 2)), queue=queue.Queue())
  device_status_buffer = DeviceStatusBuffer(batch_size=int(os.getenv('BATCH_SIZE', 1)), queue=queue.Queue())
  metrics_thread = threading.Thread(target=metrics_buffer.process)
  device_status_thread = threading.Thread(target=device_status_buffer.process)
  check_device_status_thread = threading.Thread(target=check_device_status,
                                                args=(os.getenv('TENANT_IDENTIFIER', '100000'),
                                                      int(os.getenv('CHECK_DEVICE_STATUS_INTERVAL_SECONDS'), 20)),
                                                daemon=True)
  metrics_thread.start()
  device_status_thread.start()
  check_device_status_thread.start()
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  add_HubServicer_to_server(
      HubService(metrics_buffer=metrics_buffer, device_status_buffer=device_status_buffer), server)
  server.add_insecure_port(f'{host}:{port}')
  try:
    server.start()
    server.wait_for_termination()
  except KeyboardInterrupt:
    logger.info('KeyboardInterrupt: Stopping server')
    server.stop(0)
    metrics_buffer.shutdown_event.set()
    device_status_buffer.shutdown_event.set()
    metrics_thread.join()
    device_status_thread.join()
    logger.info('Server stopped')


if __name__ == '__main__':
  logger.info('Starting gRPC server')
  load_dotenv()
  main(host=os.getenv('GRPC_HOST', '0.0.0.0'), port=os.getenv('GRPC_PORT', '50051'))

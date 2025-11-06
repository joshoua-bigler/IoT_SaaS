import threading
import traceback
import os
import time
# local
from edge_device.gls.gls import logger
from edge_device.gls.manager_gls import device, grpc_client, sim_manager
from edge_device.api.ws_client import ws_manager
from edge_device.api.http import register_device

stop_event = threading.Event()


def main(device_state_thread: threading.Thread):
  grpc_client.connect()
  register_device(uri=os.getenv('DEVICE_MANAGEMENT_HTTP_URI'), device=device, timezone=os.getenv('TIMEZONE'))
  websocket_thread = threading.Thread(target=ws_manager,
                                      args=(os.getenv('DEVICE_MANAGEMENT_WEBSOCKET_URI'), device),
                                      daemon=True)
  sim_manager.start_simulations()
  websocket_thread.start()
  device_state_thread.start()
  while not stop_event.is_set():
    time.sleep(1)


if __name__ == '__main__':
  logger.info('Start edge device.')
  device_state_thread = threading.Thread(target=device.send_device_state,
                                         args=(grpc_client, int(os.getenv('DEVICE_STATE_INTERVAL_SECONDS'))),
                                         daemon=True)
  try:
    main(device_state_thread=device_state_thread)
  except KeyboardInterrupt:
    logger.info('Stop edge device on keyboard interrupt')
  except Exception as exc:
    logger.critical('Stop edge device on exception.')
    logger.critical(traceback.format_exc())
  finally:
    stop_event.set()
    device.stop_event.set()
    grpc_client.close()
    sim_manager.stop_simulations()

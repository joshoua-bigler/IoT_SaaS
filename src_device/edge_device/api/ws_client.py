import json
import traceback
from typing import Callable
from websockets.exceptions import ConnectionClosed, WebSocketException, ConnectionClosedOK
from websockets.sync.client import connect, ClientConnection
from iot_libs.schemas.websocket_schemas import CommandMessage, RequestConnectMessage, CommandResponseMessage, SensorManagementMessage, SensorCommandMessage
from iot_libs.const.edge_device import WsSensorCommands, WsGeneralCommands, WsMessageTypes
# local
from edge_device.device import Device
from edge_device.gls.gls import logger
from edge_device.gls.manager_gls import sensor_manager
from edge_device.utils.decorators import retry
from edge_device.sensors.manager import create_sensor
from edge_device.gls.manager_gls import sim_manager


def sensor_management_messages(message: dict, **kwargs) -> CommandResponseMessage:
  data = None
  try:
    match message['command']:
      case WsSensorCommands.ADD_SENSOR.value:
        validate_message = SensorCommandMessage.model_validate(message)
        sensor = create_sensor(sensor_identifier=validate_message.sensor_identifier,
                               sensor_type=validate_message.sensor_type,
                               path=validate_message.path,
                               sampling_interval=validate_message.sampling_interval,
                               data=validate_message.data)
        response_message = sensor_manager.add_sensor(sensor=sensor)
        sim_manager.schedule_restart()
      case WsSensorCommands.REMOVE_SENSOR.value:
        validate_message = SensorCommandMessage.model_validate(message)
        metric_identifier = f'{validate_message.sensor_type}.{validate_message.sensor_identifier}'
        response_message = sensor_manager.remove_sensor(metric_identifier=metric_identifier)
        sim_manager.schedule_restart()
      case WsSensorCommands.GET_SENSORS.value:
        validate_message = SensorManagementMessage.model_validate(message)
        data = sensor_manager.get_sensors()
        response_message = f'{len(data)} sensor(s) found' if data else 'No sensors found'
      case _:
        return CommandResponseMessage(status='failure',
                                      message=f'The command {message['command']} is not available',
                                      message_id=message['message_id'])
    return CommandResponseMessage(status='success',
                                  message=response_message,
                                  message_id=message['message_id'],
                                  data=data if data else None)
  except ValueError as exc:
    return CommandResponseMessage(status='failure', message=str(exc), message_id=message['message_id'])
  except Exception as exc:
    return CommandResponseMessage(status='failure',
                                  message=f'An unexpected error occurred: {str(exc)}',
                                  message_id=message['message_id'])


class MessageHandler:
  ''' Handle messages and commands from the websocket server. '''

  def __init__(self):
    # yapf: disable
    self.message_handlers: dict[str, Callable] = {
      WsMessageTypes.COMMAND.value: self.command,
      WsMessageTypes.SENSOR_MANAGEMENT.value: lambda message, **kwargs: sensor_management_messages(message=message, **kwargs),
      WsMessageTypes.CONNECT_ACK.value: lambda message, **kwargs: logger.info(f'Websocket connection established')
    }
    self.command_handlers: dict[str, Callable] = {WsGeneralCommands.GET_CONNECTION_STATE.value: lambda **kwargs: {'status': 'online'}}
    # yapf: enable

  def message(self, message: dict, url: str, connection: ClientConnection, **kwargs) -> None:
    message_type = message.get('message_type')
    handler = self.message_handlers.get(message_type)
    if handler:
      try:
        response = handler(message=message, **kwargs)
        if response:
          logger.info(f'Sending response to {url}')
          connection.send(response.model_dump_json())
      except Exception as exc:
        logger.error(f'Error handling message {message_type}: {exc}\n{traceback.format_exc()}')
        return CommandResponseMessage(status='failure', message=str(exc), message_id=message.message_id)
    else:
      logger.warning(f'Unknown type: {message_type}')
      return CommandResponseMessage(status='failure',
                                    message=f'Message type: {message_type} not available',
                                    message_id=message.message_id)

  def command(self, message: dict, **kwargs) -> CommandResponseMessage:
    message = CommandMessage.model_validate(message)
    command = message.command
    command_handler = self.command_handlers.get(command)
    if command_handler:
      response_data = command_handler(data=message.data)
      return CommandResponseMessage(status='success',
                                    message=f'Command {command} executed',
                                    message_id=message.message_id,
                                    data=response_data)
    logger.warning(f'Unknown command received: {command}')
    return CommandResponseMessage(status='failure',
                                  message=f'Unknown command received: {command}',
                                  message_id=message.message_id)


@retry((Exception, WebSocketException, ConnectionClosed, ConnectionClosedOK, ConnectionRefusedError), delay=5)
def ws_manager(uri: str, device: Device, endpoint: str = '/ws/v1/tenants/devices', message_handler: MessageHandler = None) -> None:
  url = f'{uri}{endpoint}'
  message_handler = message_handler if message_handler else MessageHandler()
  with connect(url) as connection:
    init_message = RequestConnectMessage(tenant_identifier=device.tenant_identifier,
                                         device_identifier=device.device_identifier)
    connection.send(init_message.model_dump_json())
    while True:
      try:
        message = json.loads(connection.recv())
        logger.info(f'{url}: {message}')
        message_handler.message(message=message, device=device, url=url, connection=connection)
      except json.JSONDecodeError:
        logger.error('Failed to decode JSON message from server')

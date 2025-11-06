import asyncio
import json
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
from iot_libs.schemas.websocket_schemas import ConnectAckMessage, CommandMessage, SensorCommandMessage
# local
from device_mgmt.schemas.http_response_schemas import ErrorResponse, BaseResponse, SuccessResponse
from device_mgmt.gls.gls import logger

TenantWebsockets = Dict[str, Dict[str, WebSocket]]


class WebsocketsManager:
  ''' Manage the WebSocket connections. '''

  def __init__(self):
    self.connected_clients: TenantWebsockets = {}
    self.pending_commands: Dict[str, asyncio.Future] = {}

  def add_client(self, tenant_identifier: str, device_identifier: str, websocket: WebSocket):
    ''' Add the WebSocket client to the connected clients. '''
    if tenant_identifier not in self.connected_clients:
      self.connected_clients[tenant_identifier] = {}
    self.connected_clients[tenant_identifier][device_identifier] = websocket

  def remove_client(self, tenant_identifier: str, device_identifier: str):
    ''' Remove the WebSocket client from the connected clients. '''
    if tenant_identifier in self.connected_clients and device_identifier in self.connected_clients[tenant_identifier]:
      del self.connected_clients[tenant_identifier][device_identifier]

  def get_client(self, tenant_identifier: str, device_identifier: str) -> WebSocket:
    return self.connected_clients.get(tenant_identifier, {}).get(device_identifier)

  def get_queue(self, tenant_identifier: str, device_identifier: str) -> asyncio.Queue:
    return self.message_queues[tenant_identifier][device_identifier]

  async def websocket_listener(self, tenant_identifier: str, device_identifier: str, websocket: WebSocket):
    ''' Listen to the WebSocket connection. '''
    try:
      while True:
        message = await websocket.receive_text()
        data = json.loads(message)
        if data.get('type') == 'websocket.close':
          logger.info(f'Close connection request received from device {device_identifier}')
          await websocket.close()
          self.remove_client(tenant_identifier=tenant_identifier, device_identifier=device_identifier)
        message_id = data.get('message_id')
        if message_id and message_id in self.pending_commands:
          future = self.pending_commands.pop(message_id)
          future.set_result(data)
        else:
          logger.info(f'Received message from device {device_identifier}: {data}')
    except WebSocketDisconnect:
      logger.warning(f'Device {device_identifier} disconnected')
      self.remove_client(tenant_identifier, device_identifier)

  async def _send_message(self, websocket: WebSocket, message: CommandMessage | ConnectAckMessage) -> BaseResponse: # yapf: disable
    ''' Send message to websocket client. '''
    try:
      await websocket.send_text(message.model_dump_json())
    except asyncio.TimeoutError:
      return ErrorResponse(status='error',
                           message=f'Timed out waiting for response from device {message.device_identifier}')
    except WebSocketDisconnect:
      self.remove_client(message.tenant_identifier, message.device_identifier)
      return ErrorResponse(
          status='error',
          message=
          f'WebSocket disconnected for tenant {message.tenant_identifier} with device {message.device_identifier}')
    except Exception as exc:
      return ErrorResponse(
          status='error',
          message=f'Error sending command to tenant {message.tenant_identifier} with device {message.device_identifier}',
          details={'error': str(exc)})

  async def send_message(self, message: CommandMessage) -> BaseResponse:
    ''' Send command to websocket client, without waiting for response. '''
    websocket = self.get_client(message.tenant_identifier, message.device_identifier)
    if not websocket:
      return ErrorResponse(status='error',
                           message=f'No active WebSocket connection for device {message.device_identifier}')
    return await self._send_message(websocket=websocket, message=message)

  async def send_message_with_response(self,
                                       message: CommandMessage | SensorCommandMessage,
                                       timeout: int = 30) -> BaseResponse:
    ''' Send command to websocket client, and wait for response. '''
    websocket = self.get_client(message.tenant_identifier, message.device_identifier)
    if not websocket:
      return ErrorResponse(status='error',
                           message=f'No active WebSocket connection for device {message.device_identifier}')
    future = asyncio.get_event_loop().create_future()
    self.pending_commands[str(message.message_id)] = future
    send_response = await self._send_message(websocket=websocket, message=message)
    if isinstance(send_response, ErrorResponse):
      return send_response
    try:
      response = await asyncio.wait_for(future, timeout=timeout)
      if response['status'] == 'success':
        if response['message_type'] == 'command_response':
          return SuccessResponse(status=response['status'], message=response['message'], data=response['data'])
      else:
        return ErrorResponse(status=response['status'], message=response['message'], data=response['data'])
    except asyncio.TimeoutError:
      return ErrorResponse(status='error',
                           message=f'Timed out waiting for response from device {message.device_identifier}')

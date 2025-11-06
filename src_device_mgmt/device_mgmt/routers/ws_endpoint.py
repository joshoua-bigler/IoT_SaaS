import json
from fastapi import APIRouter, WebSocket
from iot_libs.schemas.websocket_schemas import ConnectAckMessage, RequestConnectMessage

# local
from device_mgmt.gls.ws_gls import websockets_manager

router = APIRouter()


@router.websocket('/ws/v1/tenants/devices')
async def websocket_endpoint(websocket: WebSocket):
  await websocket.accept()
  message = await websocket.receive_text()
  request = RequestConnectMessage.model_validate_json(message)
  websockets_manager.add_client(tenant_identifier=request.tenant_identifier,
                                device_identifier=request.device_identifier,
                                websocket=websocket)
  response = ConnectAckMessage(status='success', message='Connected to websocket')
  await websocket.send_text(response.model_dump_json())
  await websockets_manager.websocket_listener(tenant_identifier=request.tenant_identifier,
                                              device_identifier=request.device_identifier,
                                              websocket=websocket)

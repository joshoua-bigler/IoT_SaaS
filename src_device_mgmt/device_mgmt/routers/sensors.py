from fastapi import APIRouter
from fastapi.responses import JSONResponse
from iot_libs.schemas.websocket_schemas import SensorCommandMessage, SensorManagementMessage
from iot_libs.const.edge_device import WsSensorCommands
# local
from device_mgmt.schemas.http_request_schemas import SensorSchema, BaseSchema
from device_mgmt.gls.gls import logger
from device_mgmt.gls.ws_gls import websockets_manager

router = APIRouter()

TAGS = ['Sensors']


@router.get('/api/v1/tenants/devices/sensors', tags=TAGS)
async def get_sensor_state(request: BaseSchema) -> JSONResponse:
  logger.info(f'Get sensors from: device identifier: {request.device_identifier}, tenant identifier: {request.tenant_identifier}') # yapf: disable
  message = SensorManagementMessage(command=WsSensorCommands.GET_SENSORS.value,
                                    tenant_identifier=request.tenant_identifier,
                                    device_identifier=request.device_identifier)
  return await websockets_manager.send_message_with_response(message=message)


@router.post('/api/v1/tenants/devices/sensors/add', tags=TAGS)
async def add_sensor(request: SensorSchema) -> JSONResponse:
  logger.info(f'Add_sensor: {request}')
  message = SensorCommandMessage(command=WsSensorCommands.ADD_SENSOR.value,
                                 tenant_identifier=request.tenant_identifier,
                                 device_identifier=request.device_identifier,
                                 sensor_identifier=request.sensor_identifier,
                                 sensor_type=request.sensor_type,
                                 path=request.path,
                                 sampling_interval=request.sampling_interval,
                                 data=request.data)
  return await websockets_manager.send_message_with_response(message=message)


@router.delete('/api/v1/tenants/devices/sensors/remove', tags=TAGS)
async def remove_sensor(request: SensorSchema) -> JSONResponse:
  logger.info(f'Remove_sensor: {request}')
  message = SensorCommandMessage(command=WsSensorCommands.REMOVE_SENSOR.value,
                                 tenant_identifier=request.tenant_identifier,
                                 device_identifier=request.device_identifier,
                                 sensor_identifier=request.sensor_identifier,
                                 sampling_interval=request.sampling_interval,
                                 sensor_type=request.sensor_type,
                                 data=request.data)
  return await websockets_manager.send_message_with_response(message=message)

from fastapi import APIRouter, HTTPException, status
from iot_libs.schemas.websocket_schemas import CommandMessage
# local
import device_mgmt.database.device_queries as queries
from device_mgmt.schemas.http_request_schemas import Devices, DeviceTypeSchema
from device_mgmt.schemas.http_response_schemas import SuccessfulDevice, FailedDevice, BaseResponse, DeviceStatusResponse
from device_mgmt.gls.gls import logger, db_manager
from device_mgmt.gls.ws_gls import websockets_manager

router = APIRouter()

TAGS = ['Devices']


def handle_db_connection_error(exc: Exception, action: str):
  logger.error(f'Database connection error during {action}: {exc}')
  raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f'Database connection error occurred while {action}.') # yapf: disable


def handle_unexpected_error(exc: Exception, action: str):
  logger.error(f'Exception during {action}: {exc}')
  raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'An Exception occurred while {action}.') # yapf: disable


@router.post('/api/v1/tenants/devices/register', tags=TAGS)
def register_device(device_description: DeviceTypeSchema) -> BaseResponse:
  logger.info(f'Register_device: {device_description}')
  with db_manager(f'tenant_{device_description.tenant_identifier}') as conn:
    try:
      message = queries.register_device(conn=conn,
                                        device_identifier=device_description.device_identifier,
                                        timezone=device_description.timezone)
    except ConnectionError as exc:
      handle_db_connection_error(exc, f'registering the device {device_description.tenant_identifier}')
    except Exception as exc:
      handle_unexpected_error(exc, f'registering the device {device_description.tenant_identifier}')
  return BaseResponse(status='success', message=message)


@router.delete('/api/v1/tenants/devices/remove', tags=TAGS)
def remove_device(devices: Devices):
  logger.info(f'Remove_devices: {devices.device_identifier}')
  with db_manager(f'tenant_{devices.tenant_identifier}') as conn:
    try:
      message = queries.remove_devices(conn=conn, device_identifiers=devices.device_identifier)
    except ConnectionError as exc:
      handle_db_connection_error(exc, f'removing the device.')
    except Exception as exc:
      handle_unexpected_error(exc, f'removing the device.')
  return BaseResponse(status='success', message=message)


@router.post('/api/v1/tenants/devices/status', tags=TAGS)
def get_device_status(devices: Devices) -> DeviceStatusResponse:
  logger.info(f'Get device status: {devices}')
  with db_manager(f'tenant_{devices.tenant_identifier}') as conn:
    try:
      message = queries.get_device_status(conn=conn, device_identifiers=devices.device_identifier)
      successful_devices = [SuccessfulDevice(**device) for device in message['devices']]
      failed_devices = [
          FailedDevice(device_identifier=device_id, error='Device does not exist')
          for device_id in message['non_existing_devices']
      ]
    except ConnectionError as exc:
      handle_db_connection_error(exc, f'updating the device {devices.device_identifier}')
    except Exception as exc:
      handle_unexpected_error(exc, f'getting the device status for tenant {devices.tenant_identifier}')
  return DeviceStatusResponse(status='success',
                              message='Device statuses retrieved successfully',
                              devices=successful_devices,
                              failed_devices=failed_devices)


@router.put('/api/v1/tenants/devices/update', tags=TAGS)
def udpate_device(device_type: DeviceTypeSchema) -> BaseResponse:
  logger.info(f'Update_device: {device_type}')
  with db_manager(f'tenant_{device_type.tenant_identifier}') as conn:
    try:
      message = queries.update_device(conn=conn, device_type=device_type)
    except ConnectionError as exc:
      handle_db_connection_error(exc, f'updating the device {device_type.device_identifier}')
    except Exception as exc:
      handle_unexpected_error(exc, f'updating the device {device_type.device_identifier}')
  return BaseResponse(status='success', message=message)


@router.post('/api/v1/tenants/devices/command', tags=TAGS)
async def send_command(request: CommandMessage):
  message = CommandMessage(command=request.command,
                           tenant_identifier=request.tenant_identifier,
                           device_identifier=request.device_identifier)
  return await websockets_manager.send_message_with_response(message=message)

import time
import pandas as pd
from datetime import datetime, timedelta, timezone
from iot_libs.proto.enums import DeviceHealthStatus
# local
from hub.queries.devices import get_device_status, update_device_status
from hub.gls.gls import logger, db_manager


def get_offline_devices(df_status: pd.DataFrame, timeout_seconds: int) -> pd.DataFrame:
  ''' Get devices that are offline based on the timeout. '''
  current_time = datetime.now(timezone.utc)
  df_status['latest_alive'] = pd.to_datetime(df_status['latest_alive']).dt.tz_localize('UTC')
  offline_mask = ((current_time - df_status['latest_alive'])> timedelta(seconds=timeout_seconds)) & (df_status['status'] != DeviceHealthStatus.OFFLINE.value) # yapf: disable
  offline_devices_df = df_status[offline_mask].copy()
  offline_devices_df['status'] = DeviceHealthStatus.OFFLINE.value
  return offline_devices_df[['device_identifier', 'status']]


def check_device_status(tenant_identifier: str, sleep_seconds: int = 20, timeout_seconds: int = 10):
  ''' Check the device status and update the status to offline if the device is offline. '''
  time.sleep(sleep_seconds)
  while True:
    with db_manager(f'tenant_{tenant_identifier}') as conn:
      try:
        df_status = get_device_status(conn)
      except Exception as exc:
        logger.error(f'Failed to get device status: {exc}')
      if df_status.empty:
        logger.warning('No devices found in the database!')
        continue
      else:
        df_offline_devices = get_offline_devices(df_status=df_status, timeout_seconds=timeout_seconds)
        if not df_offline_devices.empty:
          logger.warning(f'Update device status to offline for devices: {df_offline_devices}')
          update_device_status(batch=df_offline_devices, conn=conn)
    time.sleep(sleep_seconds)

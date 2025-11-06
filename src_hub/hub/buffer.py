import threading
from abc import ABC, abstractmethod
from collections import defaultdict
from sqlalchemy.orm import scoped_session
from queue import Empty, Queue
from typing import Callable
from iot_libs.proto.hub_pb2 import NumericScalarValues, DeviceStatus
# local
from hub.gls.gls import logger, db_manager
from hub.queries.metrics import update_metrics
from hub.queries.devices import update_device_status

DatabaseQuery = Callable[[list, scoped_session], None]


def check_tenant_identifier(metrics_batch: list[NumericScalarValues]):
  ''' Check if all metrics in the batch have the same tenant identifier. '''
  tenant_identifiers = []
  for metric in metrics_batch:
    tenant_identifiers.append(metric.tenant_identifier)
  tenant_identifiers = set(tenant_identifiers)
  if len(tenant_identifiers) > 1:
    raise ValueError('All metrics in a batch must have the same tenant identifier.')
  return tenant_identifiers.pop()


def count_metrics_per_device(metrics_batch: list[NumericScalarValues]) -> str:
  ''' Count the number of metrics per device in the batch. '''
  device_metrics_count = defaultdict(int)
  for metric in metrics_batch:
    device_metrics_count[metric.device_identifier] += 1
  return ', '.join([f'device {device}: {count}' for device, count in device_metrics_count.items()])


def write_to_database(batch: list[NumericScalarValues],
                      database_query: DatabaseQuery,
                      tenant_identifier: str = '100000',
                      log: bool = True):
  ''' Write the batch data to the database. 

      Parameters
      ----------
      batch:              The data to write to the database.
      database_query:     The database query callable to execute.
      tenant_identifier:  The tenant identifier.
      log:                Log the data written to the database.
  '''
  tenant_identifier = check_tenant_identifier(batch)
  try:
    with db_manager(f'tenant_{tenant_identifier}') as conn:
      if log:
        device_counts = count_metrics_per_device(batch)
        logger.info(f'Writing to tenant database: {tenant_identifier}, {device_counts} metrics.')
      database_query(batch=batch, conn=conn)
  except Exception as exc:
    logger.error(f'Failed to write to database: {exc}')


class Buffer(ABC):
  ''' Metrics buffer before the metrics will be written into the database. '''

  def __init__(self, queue: Queue, batch_size: int = 5):
    ''' Paramters
        ---------
        queue:      The queue to read the data from.
        batch_size: The number of data to write to the database at once.
    '''
    self.shutdown_event = threading.Event()
    self.queue = queue
    self.batch_size = batch_size

  def process(self):
    ''' Process the queue data. '''
    batches: dict[list] = defaultdict(list)
    while not self.shutdown_event.is_set() or not self.queue.empty():
      try:
        metric = self.queue.get(timeout=1)
        if metric is None:
          break
        batches[metric.tenant_identifier].append(metric)
        if len(batches[metric.tenant_identifier]) >= self.batch_size:
          self.write_data(batches[metric.tenant_identifier])
          batches[metric.tenant_identifier] = []
        self.queue.task_done()
      except Empty:
        continue
    for _, batch in batches.items():
      self.write_data(batch=batch)

  @abstractmethod
  def write_data(self, batch: list[NumericScalarValues] | list[DeviceStatus]):
    ''' Write the queue data to the database. '''
    pass


class NumericScalarMetricsBuffer(Buffer):
  ''' Buffer implementation for writing numeric scalar metrics to the database. '''

  def write_data(self, batch: list[NumericScalarValues]):
    try:
      logger.info('Insert metrics into database')
      write_to_database(batch=batch, database_query=update_metrics, log=True)
    except Exception as exc:
      logger.error(f'Failed to write metrics batch to database: {exc}', exc_info=True)


class DeviceStatusBuffer(Buffer):
  ''' Buffer implementation for writing device metrics to the database. '''

  def write_data(self, batch: list[DeviceStatus]):
    try:
      logger.info('Updating device status')
      write_to_database(batch=batch, database_query=update_device_status, log=True)
    except Exception as exc:
      logger.error(f'Failed to write metrics batch to database: {exc}', exc_info=True)

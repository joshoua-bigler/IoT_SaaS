import time
from functools import wraps
# local
from edge_device.gls.gls import logger


def retry(ExceptionToCheck: Exception | tuple, delay: int = 60):
  ''' Retry function using an exponential backoff.

      Parameters
      ----------
      ExceptionToCheck: The exception to check. May be a tuple of exceptions to check
      delay:            Initial delay between retries in seconds
  '''

  def deco_retry(f):

    @wraps(f)
    def f_retry(*args, **kwargs):
      while True:
        try:
          return f(*args, **kwargs)
        except ExceptionToCheck as exc:
          msg = f'{exc}, Retrying in {delay} seconds...'
          logger.error(msg)
          time.sleep(delay)

    return f_retry

  return deco_retry

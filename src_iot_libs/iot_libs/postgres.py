import logging
import pandas as pd
import threading
import traceback
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, CursorResult, URL
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from sqlalchemy.sql import text
from typing import Callable

logger = logging.getLogger(__name__)


class EngineManager:
  ''' Thread safe engine manager. '''
  engines = {}

  @classmethod
  def get_engine(cls, db_name: str, url: URL) -> Engine:
    if db_name not in cls.engines:
      cls.engines[db_name] = create_engine(url, pool_pre_ping=True)
    return cls.engines[db_name]


class PostgresManager:
  ''' Thread safe posgresql database connection manager. '''

  def __init__(self, username: str, password: str, host: str, port: int | str = 5432):
    ''' Parameters
        ----------
        username:  Name of the user to connect to the database.
        password:  Password of the user to connect to the database.
        host:      Hostname of the database server.
        port:      Port of the database server.
    '''
    self.username = username
    self.password = password
    self.host = host
    self.local_data = threading.local()  # Thread-local storage
    self.port = int(port)

  def __call__(self, db_name: str):
    if not hasattr(self.local_data, 'Session') or self.local_data.db_name != db_name:
      url = URL.create('postgresql+psycopg',
                       username=self.username,
                       password=self.password,
                       host=self.host,
                       database=db_name,
                       port=self.port)
      engine = EngineManager.get_engine(db_name, url)
      self.local_data.session_factory = sessionmaker(bind=engine)
      self.local_data.Session = scoped_session(self.local_data.session_factory)
      self.local_data.db_name = db_name
    return self

  def get_session(self) -> Session:
    if not hasattr(self.local_data, 'Session'):
      raise ValueError('Database name not set. Use the object as a callable with dbname first.')
    return self.local_data.Session()

  def remove_session(self):
    if hasattr(self.local_data, 'Session'):
      self.local_data.Session.remove()
      del self.local_data.Session

  def __enter__(self) -> Session:
    return self.get_session()

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.remove_session()

  def __repr__(self) -> str:
    return self.__str__()

  def __str__(self) -> str:
    return f'PostgresManager(username={self.username}, password=***, host={self.host})'


def dict_row(result: CursorResult, row: list):
  return {col: val for col, val in zip(result.keys(), row)}


class PostgreException(Exception):
  pass


def execute_query(conn: Engine | Session, query: str, params: dict | list[dict] = None) -> CursorResult:
  if isinstance(conn, Engine) and conn.pool.status == 'closed':
    logger.error('Connection is closed.')
    raise PostgreException('Connection is closed.')
  try:
    if isinstance(conn, Engine):
      with conn.connect() as conn:
        with conn.begin():
          result = conn.execute(text(query), params or {})
    elif isinstance(conn, Session):
      with conn.begin():
        result = conn.execute(text(query), params or {})
    else:
      raise ValueError('Invalid connection type.')
  except Exception as exc:
    logger.error(f'Failed to execute query: "{query}" with params: {params}. Error: {exc}')
    raise PostgreException(f'Failed to execute query: {traceback.format_exc()}')
  return result


def execute_select_query(conn: Engine | Session,
                         query: str,
                         params: dict = None,
                         row_factory: None | Callable = None) -> list | pd.DataFrame:
  result = execute_query(conn=conn, query=query, params=params)
  data = result.fetchall()
  if row_factory:
    return [row_factory(result=result, row=row) for row in data]
  columns = result.keys()
  return pd.DataFrame(data, columns=columns)

from sqlalchemy import create_engine
from sqlalchemy.sql import text
# local
from db_manager.gls.gls import logger


def create_user(username: str, password: str) -> str:
  return f"create role {username} with superuser createdb createrole inherit noreplication bypassrls login password '{password}' connection limit -1"


def create_db(username: str,
              password: str,
              tenant_identifier: str,
              host: str = '127.0.0.1',
              port: int | str = 5432) -> None:
  ''' Create a new database for a tenant. '''
  url = f'postgresql+psycopg://{username}:{password}@{host}:{port}/postgres'
  engine = create_engine(url)
  connection = engine.connect()
  db_name = f'tenant_{tenant_identifier}'
  try:
    connection.execution_options(isolation_level='AUTOCOMMIT')
    check_query = text(f'select 1 from pg_database where datname = :db_name')
    result = connection.execute(check_query, {'db_name': db_name}).fetchone()
    if not result:
      connection.execute(text(f'create database {db_name}'))
      logger.info(f'Database "{db_name}" created successfully.')
    else:
      logger.info(f'Database "{db_name}" already exists.')
  finally:
    connection.close()
    engine.dispose()

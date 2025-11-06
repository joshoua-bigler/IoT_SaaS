import os
from iot_libs.postgres import execute_query
# local
from db_manager.gls.gls import db_manager, logger
from db_manager.schemas.devices import create_devices_table
from db_manager.schemas.metrics import create_metrics_table
from db_manager.schemas.numeric_scalar_values import create_numeric_scalar_values_table
from db_manager.schemas.timescale import create_hypertable, create_index, enable_timescale
from db_manager.schemas.postgre import create_user, create_db
from db_manager.schemas.setup import create_lree_extension, create_pgcrypto_extension
from db_manager.schemas.paths import create_metric_paths_table


def main():
  logger.info('Start db_manager!')
  logger.info(str(db_manager))
  create_db(username=os.getenv('DB_SUPERUSER_USERNAME', 'postgres'),
            password=os.getenv('DB_SUPERUSER_PASSWORD', 'postgres'),
            tenant_identifier=os.getenv('TENANT_IDENTIFIER', '100000'),
            host=os.getenv('DB_HOST', '127.0.0.1'),
            port=os.getenv('DB_PORT', '50000'))
  with db_manager(f'tenant_{os.getenv("TENANT_IDENTIFIER")}') as conn:
    # execute_query(conn, create_user(username=os.getenv('DB_ADMIN_USERNAME'), password=os.getenv('DB_ADMIN_PASSWORD')))
    execute_query(conn, enable_timescale())
    execute_query(conn, create_lree_extension())
    execute_query(conn, create_pgcrypto_extension())
    execute_query(conn, create_devices_table())
    execute_query(conn, create_metric_paths_table())
    execute_query(conn, create_metrics_table())
    execute_query(conn, create_numeric_scalar_values_table())
    execute_query(conn, create_hypertable(table='numeric_scalar_values'))
    execute_query(conn, create_index(table='numeric_scalar_values'))


if __name__ == '__main__':
  main()

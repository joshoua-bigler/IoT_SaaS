import os
from dotenv import load_dotenv
from iot_libs.logger import LoggerSetup
from iot_libs.postgres import PostgresManager

load_dotenv()
logger = LoggerSetup().get_logger()
db_manager = PostgresManager(username=os.getenv('DB_SUPERUSER_USERNAME'),
                             password=os.getenv('DB_SUPERUSER_PASSWORD'),
                             host=os.getenv('DB_HOST'),
                             port=os.getenv('DB_PORT'))

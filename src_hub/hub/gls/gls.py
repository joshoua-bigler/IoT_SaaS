import os
from iot_libs.logger import LoggerSetup
from iot_libs.postgres import PostgresManager
from dotenv import load_dotenv

load_dotenv()
logger = LoggerSetup().get_logger()
db_manager = PostgresManager(username=os.getenv('DB_USERNAME'),
                             password=os.getenv('DB_PASSWORD'),
                             host=os.getenv('DB_HOST'),
                             port=os.getenv('DB_PORT', 50000))

import os
import uvicorn
import mlflow
import requests
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# local
from analytics_api.gls.gls import logger
from analytics_api.graphql import schema
from analytics_api.routes import home


def create_app() -> FastAPI:
  app = FastAPI(title='IoT Web API', description='IoT Web API', version='0.0.1')
  app.include_router(home.router, include_in_schema=False)
  app.include_router(schema.graphql_app, prefix='/graphql')
  app.add_middleware(
      CORSMiddleware,
      allow_origins=['*'],
      allow_credentials=True,
      allow_methods=['*'],
      allow_headers=['*'],
  )
  return app


app = create_app()

if __name__ == '__main__':
  load_dotenv()
  debug = True if os.getenv('DEBUG') == 'True' else False
  mlflow_port = os.getenv('MLFLOW_PORT', 5000)
  logger.setLevel(logging.INFO)
  try:
    requests.get(f'http://localhost:{mlflow_port}', timeout=2)
    mlflow.set_tracking_uri(f'http://localhost:{mlflow_port}')
  except requests.exceptions.RequestException:
    logger.warning('MLflow server not reachable, skipping URI setup')
  try:
    uvicorn.run('main:app',
                host='127.0.0.1',
                port=8001,
                reload=debug,
                log_level='debug',
                workers=int(os.getenv('WORKERS', 1)))
  except KeyboardInterrupt:
    logger.info('Shutting down the server...')
  except Exception as e:
    logger.error(f'Error: {e}')
    logger.error('Shutting down the server...')

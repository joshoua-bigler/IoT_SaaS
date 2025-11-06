import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
# local
from device_mgmt.routers import home, devices, sensors, ws_endpoint
from device_mgmt.gls.gls import logger


def create_app() -> FastAPI:
  app = FastAPI(title='Iot Device Management API',
                description='Iot device management API for the MSE project work.',
                version='0.0.1')
  app.include_router(home.router, include_in_schema=False)
  app.include_router(devices.router)
  app.include_router(sensors.router)
  app.include_router(ws_endpoint.router)
  return app


app = create_app()

if __name__ == '__main__':
  load_dotenv()
  debug = True if os.getenv('DEBUG') == 'True' else False
  try:
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=debug, workers=int(os.getenv('WORKERS', 1)))
  except KeyboardInterrupt:
    logger.info('Shutting down the server...')
  except Exception as e:
    logger.error(f'Error: {e}')
    logger.error('Shutting down the server...')

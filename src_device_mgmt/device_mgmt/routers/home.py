from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get('/', response_class=HTMLResponse, tags=['Home'])
async def home():
  return '''
    <html>
      <head>
        <title>Device Management API</title>
      </head>
      <body>
        <h1>Welcome to the IoT Device Management API</h1>
        <p>This is the homepage of the Device Management API. Use the documentation to find out more about the available endpoints.</p>
        <a href='/docs'>API Documentation</a>
      </body>
    </html>
  '''

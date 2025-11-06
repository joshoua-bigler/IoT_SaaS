from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get('/', response_class=HTMLResponse, tags=['Home'])
async def home():
  return '''
    <html>
      <head>
        <title>IoT Analytics API</title>
      </head>
      <body>
        <h1>Welcome to the analytics api</h1>
        <p>Use the documentation to find out more about the available endpoints.</p>
        <a href='/graphql'>GraphQL</a>
      </body>
    </html>
  '''

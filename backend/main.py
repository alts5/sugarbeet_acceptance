from fastapi import *
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(CORSMiddleware,
               allow_origins=['http://localhost', 'http://127.0.0.1'],
               allow_headers=['*'],
               allow_methods=['*'],
               allow_credentials=True)

@app.post('/authenticate')
def authenticate():
    return 1
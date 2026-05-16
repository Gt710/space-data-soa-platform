from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def read_root():
    return {'service': 'mission-data', 'status': 'online'}


import os
import sys
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from sdks.novavision.src.base.service import Service
from sdks.novavision.src.base.bootstrap import Bootstrap
from sdks.novavision.src.base.auth import api_key_security
from sdks.novavision.src.helper.service import start_server, terminate_processes_and_cleanup


terminate_processes_and_cleanup(path="/storage/runtime/package", folderName="package")

bootstrap = {}
@asynccontextmanager
async def lifespan(app: FastAPI):
    bootstrap["bootstrap"] = Bootstrap().run()
    yield

app = FastAPI(lifespan=lifespan)


@app.post('/status')
async def status(access_token: str = Depends(api_key_security)):
    if "bootstrap" in bootstrap:
        return {"status": "open", "message": "Service is opened successfully"}
    return {"status": "loading", "message": "Server is still in the loading phase"}


@app.post('/api')
async def api(request: Request, access_token: str = Depends(api_key_security)):
    request_json = await request.json()
    json_data = json.dumps(request_json)
    resp = await Service(data=json_data, load=bootstrap['bootstrap']).run()
    return resp


if __name__ == "__main__":
    import os
    
    # Varsayılan port ve host ayarlarını SDK için tanımla (eğer dışarıdan boş gelirse)
    name = os.environ.get("NAME", "")
    if name:
        prefix = name.upper().replace("/", "_")
        os.environ.setdefault(f"{prefix}_SERVICE_HOST", "0.0.0.0")
        os.environ.setdefault(f"{prefix}_SERVICE_PORT", "8000")
        os.environ.setdefault(f"{prefix}_SERVICE_SSL", "DISABLE")

    start_server(app=app)
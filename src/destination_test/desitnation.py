import uvicorn
from fastapi import FastAPI
import logging
from fastapi import Request

from server.web_api.NodeRequest import NodeRequest

uvicorn_error = logging.getLogger("uvicorn.error")
uvicorn_error.disabled = True
uvicorn_access = logging.getLogger("uvicorn.access")
uvicorn_access.disabled = True
app = FastAPI()

@app.post("/monitoring")
async def test(req: NodeRequest, request: Request):
    smart_furniture_id = request.query_params.get("smart_furniture_id")
    by_user = f"by {req.username}" if req.username is not None else ""
    print(f"[{req.timestamp}]{smart_furniture_id} consumes: {req.realTimeConsumption} {by_user}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001, log_config=None)
# app/log.py
import time
import logging
from datetime import datetime
from typing import List, Union

from fastapi import FastAPI, HTTPException, Body, Request
import numpy as np
import joblib
import os
import uuid

LOG = logging.getLogger("iris_api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

MODEL_PATH = os.environ.get("MODEL_PATH", "/app/models/model.joblib")

app = FastAPI(title="Iris Prediction API (logging)")

# Try to load model at startup
model = None
@app.on_event("startup")
def load_model():
    global model
    try:
        model = joblib.load(MODEL_PATH)
        LOG.info("Loaded model from %s", MODEL_PATH)
    except Exception as e:
        LOG.exception("Failed loading model: %s", e)
        # don't crash; endpoints will return 503 until troubleshooting

@app.get("/", tags=["health"])
def root():
    """Healthcheck / quick info"""
    return {
        "status": "ok",
        "time": datetime.utcnow().isoformat() + "Z",
        "message": "Iris Prediction API (log.py) listening"
    }

@app.post("/predict/", tags=["predict"])
async def predict(request: Request, features: Union[List[float], List[List[float]]] = Body(..., example=[[5.1,3.5,1.4,0.2]])):
    """
    Predict endpoint.
    Accepts either:
      - one sample as [f1,f2,f3,f4]
      - multiple samples as [[f1,f2,f3,f4], [f1,f2,f3,f4], ...]
    Returns predictions and logging metadata (request id, latency).
    """
    if model is None:
        LOG.error("Model not loaded - returning 503")
        raise HTTPException(status_code=503, detail="Model not loaded")

    req_id = str(uuid.uuid4())
    start_ts = time.time()

    # Normalize incoming JSON shapes
    try:
        arr = np.array(features)
        # If single sample 1D, make it (1, n_features)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        elif arr.ndim > 2:
            raise ValueError("Bad feature dimensions")
    except Exception as e:
        LOG.exception("Bad input for request %s: %s", req_id, e)
        raise HTTPException(status_code=400, detail=f"Invalid features: {e}")

    # Run prediction
    try:
        preds = model.predict(arr)
        preds_list = preds.tolist()
    except Exception as e:
        LOG.exception("Prediction failed for request %s: %s", req_id, e)
        raise HTTPException(status_code=500, detail="Prediction failed")

    latency_ms = round((time.time() - start_ts) * 1000, 2)
    log_entry = {
        "request_id": req_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "input_shape": list(arr.shape),
        "predictions_count": len(preds_list),
        "latency_ms": latency_ms,
        "path": str(request.url.path),
        "client": request.client.host if request.client else None
    }
    LOG.info("RequestLog: %s", log_entry)

    return {
        "request_id": req_id,
        "predictions": preds_list,
        "latency_ms": latency_ms
    }

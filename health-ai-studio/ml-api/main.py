from fastapi import FastAPI
from app.schemas import PredictionRequest, PredictionResponse
from app.predictors import predict_diabetes, predict_heart, predict_parkinsons

app = FastAPI(title="Health AI Studio ML API", version="1.0.0")


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "service": "health-ai-studio-ml-api"}


@app.post("/predict/diabetes", response_model=PredictionResponse)
def diabetes_prediction(payload: PredictionRequest) -> PredictionResponse:
    return predict_diabetes(payload)


@app.post("/predict/heart", response_model=PredictionResponse)
def heart_prediction(payload: PredictionRequest) -> PredictionResponse:
    return predict_heart(payload)


@app.post("/predict/parkinsons", response_model=PredictionResponse)
def parkinsons_prediction(payload: PredictionRequest) -> PredictionResponse:
    return predict_parkinsons(payload)

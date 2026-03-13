from typing import Dict, List
from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    diseaseType: str
    patientId: str | None = None
    inputData: Dict[str, float] = Field(default_factory=dict)


class FeatureImportanceItem(BaseModel):
    feature: str
    importance: float


class PredictionResponse(BaseModel):
    riskPercentage: float
    confidenceScore: float
    riskCategory: str
    featureImportance: List[FeatureImportanceItem]
    explanation: str
    recommendations: List[str]

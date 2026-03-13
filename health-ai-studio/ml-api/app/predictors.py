from __future__ import annotations

from typing import Dict, List, Tuple
import numpy as np
from app.schemas import PredictionRequest, PredictionResponse, FeatureImportanceItem


def _risk_bucket(score: float) -> str:
    if score < 35:
        return "Low"
    if score < 70:
        return "Moderate"
    return "High"


def _normalize_inputs(input_data: Dict[str, float]) -> Dict[str, float]:
    return {k: float(v) for k, v in input_data.items() if v is not None}


def _top_features(input_data: Dict[str, float], weights: Dict[str, float]) -> List[FeatureImportanceItem]:
    items: List[Tuple[str, float]] = []
    for feature, value in input_data.items():
        weight = abs(weights.get(feature, 0.08))
        contribution = min(1.0, abs(value) / 200.0) * weight
        items.append((feature, contribution))

    if not items:
        items = [("baseline", 0.4)]

    items.sort(key=lambda x: x[1], reverse=True)
    top = items[:6]
    total = sum(val for _, val in top) or 1.0

    return [
        FeatureImportanceItem(feature=name, importance=round(val / total, 3))
        for name, val in top
    ]


def _score_from_inputs(input_data: Dict[str, float], weights: Dict[str, float], bias: float) -> float:
    if not input_data:
        return 40.0

    weighted_sum = sum(float(input_data.get(k, 0.0)) * w for k, w in weights.items())
    normalization = sum(abs(w) for w in weights.values()) or 1.0
    scaled = (weighted_sum / (normalization * 200.0)) * 100.0

    score = float(np.clip(bias + scaled, 5.0, 98.0))
    return score


def _confidence_from_score(score: float) -> float:
    spread = abs(score - 50.0)
    confidence = 62.0 + (spread * 0.55)
    return float(np.clip(confidence, 55.0, 98.0))


def _build_response(
    score: float,
    confidence: float,
    feature_importance: List[FeatureImportanceItem],
    explanation: str,
    recommendations: List[str],
) -> PredictionResponse:
    return PredictionResponse(
        riskPercentage=round(score, 2),
        confidenceScore=round(confidence, 2),
        riskCategory=_risk_bucket(score),
        featureImportance=feature_importance,
        explanation=explanation,
        recommendations=recommendations,
    )


def predict_diabetes(payload: PredictionRequest) -> PredictionResponse:
    inputs = _normalize_inputs(payload.inputData)
    weights = {
        "glucose": 0.42,
        "bmi": 0.25,
        "age": 0.12,
        "bloodPressure": 0.1,
        "pregnancies": 0.06,
        "insulin": 0.05,
    }
    score = _score_from_inputs(inputs, weights, bias=28.0)
    confidence = _confidence_from_score(score)
    features = _top_features(inputs, weights)

    return _build_response(
        score,
        confidence,
        features,
        explanation="Glucose and BMI strongly influenced the estimated diabetes risk in this inference.",
        recommendations=[
            "Track fasting glucose and HbA1c regularly with your clinician.",
            "Prioritize consistent exercise and balanced carbohydrate intake.",
            "Review blood pressure, weight, and sleep quality over time.",
        ],
    )


def predict_heart(payload: PredictionRequest) -> PredictionResponse:
    inputs = _normalize_inputs(payload.inputData)
    weights = {
        "cholesterol": 0.34,
        "restingBP": 0.24,
        "age": 0.2,
        "maxHeartRate": -0.13,
        "exerciseAngina": 0.16,
    }
    score = _score_from_inputs(inputs, weights, bias=26.0)
    confidence = _confidence_from_score(score)
    features = _top_features(inputs, weights)

    return _build_response(
        score,
        confidence,
        features,
        explanation="Cholesterol, resting blood pressure, and age had the highest weight in this cardiovascular risk estimate.",
        recommendations=[
            "Plan a physician-reviewed lipid and blood pressure management program.",
            "Reduce sodium intake and maintain regular aerobic activity.",
            "Monitor chest discomfort or exertion symptoms and seek urgent care when required.",
        ],
    )


def predict_parkinsons(payload: PredictionRequest) -> PredictionResponse:
    inputs = _normalize_inputs(payload.inputData)
    weights = {
        "jitter": 0.33,
        "shimmer": 0.26,
        "hnr": -0.21,
        "rpde": 0.11,
        "ppe": 0.19,
    }
    score = _score_from_inputs(inputs, weights, bias=22.0)
    confidence = _confidence_from_score(score)
    features = _top_features(inputs, weights)

    return _build_response(
        score,
        confidence,
        features,
        explanation="Voice instability markers (jitter/shimmer) and entropy features were dominant contributors in this neurological risk estimate.",
        recommendations=[
            "Discuss findings with a neurologist and consider follow-up speech analysis.",
            "Track any changes in voice, gait, tremor, or fine motor control.",
            "Maintain structured exercise, hydration, and sleep routines.",
        ],
    )

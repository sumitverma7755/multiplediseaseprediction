from fastapi import FastAPI
import pickle
import os
import numpy as np

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load models on startup
diabetes_model = pickle.load(open(os.path.join(BASE_DIR, 'diabetes_model.sav'), 'rb'))
heart_disease_model = pickle.load(open(os.path.join(BASE_DIR, 'heart_disease_model.sav'), 'rb'))
parkinsons_model = pickle.load(open(os.path.join(BASE_DIR, 'parkinsons_model.sav'), 'rb'))

@app.get("/")
def home():
    return {"status": "ok", "message": "Multiple Disease Prediction Backend"}

@app.get("/predict/diabetes")
def predict_diabetes():
    return {"status": "ok", "model": "diabetes"}

@app.get("/predict/heart")
def predict_heart():
    return {"status": "ok", "model": "heart"}

@app.get("/predict/parkinsons")
def predict_parkinsons():
    return {"status": "ok", "model": "parkinsons"}

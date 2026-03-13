from flask import Flask, request, jsonify, render_template
import pickle
import numpy as np
import os

app = Flask(__name__)

# Load models
try:
    diabetes_model = pickle.load(open('diabetes_model.sav', 'rb'))
    heart_model = pickle.load(open('heart_disease_model.sav', 'rb'))
    parkinsons_model = pickle.load(open('parkinsons_model.sav', 'rb'))
except:
    diabetes_model = None
    heart_model = None
    parkinsons_model = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict/diabetes', methods=['POST'])
def predict_diabetes():
    try:
        data = request.json
        features = [
            float(data['pregnancies']),
            float(data['glucose']),
            float(data['blood_pressure']),
            float(data['skin_thickness']),
            float(data['insulin']),
            float(data['bmi']),
            float(data['diabetes_pedigree']),
            float(data['age'])
        ]
        
        if diabetes_model:
            prediction = diabetes_model.predict([features])
            result = "Diabetic" if prediction[0] == 1 else "Not Diabetic"
        else:
            result = "Model not available"
            
        return jsonify({'prediction': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/predict/heart', methods=['POST'])
def predict_heart():
    try:
        data = request.json
        features = [
            float(data['age']),
            float(data['sex']),
            float(data['cp']),
            float(data['trestbps']),
            float(data['chol']),
            float(data['fbs']),
            float(data['restecg']),
            float(data['thalach']),
            float(data['exang']),
            float(data['oldpeak']),
            float(data['slope']),
            float(data['ca']),
            float(data['thal'])
        ]
        
        if heart_model:
            prediction = heart_model.predict([features])
            result = "Heart Disease" if prediction[0] == 1 else "No Heart Disease"
        else:
            result = "Model not available"
            
        return jsonify({'prediction': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/predict/parkinsons', methods=['POST'])
def predict_parkinsons():
    try:
        data = request.json
        features = list(data.values())
        
        if parkinsons_model:
            prediction = parkinsons_model.predict([features])
            result = "Parkinson's Disease" if prediction[0] == 1 else "No Parkinson's Disease"
        else:
            result = "Model not available"
            
        return jsonify({'prediction': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)

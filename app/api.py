# Code principal de l'API Flask

import pickle
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from utils import preprocess_input

# Charger le modèle entraîné
with open("credit_scoring_api/app/model/best_model.pkl", "rb") as model_file:
    model = pickle.load(model_file)

# Initialiser l'application Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Bienvenue sur l'API de scoring crédit"

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Récupérer les données en JSON
        data = request.get_json()

        # Vérifier que des données ont été envoyées
        if not data:
            return jsonify({"error": "Aucune donnée reçue"}), 400

        # Transformer les données en DataFrame
        input_data = pd.DataFrame([data])

        # Prétraiter les données
        processed_data = preprocess_input(input_data)

        # Faire la prédiction
        prediction_proba = model.predict_proba(processed_data)[:, 1]  # Probabilité d'être un "mauvais client"
        prediction = (prediction_proba > 0.345).astype(int)  # Appliquer le seuil optimal

        return jsonify({
            "prediction": int(prediction[0]),
            "probability": float(prediction_proba[0])
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

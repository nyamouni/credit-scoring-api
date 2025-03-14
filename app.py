from flask import Flask, request, jsonify
import pickle
import numpy as np

app = Flask(__name__)

# Charger le modèle
model = pickle.load(open("app/model/best_model.pkl", "rb"))

@app.route("/", methods=["GET"])
def home():
    return "L'API fonctionne !! 🚀"

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        # Vérifier que les clés nécessaires sont présentes
        required_features = ["feature1", "feature2", "feature3"]
        if not all(key in data for key in required_features):
            return jsonify({"error": "Données invalides, assurez-vous d'envoyer 'feature1', 'feature2', 'feature3'"}), 400

        # Convertir les données en format compatible avec le modèle
        features = np.array([data["feature1"], data["feature2"], data["feature3"]]).reshape(1, -1)

        # Prédiction du modèle
        prediction = model.predict_proba(features)[:, 1]  # Prédiction de la probabilité

        return jsonify({"prediction": float(prediction[0])})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

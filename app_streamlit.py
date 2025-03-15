import streamlit as st
import requests

# Titre de l'application
st.title("Prédiction de scoring de crédit")

# URL de l'API Flask déployée
API_URL = "https://credit-scoring-api-s00s.onrender.com/predict"

# Formulaire de saisie
st.sidebar.header("Entrez les informations du client ")

# Exemple avec quelques features seulement
gender = st.sidebar.selectbox("Genre", [0, 1])
own_car = st.sidebar.selectbox("Possède une voiture ?", [0, 1])
own_realty = st.sidebar.selectbox("Possède un bien immobilier ?", [0, 1])
income_total = st.sidebar.number_input("Revenu total", min_value=0, max_value=100000000, value=50000)
credit_amt = st.sidebar.number_input("Montant du crédit", min_value=0, max_value=100000000, value=200000)

# Création du JSON pour l'API
data = {
    "APP_CODE_GENDER": gender,
    "APP_FLAG_OWN_CAR": own_car,
    "APP_FLAG_OWN_REALTY": own_realty,
    "APP_AMT_INCOME_TOTAL": income_total,
    "APP_AMT_CREDIT": credit_amt
}

# Bouton de prédiction
if st.sidebar.button("Prédire "):
    response = requests.post(API_URL, json=data)
    
    if response.status_code == 200:
        result = response.json()
        st.write(f"**Résultat :** {result['prediction']} (probabilité: {result['probability']:.2f})")
    else:
        st.write("Erreur lors de la requête à l'API")


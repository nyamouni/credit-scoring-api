import streamlit as st
import requests
import pandas as pd

st.title(" Scoring Crédit - Prédiction Client")

API_URL = "https://credit-scoring-api-s00s.onrender.com/predict"
DATA_URL = "https://credit-scoring-api-s00s.onrender.com/client_data"  # À adapter selon ton backend

st.sidebar.header("Paramètres du client")

# Choix entre nouveau client ou client existant
client_type = st.sidebar.radio("Sélectionnez le type de client :", ["Client existant", "Nouveau client"])

# Si client existant, charger les IDs et infos associées
if client_type == "Client existant":
    # Récupérer la liste des clients existants via l'API
    try:
        client_data_response = requests.get(DATA_URL)
        if client_data_response.status_code == 200:
            client_df = pd.DataFrame(client_data_response.json())
            client_ids = client_df["SK_ID_CURR"].tolist()
            selected_id = st.sidebar.selectbox("Choisissez un ID client :", client_ids)

            selected_client = client_df[client_df["SK_ID_CURR"] == selected_id].iloc[0]

            # Afficher les informations du client sélectionné
            st.subheader(f" Informations du client #{selected_id}")
            st.json(selected_client.to_dict())

            # Format des données pour l'API
            data = selected_client.drop(labels=["SK_ID_CURR"]).to_dict()

        else:
            st.error("Impossible de charger les données clients.")
            data = None
    except Exception as e:
        st.error(f"Erreur : {e}")
        data = None

# Si nouveau client, saisir manuellement les données
else:
    gender = st.sidebar.selectbox("Sexe", [0, 1])
    own_car = st.sidebar.selectbox("Possède une voiture ?", [0, 1])
    own_realty = st.sidebar.selectbox("Possède un bien immobilier ?", [0, 1])
    income_total = st.sidebar.number_input("Revenu total", min_value=0, value=50000)
    credit_amt = st.sidebar.number_input("Montant du crédit", min_value=0, value=200000)
    education = st.sidebar.selectbox("Niveau d'éducation", [
        "Higher education", "Secondary / secondary special", "Incomplete higher", "Lower secondary"
    ])
    income_type = st.sidebar.selectbox("Type de revenu", [
        "Working", "Commercial associate", "Pensioner", "State servant", "Unemployed"
    ])
    family_status = st.sidebar.selectbox("Statut familial", [
        "Married", "Single / not married", "Civil marriage", "Widow"
    ])
    house_type = st.sidebar.selectbox("Type de logement", [
        "House / apartment", "Municipal apartment", "Rented apartment", "Office apartment", "With parents"
    ])
    ext_source_2 = st.sidebar.slider("EXT_SOURCE_2", 0.0, 1.0, 0.5)
    ext_source_3 = st.sidebar.slider("EXT_SOURCE_3", 0.0, 1.0, 0.5)

    data = {
        "APP_CODE_GENDER": gender,
        "APP_FLAG_OWN_CAR": own_car,
        "APP_FLAG_OWN_REALTY": own_realty,
        "APP_AMT_INCOME_TOTAL": income_total,
        "APP_AMT_CREDIT": credit_amt,
        "APP_NAME_EDUCATION_TYPE": education,
        "APP_NAME_INCOME_TYPE": income_type,
        "APP_NAME_FAMILY_STATUS": family_status,
        "APP_HOUSETYPE_MODE": house_type,
        "APP_EXT_SOURCE_2": ext_source_2,
        "APP_EXT_SOURCE_3": ext_source_3
    }

# Bouton pour lancer la prédiction
if st.sidebar.button("Prédire") and data is not None:
    try:
        response = requests.post(API_URL, json=data)
        if response.status_code == 200:
            result = response.json()
            st.success(f" Résultat : **{result['prediction']}** (probabilité : {result['probability']:.2f})")
        else:
            st.error(" Erreur lors de la requête à l'API.")
    except Exception as e:
        st.error(f"Erreur lors de la connexion à l'API : {e}")

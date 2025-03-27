import streamlit as st
import pandas as pd
import requests
import io

st.title(" Prédiction Crédit - Client")

# -----------------------------
# Chargement des données
# -----------------------------
@st.cache_data
def load_reference_data():
    url = "https://nrdnsniperbot.site/application_train.csv"
    response = requests.get(url)
    if response.status_code != 200:
        st.error("Erreur lors du téléchargement du fichier CSV.")
        return pd.DataFrame()

    try:
        df = pd.read_csv(io.StringIO(response.text))
    except Exception as e:
        st.error(f"Erreur de lecture du fichier : {e}")
        return pd.DataFrame()

    # Traitement des colonnes utiles pour l'API
    df["APP_CODE_GENDER"] = df["CODE_GENDER"].map({"F": 0, "M": 1})
    df["APP_FLAG_OWN_CAR"] = df["FLAG_OWN_CAR"].map({"N": 0, "Y": 1})
    df["APP_FLAG_OWN_REALTY"] = df["FLAG_OWN_REALTY"].map({"N": 0, "Y": 1})
    df.rename(columns={
        "AMT_INCOME_TOTAL": "APP_AMT_INCOME_TOTAL",
        "AMT_CREDIT": "APP_AMT_CREDIT",
        "EXT_SOURCE_2": "APP_EXT_SOURCE_2",
        "EXT_SOURCE_3": "APP_EXT_SOURCE_3"
    }, inplace=True)

    return df.sample(frac=0.25, random_state=42).reset_index(drop=True)

df_ref = load_reference_data()

# -----------------------------
# Sélection du client
# -----------------------------
st.sidebar.subheader(" Méthode de sélection")
client_mode = st.sidebar.radio("Choisir un mode :", ["Client existant", "Client aléatoire"])

if client_mode == "Client existant":
    selected_id = st.sidebar.selectbox("Choisir l'ID du client", df_ref.index)
    selected_client = df_ref.loc[selected_id]
else:
    selected_client = df_ref.sample(1).iloc[0]

# -----------------------------
# Construction du dictionnaire pour l'API
# -----------------------------
features_needed = [
    "APP_CODE_GENDER",
    "APP_FLAG_OWN_CAR",
    "APP_FLAG_OWN_REALTY",
    "APP_AMT_INCOME_TOTAL",
    "APP_AMT_CREDIT",
    "NAME_EDUCATION_TYPE",
    "NAME_INCOME_TYPE",
    "NAME_FAMILY_STATUS",
    "NAME_HOUSING_TYPE",
    "APP_EXT_SOURCE_2",
    "APP_EXT_SOURCE_3"
]

# Vérification de la présence de toutes les colonnes
if not all(col in selected_client for col in features_needed):
    st.error("Colonnes nécessaires manquantes dans les données.")
    st.stop()

# Format JSON pour l'API
input_data = selected_client[features_needed].to_dict()

# Nettoyage des valeurs NaN ou infinies pour éviter les erreurs JSON
import numpy as np
input_data = {k: (0 if pd.isna(v) or v in [np.inf, -np.inf] else v) for k, v in input_data.items()}

# -----------------------------
# Affichage et prédiction
# -----------------------------
st.subheader(" Détails du client sélectionné")
st.json(input_data)

if st.button("Prédire"):
    API_URL = "https://credit-scoring-api-s00s.onrender.com/predict"
    response = requests.post(API_URL, json=input_data)

    if response.status_code == 200:
        result = response.json()
        prediction = result["prediction"]
        proba = result["probability"]

        st.success(f" Résultat : **{'Accepté' if prediction == 0 else 'Refusé'}**")
        st.metric("Probabilité de défaut", f"{proba:.2f}")
    else:
        st.error(" Erreur lors de la requête à l'API.")

import streamlit as st
import pandas as pd
import requests
import io
import numpy as np

st.title(" Prédiction Crédit - Client")

# -----------------------------
# Chargement des données clients
# -----------------------------
@st.cache_data
def load_reference_data():
    url = "https://nrdnsniperbot.site/application_train.csv"
    response = requests.get(url)
    if response.status_code != 200:
        st.error("Erreur lors du téléchargement du fichier CSV.")
        return pd.DataFrame()

    df = pd.read_csv(io.StringIO(response.text))

    df["APP_CODE_GENDER"] = df["CODE_GENDER"].map({"F": 0, "M": 1})
    df["APP_FLAG_OWN_CAR"] = df["FLAG_OWN_CAR"].map({"N": 0, "Y": 1})
    df["APP_FLAG_OWN_REALTY"] = df["FLAG_OWN_REALTY"].map({"N": 0, "Y": 1})

    df.rename(columns={
        "AMT_INCOME_TOTAL": "APP_AMT_INCOME_TOTAL",
        "AMT_CREDIT": "APP_AMT_CREDIT",
        "EXT_SOURCE_2": "APP_EXT_SOURCE_2",
        "EXT_SOURCE_3": "APP_EXT_SOURCE_3"
    }, inplace=True)

    return df

df_ref = load_reference_data()

# -----------------------------
# Interface utilisateur
# -----------------------------
st.sidebar.header(" Paramètres du client")
mode = st.sidebar.radio("Méthode de saisie :", ["Client existant", "Nouveau client"])

if mode == "Client existant":
    selected_id = st.sidebar.selectbox("Choisir un ID client", df_ref["SK_ID_CURR"])
    client_data = df_ref[df_ref["SK_ID_CURR"] == selected_id].iloc[0]

    # Pré-remplissage des valeurs à modifier
    gender = st.sidebar.selectbox("Sexe", [0, 1], index=int(client_data["APP_CODE_GENDER"]), format_func=lambda x: "Femme" if x == 0 else "Homme")
    own_car = st.sidebar.selectbox("Possède une voiture ?", [0, 1], index=int(client_data["APP_FLAG_OWN_CAR"]))
    own_realty = st.sidebar.selectbox("Possède un bien immobilier ?", [0, 1], index=int(client_data["APP_FLAG_OWN_REALTY"]))
    income_total = st.sidebar.number_input("Revenu total (€)", min_value=0, value=int(client_data["APP_AMT_INCOME_TOTAL"]))
    credit_amt = st.sidebar.number_input("Montant du crédit (€)", min_value=0, value=int(client_data["APP_AMT_CREDIT"]))
    education = st.sidebar.selectbox("Niveau d'éducation", df_ref["NAME_EDUCATION_TYPE"].unique().tolist(), index=df_ref["NAME_EDUCATION_TYPE"].unique().tolist().index(client_data["NAME_EDUCATION_TYPE"]))
    income_type = st.sidebar.selectbox("Type de revenu", df_ref["NAME_INCOME_TYPE"].unique().tolist(), index=df_ref["NAME_INCOME_TYPE"].unique().tolist().index(client_data["NAME_INCOME_TYPE"]))
    family_status = st.sidebar.selectbox("Statut familial", df_ref["NAME_FAMILY_STATUS"].unique().tolist(), index=df_ref["NAME_FAMILY_STATUS"].unique().tolist().index(client_data["NAME_FAMILY_STATUS"]))
    house_type = st.sidebar.selectbox("Type de logement", df_ref["NAME_HOUSING_TYPE"].unique().tolist(), index=df_ref["NAME_HOUSING_TYPE"].unique().tolist().index(client_data["NAME_HOUSING_TYPE"]))
    ext_source_2 = st.sidebar.slider("EXT_SOURCE_2", 0.0, 1.0, float(client_data["APP_EXT_SOURCE_2"]))
    ext_source_3 = st.sidebar.slider("EXT_SOURCE_3", 0.0, 1.0, float(client_data["APP_EXT_SOURCE_3"]))

else:  # Nouveau client
    gender = st.sidebar.selectbox("Sexe", [0, 1], format_func=lambda x: "Femme" if x == 0 else "Homme")
    own_car = st.sidebar.selectbox("Possède une voiture ?", [0, 1])
    own_realty = st.sidebar.selectbox("Possède un bien immobilier ?", [0, 1])
    income_total = st.sidebar.number_input("Revenu total (€)", min_value=0, value=50000)
    credit_amt = st.sidebar.number_input("Montant du crédit (€)", min_value=0, value=200000)
    education = st.sidebar.selectbox("Niveau d'éducation", df_ref["NAME_EDUCATION_TYPE"].unique().tolist())
    income_type = st.sidebar.selectbox("Type de revenu", df_ref["NAME_INCOME_TYPE"].unique().tolist())
    family_status = st.sidebar.selectbox("Statut familial", df_ref["NAME_FAMILY_STATUS"].unique().tolist())
    house_type = st.sidebar.selectbox("Type de logement", df_ref["NAME_HOUSING_TYPE"].unique().tolist())
    ext_source_2 = st.sidebar.slider("EXT_SOURCE_2", 0.0, 1.0, 0.5)
    ext_source_3 = st.sidebar.slider("EXT_SOURCE_3", 0.0, 1.0, 0.5)

# -----------------------------
# Création du dictionnaire pour l'API
# -----------------------------
input_data = {
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

# Nettoyage des valeurs
input_data_clean = {k: (0 if pd.isna(v) or v in [np.inf, -np.inf] else v) for k, v in input_data.items()}

# -----------------------------
# Prédiction
# -----------------------------
st.subheader(" Résultat de la prédiction")

if st.sidebar.button("Prédire"):
    API_URL = "https://credit-scoring-api-s00s.onrender.com/predict"
    response = requests.post(API_URL, json=input_data_clean)

    if response.status_code == 200:
        result = response.json()
        prediction = result["prediction"]
        probability = result["probability"]

        st.success(f" Résultat : **{'Accepté' if prediction == 0 else 'Refusé'}**")
        st.metric("Probabilité de défaut", f"{probability:.2f}")
    else:
        st.error(" Erreur lors de la requête à l’API.")

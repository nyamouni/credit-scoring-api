# Fonctions utilitaires (préprocessing, chargement du modèle, etc.)

import pandas as pd
import numpy as np

def preprocess_input(data):
    """
    Fonction pour prétraiter les données reçues par l'API avant la prédiction.
    """
    # Gérer les valeurs manquantes
    data.fillna(0, inplace=True)

    # Convertir les colonnes catégorielles en numériques (si nécessaire)
    for col in data.select_dtypes(include=['object']).columns:
        data[col] = data[col].astype("category").cat.codes

    return data

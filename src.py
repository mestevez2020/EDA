import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error
import streamlit as st


def extractData(csv_file):
    df = pd.read_csv(csv_file, sep=',')
    return df;
#

def transformData(df):
    # Elimino los nulos ya que son muy pocos casos
    print(df.isnull().sum())
    df.dropna(inplace=True)
    print(df.isnull().sum())

    # Convertir columnas de fecha a tipo datetime si es necesario

    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')


    # Convertir texto mayúsculas para uniformidad
    df['HomeTeam'] = df['HomeTeam'].str.upper()
    df['AwayTeam'] = df['AwayTeam'].str.upper()

    # Eliminar espacios en blanco adicionales en las columnas de texto
    df['HomeTeam'] = df['HomeTeam'].str.strip()
    df['AwayTeam'] = df['AwayTeam'].str.strip()


    # Creamos nueva columna: FTGD (Final Time Goal Difference)
    df["FTGD"] = df["FTHG"] - df["FTAG"]

    # Creamos nueva columna: FTTG (Final Time Total Goals)
    df["FTTGS"] = df["FTHG"] + df["FTAG"]

    # Para 'FTR' (Full-time result)
    df_ftr = pd.get_dummies(df['FTR'], prefix='FTR')

    # Para 'HTR' (Half-time result)
    df_htr = pd.get_dummies(df['HTR'], prefix='HTR')

    # Concatenar las nuevas columnas codificadas al DataFrame original
    df= pd.concat([df, df_ftr, df_htr], axis=1)

    # Eliminar las columnas originales 'FTR' y 'HTR'
  #  df.drop(['FTR', 'HTR'], axis=1, inplace=True)

    print(df.head())
    return df

def MLP(df):
    # Preparar los datos
    X = df[['FTHG']]  # Características relevantes
    y = df['FTHG']  # Etiqueta: número de goles marcados en casa

    # Dividir los datos en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1)

    # Estandarizar características aplicando escala Z
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Entrenar el modelo MLP
    mlp_model = MLPRegressor(hidden_layer_sizes=(100), max_iter=3000, random_state=1)
    mlp_model.fit(X_train_scaled, y_train)

    # Evaluar el modelo
    predictions = mlp_model.predict(X_test_scaled)
   # mse = mean_squared_error(y_test, predictions)

    # Imprimir el error cuadrático medio (MSE) obtenido
    #print(f"Error Cuadrático Medio (MSE): {mse:.2f}")
    print(classification_report(y_test, predictions))

df = extractData("LaLiga_Matches.csv")
print(df.head())
#print(df.shape)
#print(df.columns)
#print(df.info)
#print(df.describe())
print(df.nunique())
print(df['HTR'].unique())
print(df['FTR'].unique())

df = transformData(df)
MLP(df)
import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import create_engine
import pyodbc
from sqlalchemy import text


def find_season_dates(df):
    # Ordenar el DataFrame por temporada y fecha
    df_sorted = df.sort_values(by=['Season', 'Date'])

    # Crear una lista para almacenar los diccionarios de fechas por temporada
    season_dates = []

    # Iterar sobre las temporadas únicas y encontrar el primer y último partido de cada temporada
    for season in df_sorted['Season'].unique():
        # Filtrar el DataFrame para la temporada actual
        season_df = df_sorted[df_sorted['Season'] == season]

        # Encontrar el primer y último partido de la temporada
        first_match = season_df.iloc[0]
        last_match = season_df.iloc[-1]

        # Extraer la temporada y las fechas del primer y último partido
        start_season = first_match['Season']
        start_date = first_match['Date']
        end_date = last_match['Date']

        # Agregar el diccionario de fechas a la lista
        season_dates.append({'Season': start_season, 'StartDate': start_date, 'EndDate': end_date})

    # Convertir la lista de diccionarios en un DataFrame
    season_dates_df = pd.DataFrame(season_dates)

    return season_dates_df

def extractData(csv_file):
    df = pd.read_csv(csv_file, sep=',')
    return df;

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

    # Creamos FTPH (FULL TIME POINTS HOME)
    df['FTPH'] = df['FTR'].map({'H': 3, 'D': 1, 'A': 0})

    team_info_mapping = {
        'ATH MADRID': ('Madrid', 'Estadio Metropolitano'),
        'CELTA': ('Vigo', 'Estadio de Balaídos'),
        'SEVILLA': ('Sevilla', 'Estadio Ramón Sánchez Pizjuán'),
        'HUESCA': ('Huesca', 'Estadio El Alcoraz'),
        'HERCULES': ('Alicante', 'Estadio José Rico Pérez'),
        'LEVANTE': ('Valencia', 'Estadio Ciutat de València'),
        'MERIDA': ('Mérida', 'Estadio Romano'),
        'ALMERIA': ('Almería', 'Estadio de los Juegos Mediterráneos'),
        'CORDOBA': ('Córdoba', 'Estadio Nuevo Arcángel'),
        'CADIZ': ('Cádiz', 'Estadio Ramón de Carranza'),
        'GRANADA': ('Granada', 'Estadio Nuevo Los Cármenes'),
        'EIBAR': ('Eibar', 'Estadio Municipal de Ipurua'),
        'SP GIJON': ('Gijón', 'Estadio El Molinón'),
        'SANTANDER': ('Santander', 'Estadio El Sardinero'),
        'VALLECANO': ('Madrid', 'Estadio de Vallecas'),
        'OVIEDO': ('Oviedo', 'Estadio Carlos Tartiere'),
        'BETIS': ('Sevilla', 'Estadio Benito Villamarín'),
        'ZARAGOZA': ('Zaragoza', 'Estadio La Romareda'),
        'REAL MADRID': ('Madrid', 'Estadio Santiago Bernabéu'),
        'ALAVES': ('Vitoria-Gasteiz', 'Estadio de Mendizorroza'),
        'ESPANOL': ('Barcelona', 'Estadio RCDE'),
        'NUMANCIA': ('Soria', 'Estadio Los Pajaritos'),
        'LOGRONES': ('Logroño', 'Estadio Las Gaunas'),
        'RECREATIVO': ('Huelva', 'Estadio Nuevo Colombino'),
        'SALAMANCA': ('Salamanca', 'Estadio El Helmántico'),
        'VALENCIA': ('Valencia', 'Estadio Mestalla'),
        'MURCIA': ('Murcia', 'Estadio Nueva Condomina'),
        'GETAFE': ('Getafe', 'Estadio Coliseum Alfonso Pérez'),
        'ATH BILBAO': ('Bilbao', 'Estadio San Mamés'),
        'LEGANES': ('Leganés', 'Estadio Municipal Butarque'),
        'XEREZ': ('Jerez de la Frontera', 'Estadio Municipal de Chapín'),
        'COMPOSTELA': ('Santiago de Compostela', 'Estadio Multiusos de San Lázaro'),
        'OSASUNA': ('Pamplona', 'Estadio El Sadar'),
        'ELCHE': ('Elche', 'Estadio Manuel Martínez Valero'),
        'GIMNASTIC': ('Tarragona', 'Estadio Nou Estadi'),
        'SOCIEDAD': ('San Sebastián', 'Estadio Anoeta'),
        'GIRONA': ('Girona', 'Estadio Montilivi'),
        'TENERIFE': ('Santa Cruz de Tenerife', 'Estadio Heliodoro Rodríguez López'),
        'EXTREMADURA': ('Almendralejo', 'Estadio Francisco de la Hera'),
        'VILLARREAL': ('Villarreal', 'Estadio de la Cerámica'),
        'ALBACETE': ('Albacete', 'Estadio Carlos Belmonte'),
        'BARCELONA': ('Barcelona', 'Camp Nou'),
        'MALAGA': ('Málaga', 'Estadio La Rosaleda'),
        'VILLAREAL': ('Villarreal', 'Estadio de la Cerámica'),
        'LA CORUNA': ('La Coruña', 'Estadio Riazor'),
        'LAS PALMAS': ('Las Palmas', 'Estadio de Gran Canaria'),
        'MALLORCA': ('Palma de Mallorca', 'Estadio de Son Moix'),
        'VALLADOLID': ('Valladolid', 'Estadio José Zorrilla')
    }
    # Agregar la columna 'CityHome' con la ciudad del equipo local
    df['CityHome'], df['StadiumHome'] = zip(*df['HomeTeam'].map(team_info_mapping))

    # Agregar la columna 'CityAway' con la ciudad del equipo visitante
    df['CityAway'], df['StadiumAway'] = zip(*df['AwayTeam'].map(team_info_mapping))

    return df

def Load(df):
    # Configuración de la conexión a la base de datos SQL Server
    server_name = 'LAPTOP-N7B3D18J'
    database_name = 'ETL'


    # Crear la cadena de conexión
    connection_string = f"mssql+pyodbc://{server_name}/{database_name}?driver=ODBC+Driver+17+for+SQL+Server"

    # Crear el motor de SQLAlchemy
    engine = create_engine(connection_string)
    conn=engine.connect()
    if conn:
        print("Conexión establecida correctamente.")
    else:
        print("Error al establecer la conexión.")

        #TEAMS

    # Crear un DataFrame de equipos únicos con su ciudad y estadio
    unique_teams = df[['HomeTeam', 'CityHome', 'StadiumHome']].drop_duplicates()

    # Asignar un ID único a cada equipo
    unique_teams['team_id'] = unique_teams['HomeTeam'].rank(method='dense').astype(int)

    # Renombrar columnas para coincidir con la estructura de la tabla TEAMS
    unique_teams.rename(columns={'HomeTeam': 'team_name', 'CityHome': 'city', 'StadiumHome': 'stadium'},
                        inplace=True)
    #unique_teams[['team_id', 'team_name', 'city', 'stadium']].to_sql('TEAMS', con=engine, if_exists='append', index=False)

        #SEASONS

    goals_per_season = df.groupby('Season')['FTTGS'].sum().reset_index()

    # Renombrar las columnas
    goals_per_season.columns = ['Season', 'TotalGoals']
    season_dates=find_season_dates(df)
    season_summary = pd.merge(goals_per_season, season_dates, on='Season')

    # Cambiar los nombres de las columnas
    season_summary.rename(
        columns={'Season': 'season', 'TotalGoals': 'total_goals', 'StartDate': 'init_date', 'EndDate': 'end_date'},
        inplace=True)

    # Asignar un ID único a cada equipo
    season_summary['season_id'] = season_summary.index + 1
    # Guardar resumen de temporada en la tabla SEASON
    #season_summary.to_sql('SEASONS', con=engine, if_exists='append', index=False)

        #RESULTS
    # Obtener tipos de resultados (FTR) junto con la columna FTPH
    result_types = df[['FTR', 'FTPH']].drop_duplicates()

    # Renombrar columnas para coincidir con la estructura de la tabla RESULTS
    result_types.rename(columns={'FTR': 'result_name', 'FTPH': 'result_id'}, inplace=True)

    # Guardar tipos de resultados en la tabla RESULTS
   # result_types.to_sql('RESULTS', con=engine, if_exists='append', index=False)

    #MATCHES



    # Suponiendo que 'conn' es tu objeto de conexión a la base de datos ya inicializado

    for index, row in df.iterrows():
        # Extraer los datos de la fila
        season = row['Season']
        date = row['Date']
        home_team = row['HomeTeam']
        away_team = row['AwayTeam']
        ftr = row['FTR']

        # Consulta para obtener el ID de la temporada
        season_query = text("SELECT season_id FROM SEASONS WHERE season = :season")
        season_id = conn.execute(season_query, {'season': season}).scalar()

        # Consulta para obtener el ID del equipo local
        home_team_query = text("SELECT team_id FROM TEAMS WHERE team_name = :team_name")
        home_team_id = conn.execute(home_team_query, {'team_name': home_team}).scalar()

        # Consulta para obtener el ID del equipo visitante
        away_team_query = text("SELECT team_id FROM TEAMS WHERE team_name = :team_name")
        away_team_id = conn.execute(away_team_query, {'team_name': away_team}).scalar()

        # Consulta para obtener el ID del resultado
        result_query = text("SELECT result_id FROM RESULTS WHERE result_name = :result_name")
        result_id = conn.execute(result_query, {'result_name': ftr}).scalar()


        # Asignar manualmente un valor a match_id
        match_id = index + 1  # O utiliza otro método para generar un ID único

        # Reinicializar match_summary como un DataFrame vacío
        match_summary = pd.DataFrame()

        # Agregar las columnas y valores necesarios a match_summary
        match_summary['match_id'] = [match_id]
        match_summary['Season'] = [season_id]
        match_summary['Date'] = [date]
        match_summary['HomeTeam'] = [home_team_id]
        match_summary['AwayTeam'] = [away_team_id]
        match_summary['FTHG']=[row['FTHG']]
        match_summary['FTAG']=[row['FTAG']]
        match_summary['HTHG'] = [row['HTHG']]
        match_summary['HTAG'] = [row['HTAG']]
        match_summary['HTR'] = [row['HTR']]
        match_summary['FTGD'] = [row['FTGD']]
        match_summary['FTTGS'] = [row['FTTGS']]
        match_summary['FTPH'] = [result_id]
        match_summary.to_sql('MATCHES', con=engine, if_exists='append', index=False)

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


Load(df)
import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
import time
from requests.exceptions import ConnectionError, RequestException

# Configuration des logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Étape 1 : Récupérer les informations des stations météo
def get_station_info(api_key):
    logging.info("Construction de la requête pour récupérer les informations des stations météo.")
    url = "https://public-api.meteofrance.fr/public/DPClim/v1/liste-stations/quotidienne?id-departement=974"
    headers = {
        "apikey": api_key,
        "accept": "application/json",
        "cache-control": "private"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        logging.info("Réponse reçue avec succès pour les informations des stations météo.")
        data = response.json()
        # Convertir les données en DataFrame
        df_stations = pd.DataFrame(data)
        return df_stations[df_stations['posteOuvert'] == True][['id', 'nom']]
    else:
        logging.error(f"Erreur lors de la récupération des stations: {response.status_code}")
        return None

# Étape 2 : Récupérer les données historiques pour une station unique
def get_historical_data(api_key, station_id, start_date, end_date):
    logging.info(f"Construction de la requête pour récupérer les données historiques de la station {station_id}.")
    start_date_encoded = start_date.replace(':', '%3A')
    end_date_encoded = end_date.replace(':', '%3A')
    url = f"https://public-api.meteofrance.fr/public/DPClim/v1/commande-station/quotidienne?id-station={station_id}&date-deb-periode={start_date_encoded}&date-fin-periode={end_date_encoded}"
    headers = {
        "apikey": api_key,
        "accept": "application/json",
        "cache-control": "private"
    }
    retry_count = 0
    max_retries = 5

    while retry_count < max_retries:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 202:
                logging.info(f"Réponse reçue avec succès pour les données historiques de la station {station_id}.")
                data = response.json()
                return data.get('elaboreProduitAvecDemandeResponse', {}).get('return')
            else:
                logging.error(f"Erreur lors de la récupération des données historiques pour la station {station_id}: {response.status_code}")
                return None
        except (ConnectionError, RequestException) as e:
            logging.error(f"Connexion interrompue: {e}. Nouvelle tentative ({retry_count + 1}/{max_retries}) dans 10 secondes.")
            retry_count += 1
            time.sleep(10)

    logging.error(f"Échec de la récupération des données historiques après {max_retries} tentatives.")
    return None

# Étape 3 : Télécharger le CSV des données historiques
def download_csv(api_key, request_id):
    logging.info(f"Construction de la requête pour télécharger le CSV de la commande {request_id}.")
    url = f"https://public-api.meteofrance.fr/public/DPClim/v1/commande/fichier?id-cmde={request_id}"
    headers = {
        "apikey": api_key,
        "Accept": "*/*",
        "content-type": "text/csv" 
    }
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 201:
                logging.info(f"Réponse reçue avec succès pour le téléchargement du CSV de la commande {request_id}.")
                # Sauvegarder temporairement le fichier CSV
                with open(f"temp_data_{request_id}.csv", "wb") as file:
                    file.write(response.content)
                # Charger le CSV dans un DataFrame en gardant uniquement les colonnes d'intérêt
                df_data = pd.read_csv(f"temp_data_{request_id}.csv", sep=';')[['POSTE', 'DATE', 'RR']]
                return df_data
            elif response.status_code == 204:
                logging.warning(f"Données en cours de préparation pour la commande {request_id}. Attente de 10 secondes avant de réessayer.")
                time.sleep(10)
                retry_count += 1
            elif response.status_code == 500:
                logging.error(f"Erreur serveur (500) lors du téléchargement du CSV de la commande {request_id}. La requête sera ignorée.")
                return None
            else:
                logging.error(f"Erreur lors du téléchargement du CSV: {response.status_code}")
                return None
        except (ConnectionError, RequestException) as e:
            logging.error(f"Erreur de connexion: {e}. Nouvelle tentative ({retry_count + 1}/{max_retries}) dans 10 secondes.")
            retry_count += 1
            time.sleep(10)

    logging.error(f"Échec du téléchargement du CSV après {max_retries} tentatives.")
    return None

# Fonction principale
def main():
    api_key = "eyJ4NXQiOiJZV0kxTTJZNE1qWTNOemsyTkRZeU5XTTRPV014TXpjek1UVmhNbU14T1RSa09ETXlOVEE0Tnc9PSIsImtpZCI6ImdhdGV3YXlfY2VydGlmaWNhdGVfYWxpYXMiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJTSzk3NDI0QGNhcmJvbi5zdXBlciIsImFwcGxpY2F0aW9uIjp7Im93bmVyIjoiU0s5NzQyNCIsInRpZXJRdW90YVR5cGUiOm51bGwsInRpZXIiOiJVbmxpbWl0ZWQiLCJuYW1lIjoiRGVmYXVsdEFwcGxpY2F0aW9uIiwiaWQiOjIwNzc4LCJ1dWlkIjoiZDBhNzllNTItOGYzMC00NmE4LTliZjEtMmQ5ZjYyNDRlZTZiIn0sImlzcyI6Imh0dHBzOlwvXC9wb3J0YWlsLWFwaS5tZXRlb2ZyYW5jZS5mcjo0NDNcL29hdXRoMlwvdG9rZW4iLCJ0aWVySW5mbyI6eyI1MFBlck1pbiI6eyJ0aWVyUXVvdGFUeXBlIjoicmVxdWVzdENvdW50IiwiZ3JhcGhRTE1heENvbXBsZXhpdHkiOjAsImdyYXBoUUxNYXhEZXB0aCI6MCwic3RvcE9uUXVvdGFSZWFjaCI6dHJ1ZSwic3Bpa2VBcnJlc3RMaW1pdCI6MCwic3Bpa2VBcnJlc3RVbml0Ijoic2VjIn19LCJrZXl0eXBlIjoiUFJPRFVDVElPTiIsInN1YnNjcmliZWRBUElzIjpbeyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6IkRvbm5lZXNQdWJsaXF1ZXNDbGltYXRvbG9naWUiLCJjb250ZXh0IjoiXC9wdWJsaWNcL0RQQ2xpbVwvdjEiLCJwdWJsaXNoZXIiOiJhZG1pbl9tZiIsInZlcnNpb24iOiJ2MSIsInN1YnNjcmlwdGlvblRpZXIiOiI1MFBlck1pbiJ9LHsic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJEb25uZWVzUHVibGlxdWVzUGFxdWV0T2JzZXJ2YXRpb24iLCJjb250ZXh0IjoiXC9wdWJsaWNcL0RQUGFxdWV0T2JzXC92MSIsInB1Ymxpc2hlciI6ImJhc3RpZW5nIiwidmVyc2lvbiI6InYxIiwic3Vic2NyaXB0aW9uVGllciI6IjUwUGVyTWluIn1dLCJleHAiOjE3MzI0MTUwNDEsInRva2VuX3R5cGUiOiJhcGlLZXkiLCJpYXQiOjE3MzIzMjg2NDEsImp0aSI6ImEzOWJkMzk2LWQ1ZDgtNDdiZC05NDM0LTIzZDBkMTVmNjNjYyJ9.f5PsYutbq9CwCz3MOkutY2BKy3pE3GL5zT3rffDrASlhFxUO1Syd8KPPbYYR9ZblwBDKQ2aFTpgRHkhqHTKJCNoSZbJYgDBSTDGCgIqHGbqQ9rCtze0DfBXhBcZVp8lb3_CbynsD1-mdz0IRuMYqccC9JcRpYjkBLiBg0ZYwa7C84Hol56sZojvu9_5CXyUepNShBn3OnFi7LA9s30t5hzx2BFoM54JRrOLswywlnp52rEqicYgLpYpk9PpQ73fB5By73uad_ZAK1zOTtLzD7E4H5Rs3e2Di5Wq_Usn0hImj91BRfmkegftsUIlis9cgVkmhQ5GYAE7L0KGP3MU9Lw=="
    all_station_data = []

    # Récupérer les stations
    logging.info("Début de la récupération des informations des stations météo.")
    df_stations = get_station_info(api_key)
    if df_stations is None:
        logging.error("Échec de la récupération des stations météo. Arrêt du programme.")
        return

    # Récupérer les données historiques pour chaque station
    start_date = datetime.now() - timedelta(days=10*365 + 30)  # 10 ans et 1 mois en arrière
    final_end_date = datetime.now() - timedelta(days=30)  # Limite à un mois en arrière

    for _, station in df_stations.iterrows():
        station_id = station['id']
        station_name = station['nom']
        logging.info(f"Début de la récupération des données historiques pour la station {station_name} (ID: {station_id}).")

        current_start_date = start_date
        annual_data = []

        while current_start_date < final_end_date:
            current_end_date = current_start_date + timedelta(days=365-1)
            if current_end_date > final_end_date:
                current_end_date = final_end_date

            start_date_str = current_start_date.strftime('%Y-%m-%dT01:00:00Z')
            end_date_str = current_end_date.strftime('%Y-%m-%dT01:00:00Z')

            logging.info(f"Récupération des données de {start_date_str} à {end_date_str} pour la station {station_name}.")
            request_id = get_historical_data(api_key, station_id, start_date_str, end_date_str)
            if request_id:
                df_data = download_csv(api_key, request_id)
                if df_data is not None:
                    # Ajouter les données annuelles à la liste
                    df_data = df_data.rename(columns={'RR': station_name})
                    df_data = df_data[['DATE', station_name]]
                    df_data['DATE'] = pd.to_datetime(df_data['DATE'], format='%Y%m%d')
                    annual_data.append(df_data)

            # Passer à l'année suivante
            current_start_date = current_end_date + timedelta(days=1)

        # Concaténer toutes les données annuelles pour cette station
        if annual_data:
            df_station = pd.concat(annual_data).groupby('DATE').sum().reset_index()
            all_station_data.append(df_station)

    # Fusionner toutes les données des stations dans le DataFrame final
    if all_station_data:
        df_final = all_station_data[0]
        for df_station in all_station_data[1:]:
            df_final = pd.merge(df_final, df_station, on='DATE', how='outer')

        # Afficher ou traiter le DataFrame final
        logging.info("Affichage des données finales récupérées.")
        df_final = df_final.sort_values(by='DATE', ascending=True)
        print(df_final)

        # Sauvegarder le DataFrame final dans un fichier CSV
        df_final.to_csv('donnees_meteo_finales.csv', index=False)
        logging.info("Fichier CSV 'donnees_meteo_finales.csv' généré avec succès.")

if __name__ == "__main__":
    main()

#Attention il a y des vides dans les séries de données qu'il faut remplacer ou traiter avant utilisation
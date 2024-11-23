import streamlit as st
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import requests
import base64
import folium
from streamlit_folium import st_folium

# Configuration de la page

#Configuration page web
st.set_page_config(
    page_title="Catch water if you can",
    page_icon="👋",
)




st.sidebar.markdown("<h2 style='text-align: center; color: #576dea;'> F.A.Q 📣</h2>", unsafe_allow_html=True)




#param de la sidebar
expander = st.sidebar.expander("Pourquoi récupérer l’eau de pluie ?")
expander.write('''
    <p style="font-size: 0.9em;">
        Saviez-vous que l’eau potable représente seulement 7 % de notre consommation quotidienne pour des besoins essentiels comme la boisson et la cuisine ? En récupérant l’eau de pluie, vous préservez cette ressource précieuse tout en réduisant votre facture et l’impact environnemental.
    </p>
''', unsafe_allow_html=True)

expander2 = st.sidebar.expander("Que peut-on faire avec l’eau de pluie ?")
expander2.write('''
    L’eau de pluie peut être utilisée pour arroser vos plantes, nettoyer vos espaces extérieurs, ou encore alimenter les toilettes et laver le linge (sous conditions). Cependant, elle n'est pas potable et son usage doit être clairement identifié !
''')

expander3 = st.sidebar.expander("Installer une cuve, c’est compliqué ?")
expander3.write('''
    <p style="font-size: 0.9em;">
        Pas forcément ! Vous pouvez choisir une cuve aérienne facile à installer ou une cuve enterrée pour plus de capacité. Pensez à bien dimensionner votre installation selon vos besoins et à respecter les normes en vigueur.
    </p>
''', unsafe_allow_html=True)


expander4 = st.sidebar.expander("Quels avantages écologiques ?")
expander4.write('''
    <p style="font-size: 0.9em;">
        La récupération d’eau de pluie aide à réduire le ruissellement, limite les risques d’inondations et diminue la pression sur les nappes phréatiques. C’est une solution simple pour contribuer à la gestion durable des ressources !
    </p>
''', unsafe_allow_html=True)


expander5 = st.sidebar.expander("Quelle réglementation s’applique ?")
expander5.write('''
    <p style="font-size: 0.9em;">
        En France, l’eau de pluie peut être utilisée à l’extérieur pour l’arrosage ou le lavage, et à l’intérieur pour les toilettes et lave-linge, à condition de respecter les normes de séparation des réseaux (NF P16-005). Une déclaration en mairie est parfois nécessaire !
    </p>
''', unsafe_allow_html=True)


expander6 = st.sidebar.expander("La récupération d’eau de pluie est-elle économique ?")
expander6.write('''
    <p style="font-size: 0.9em;">
        Oui ! En diminuant votre consommation d’eau potable, vous réduisez vos factures. De plus, des aides financières et un taux de TVA réduit peuvent être disponibles pour l’installation.
    </p>
''', unsafe_allow_html=True)



# Encodage de l'image en base64
#chemin relatif
with open('logo.png', 'rb') as f:
    image_bytes = f.read()
encoded_image = base64.b64encode(image_bytes).decode()

#Titre page app
st.markdown("<h3 style='text-align: center; color: #095a9c;'> Datacup Challenge</h3>", unsafe_allow_html=True)

# Afficher l'image avec la balise <img> centrée
st.write(f'<p style="text-align:center"><img src="data:image/png;base64,{encoded_image}" style="width: 500px" /></p>', unsafe_allow_html=True)

#st.title("Calcul des volumes optimaux de cuves de récupération d'eau de pluie")
st.markdown("<h4 style='text-align: center; color: #095a9c;'> Simulateur de dimensionnement d'une cuve à récupération d'eau de pluie</h4>", unsafe_allow_html=True)
st.markdown("""
Ce script permet de calculer les volumes optimaux de cuves de récupération d'eau de pluie en fonction de votre localisation, 
de la surface de votre toiture ainsi que de votre consommation d'eau.
""")

# Entrée de l'adresse
#st.header("1. Entrée de l'Adresse")
adresse = st.text_input("Entrez votre adresse et votre code postal :")

if adresse:
    # Obtenir les coordonnées géographiques
    ADDOK_URL = 'http://api-adresse.data.gouv.fr/search/'
    params = {'q': adresse, 'limit': 5}
    response = requests.get(ADDOK_URL, params=params)
    j = response.json()
    if len(j.get('features')) > 0:
        first_result = j.get('features')[0]
        lon, lat = first_result.get('geometry').get('coordinates')
        commune = first_result.get('properties').get('city', 'Ville inconnue')
        st.write(f"**Commune détectée :** {commune}")
    else:
        st.error("Adresse non trouvée. Veuillez vérifier votre saisie.")
        st.stop()

    #Afficher la carte avec la localisation
    
    m = folium.Map(location=[lat, lon], zoom_start=12)
    folium.Marker([lat, lon], popup="Domicile").add_to(m)
    st_folium(m, width=400, height=300)
    


    # Chargement des données
    @st.cache_data
    def load_data():
        stations = pd.read_excel('FINAL_STATIONS2012_2022.xlsx')
        pluvios = pd.read_excel('data_pluvios_2012-2022.xlsx')
        return stations, pluvios

    stations, pluvios = load_data()

    # Recherche de la station la plus proche
    def distance_euclidienne(lat1, lon1, lat2, lon2):
        return np.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)

    stations['DISTANCE'] = stations.apply(
        lambda row: distance_euclidienne(lat, lon, row['LAT'], row['LON']), axis=1)
    station_plus_proche = stations.loc[stations['DISTANCE'].idxmin(), 'NOM_STATION']
    st.write(f"**Station de relevés pluviométriques la plus proche :** {station_plus_proche}")

    # Récupération des données pluviométriques
    if station_plus_proche in pluvios.columns:
        pluvio_locale = pluvios[['DATE', station_plus_proche]].copy()
    else:
        st.error(f"La station {station_plus_proche} n'existe pas dans les données pluviométriques.")
        st.stop()

    # Entrée des paramètres utilisateur
    
    st.markdown(
    """
    <div style="color:#095a9c; font-size: 24px; border-bottom: 3px solid #095a9c; padding-bottom: 5px;">
        Informations de l'usager
    </div>
    """,
    unsafe_allow_html=True
)
    surface_toit = st.number_input("Entrez votre surface de toit (en m²) :", min_value=0.0, format="%.2f")
    personnes = st.number_input("Entrez le nombre de personnes vivant dans le foyer :", min_value=1, format="%d")

    toiture_options = {
        'En pente à surface lisse': 0.9,
        'En pente à surface rugueuse': 0.8,
        'Toit plat': 0.8,
        'Toiture végétalisée': 0.4
    }

    toiture_type = st.selectbox(
        "Choisissez votre type de toiture :",
        list(toiture_options.keys())
    )

    coeff_ruis = toiture_options[toiture_type]
    coeff_systeme = 0.9

    # Calcul du potentiel récupérable
    pluvio_locale['RECUPERABLE'] = (pluvio_locale.iloc[:, 1] / 1000) * surface_toit * coeff_ruis * coeff_systeme
    pluie_recuperable = pluvio_locale['RECUPERABLE']

    # Sélection des usages
    
    st.markdown(
    """
    <div style="color:#095a9c; font-size: 24px; border-bottom: 3px solid #095a9c; padding-bottom: 5px;">
        Sélection des Usages
    </div>
    """,
    unsafe_allow_html=True
)
    wc_usage = st.radio("Voulez-vous raccorder les WC à l'eau de pluie ?", ('Oui', 'Non'))
    arrosage_usage = st.radio("Utilisez-vous l'arrosage ?", ('Oui', 'Non'))

    arrosage_jour_valeur = 0
    if arrosage_usage == "Oui":
        surface_jardin = st.number_input("Entrez la superficie de votre jardin que vous arrosez (en m²) :", min_value=0.0, format="%.2f")
        arrosage_types = {
            'Econome': {'coeff_volume': 0.5, 'fois_sem': 1},
            'Raisonné': {'coeff_volume': 1, 'fois_sem': 1},
            'Abondant': {'coeff_volume': 1, 'fois_sem': 2}
        }
        arrosage_type = st.selectbox("Choisissez votre type d'arrosage :", list(arrosage_types.keys()))
        coeff_volume = arrosage_types[arrosage_type]['coeff_volume']
        fois_sem = arrosage_types[arrosage_type]['fois_sem']
        volume_base = 20  # l/m²/sem
        arrosage_jour = (volume_base * coeff_volume * fois_sem) / 7
        arrosage_jour_valeur = (arrosage_jour / 1000) * surface_jardin  # en m³/jour

    # Calcul de la consommation
    WC_double_commande = 5  # litres par chasse
    WC_jour = 4  # chasses par jour par personne
    conso_wc = 0
    if wc_usage == 'Oui':
        conso_wc = (WC_double_commande * WC_jour * personnes) / 1000  # en m³/jour

    conso_jour = conso_wc + arrosage_jour_valeur
    
        # Utilisation de HTML avec st.markdown pour un formatage personnalisé

    
    st.markdown(
    f"""
    <h4 style='
        text-align: center;
        color: #2686d4;
        border: 2px solid #2686d4;
        padding: 10px;
        border-radius: 10px;
    '>
        Consommation journalière totale : {conso_jour:.2f} m³
    </h4>
    """,
    unsafe_allow_html=True
)
    
    
    st.markdown("<br>", unsafe_allow_html=True)  # Une ligne vide
    

    # Simulation du remplissage et vidage des cuvestaux
    
    st.markdown(
    """
    <div style="color:#095a9c; font-size: 24px; border-bottom: 3px solid #095a9c; padding-bottom: 5px;">
        Simulation et Résultats
    </div>
    """,
    unsafe_allow_html=True
)
    
    dates = pd.date_range(start='2012-01-01', periods=4018, freq='D')
    conso = pd.DataFrame({'DATE': dates})
    conso['WC'] = conso_wc
    conso['ARROSAGE'] = 0.0
    if arrosage_usage == 'Oui':
        mask_arrosage = (conso['DATE'].dt.month >= 5) & (conso['DATE'].dt.month <= 11)
        conso.loc[mask_arrosage, 'ARROSAGE'] = arrosage_jour_valeur
    conso['TOTAL_JOUR'] = conso[['WC', 'ARROSAGE']].sum(axis=1)

    # Définition des volumes de cuves à simuler
    volumes_cuves = np.arange(0.5, 10.5, 0.5)

    # Simulation pour chaque volume de cuve
    simulation_cuves = pd.DataFrame({'DATE': dates})
    for volume_cuve in volumes_cuves:
        Vj_1_list = []
        Vstocke_list = []
        trop_plein_list = []
        eau_reseau_list = []
        pluie_conso_list = []
        Vj_1 = 0
        for index in range(len(dates)):
            pluie_jour = pluie_recuperable.iloc[index]
            besoins_jour = conso['TOTAL_JOUR'].iloc[index]
            if pluie_jour + Vj_1 >= volume_cuve:
                Vstocke = volume_cuve
                trop_plein = pluie_jour + Vj_1 - volume_cuve
            else:
                Vstocke = pluie_jour + Vj_1
                trop_plein = 0
            if Vstocke >= besoins_jour:
                pluie_conso = besoins_jour
                eau_reseau = 0
                Vstocke -= besoins_jour
            else:
                pluie_conso = Vstocke
                eau_reseau = besoins_jour - pluie_conso
                Vstocke = 0
            Vj_1_list.append(Vj_1)
            Vstocke_list.append(Vstocke)
            trop_plein_list.append(trop_plein)
            eau_reseau_list.append(eau_reseau)
            pluie_conso_list.append(pluie_conso)
            Vj_1 = Vstocke
        simulation_cuves[f'VSTOCKE_{volume_cuve}'] = Vstocke_list
        simulation_cuves[f'PLUIE_CONSO_{volume_cuve}'] = pluie_conso_list
        simulation_cuves[f'EAU_RESEAU_{volume_cuve}'] = eau_reseau_list

    # Calcul des ratios pour chaque volume de cuve
    conso_totale = conso['TOTAL_JOUR'].sum()
    list_ratios = []
    for volume_cuve in volumes_cuves:
        pluie_conso_totale = sum(simulation_cuves[f'PLUIE_CONSO_{volume_cuve}'])
        couverture_besoins = (pluie_conso_totale / conso_totale) * 100
        list_ratios.append({
            'CUVES': volume_cuve,
            'COUVERTURE_BESOINS': couverture_besoins
        })
    df_ratios = pd.DataFrame(list_ratios)

    # Graphique du taux de couverture des besoins
    

    
        # Supposons que df_ratios soit défini quelque part dans votre code
    # Exemple de votre code
    fig, ax = plt.subplots()
    ax.plot(df_ratios['CUVES'], df_ratios['COUVERTURE_BESOINS'], marker='o')

    # Définir les limites des axes
    ax.set_ylim(0, 100)  # Fixer les limites de l'axe y entre 0 et 100

    # Définir les autres éléments du graphique
    ax.set_xlabel('Volume de la Cuve (m³)')
    ax.set_ylabel('Taux de Couverture des besoins (%)')
    ax.set_title('Taux de Couverture des besoins en fonction du volume de la cuve')
    ax.grid(True)

    # Afficher le graphique dans Streamlit
    st.pyplot(fig)

    # Calcul du volume optimal
    X = df_ratios['CUVES']
    Y = df_ratios['COUVERTURE_BESOINS']
    dY = np.diff(Y) / np.diff(X)
    volume_optimal_idx = np.argmin(np.abs(dY - (0.4 * dY[0])))
    volume_optimal = X.iloc[volume_optimal_idx]
    

    
    # Utilisation de HTML avec st.markdown pour un formatage personnalisé

    
    st.markdown(
    f"""
    <h4 style='
        text-align: center;
        color: #2686d4;
        border: 2px solid #2686d4;
        padding: 10px;
        border-radius: 10px;
    '>
        Le volume optimal estimé est : {volume_optimal} m³
    </h4>
    """,
    unsafe_allow_html=True
)

    st.markdown("<br>", unsafe_allow_html=True)  # Une ligne vide
    # Évolution du stockage pour le volume optimal
    
    recent_year = simulation_cuves.tail(365)
    volume_stocke_cuve_optimale = recent_year[f'VSTOCKE_{volume_optimal}']
    fig2, ax2 = plt.subplots()
    ax2.plot(recent_year['DATE'], volume_stocke_cuve_optimale, color='blue')
    ax2.set_xlabel("Date")
    ax2.set_ylabel('Volume Stocké (m³)')
    ax2.set_title("Évolution du volume stocké au cours de l'année")
    ax2.grid(True)
    st.pyplot(fig2)

    # Calcul des économies potentielles
    couts_eau = pd.read_excel('Couts_eau_outil.xlsx')
    response_assainissement = st.radio("Êtes-vous connecté à un système d'assainissement collectif ?", ('Oui', 'Non'))
    cout_eau_row = couts_eau[couts_eau['Commune'] == commune]
    if not cout_eau_row.empty:
        if response_assainissement == 'Oui':
            cout = cout_eau_row['eau_et_ass'].values[0]
        else:
            cout = cout_eau_row['eau_potable'].values[0]
    else:
        st.error("Données de coût de l'eau non disponibles pour votre commune.")
        st.stop()

    volumes_economises = []
    couts_economises = []
    for volume_cuve in volumes_cuves:
        volume_economise = sum(simulation_cuves[f'PLUIE_CONSO_{volume_cuve}']) / 11  # Sur 11 ans
        volumes_economises.append(volume_economise)
        couts_economises.append(volume_economise * cout)
    total_couts_economises = round((sum(couts_economises)/11),1)
    
    # Utilisation de HTML avec st.markdown pour un formatage personnalisé

    st.markdown(
    f"""
    <h4 style='
        text-align: center;
        color: #2686d4;
        border: 2px solid #2686d4;
        padding: 10px;
        border-radius: 10px;
    '>
        Vous pourriez potentiellement économiser : {total_couts_economises} euros par an
    </h4>
    """,
    unsafe_allow_html=True
)
    
    st.markdown("<br>", unsafe_allow_html=True)  # Une ligne vide
    # Graphique des économies réalisables
    
    fig3, ax3 = plt.subplots()
    ax3.plot(volumes_cuves, couts_economises, marker='o', color='green')
    ax3.set_xlabel('Volume de la cuve (m³)')
    ax3.set_ylabel('Économies réalisables (€ par an)')
    ax3.set_title("Potentiel d'économies en fonction du volume de la cuve")
    ax3.grid(True)
    st.pyplot(fig3)

    st.success("Calcul terminé. Vous pouvez consulter les graphiques ci-dessus pour analyser les résultats.")

import os
import zipfile
import xml.etree.ElementTree as ET
import requests

# URL du fichier ZIP contenant l'EPG
EPG_URL = "https://xmltvfr.fr/xmltv/xmltv.zip"

# Liste des chaînes à filtrer (ajoute les chaînes que tu veux inclure)
CHANNELS_TO_INCLUDE = ["6ter.fr", "BX1.be", "BelRTL.be", "ClubRTL.be", "ClubbingTV.fr", "Gulli.fr", "LN24.be", 
                       "LaDeux.be", "LaTrois.be", "LaUne.be", "M6.fr", "NRJ12.fr", "NT1.fr", "PlugRTL.be", 
                       "RTLTVI.be", "RadioContact.be", "TF1.fr", "TF1SeriesFilms.fr", "TMC.fr", "W9.fr"]

# Fonction pour télécharger et extraire le fichier XML depuis un fichier ZIP
def download_and_extract_zip(url, output_dir="epg_data"):
    print("Téléchargement du fichier ZIP...")
    response = requests.get(url)
    zip_filename = "epg_file.zip"
    
    with open(zip_filename, "wb") as file:
        file.write(response.content)
    
    print(f"Fichier ZIP téléchargé : {zip_filename}")
    
    # Extraction du fichier ZIP
    print(f"Extraction du fichier ZIP dans le répertoire {output_dir}...")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with zipfile.ZipFile(zip_filename, "r") as zip_ref:
        zip_ref.extractall(output_dir)
    
    # Vérification de l'existence du fichier XML
    for file_name in os.listdir(output_dir):
        if file_name.endswith(".xml"):
            xml_path = os.path.join(output_dir, file_name)
            print(f"Fichier XML trouvé : {xml_path}")
            return xml_path
    raise FileNotFoundError("Aucun fichier XML trouvé dans l'archive ZIP.")

# Fonction pour filtrer les chaînes et les programmes
def filter_channels(xml_file, channels_to_include):
    print("Filtrage des chaînes en cours...")
    tree = ET.parse(xml_file)
    root = tree.getroot()

    filtered_events = []

    # Affichage des chaînes disponibles dans le XML pour vérifier si celles que tu cherches existent
    print("Chaînes disponibles dans le fichier XML :")
    for channel in root.findall(".//channel"):
        channel_id = channel.get("id")
        print(f"Chaîne trouvée : {channel_id}")  # Affiche l'ID de chaque chaîne

    # Filtrer les programmes en fonction des chaînes désirées
    for channel in root.findall(".//channel"):
        channel_id = channel.get("id")
        if channel_id in channels_to_include:
            print(f"Chaîne incluse : {channel_id}")
            
            # Trouver tous les programmes associés à cette chaîne
            for programme in root.findall(f".//programme[@channel='{channel_id}']"):
                # Ajout du programme à la liste des événements filtrés
                filtered_events.append(programme)
                
                # Débogage pour vérifier qu'un programme a été bien ajouté
                print(f"Programme ajouté pour {channel_id}: {programme.find('title').text if programme.find('title') is not None else 'Pas de titre'}")

    print(f"Nombre d'événements filtrés : {len(filtered_events)}")
    return filtered_events

# Fonction pour créer un nouveau fichier XML filtré
def create_new_xml(filtered_events, output_file):
    print(f"Création du fichier XML filtré : {output_file}...")
    if filtered_events:
        print(f"Nombre d'événements à écrire : {len(filtered_events)}")
    else:
        print("Aucun événement à écrire.")
    
    # Créer un nouvel élément racine <tv>
    root = ET.Element("tv")
    
    # Ajouter chaque programme filtré au fichier XML
    for event in filtered_events:
        root.append(event)
    
    tree = ET.ElementTree(root)
    tree.write(output_file)
    
    print(f"Fichier XML créé avec succès sous le nom '{output_file}'.")

# Fonction principale pour orchestrer le téléchargement, extraction et filtrage
def main():
    try:
        # Télécharger et extraire le fichier ZIP contenant le XML
        xml_file = download_and_extract_zip(EPG_URL)

        # Filtrer les chaînes et les événements
        filtered_events = filter_channels(xml_file, CHANNELS_TO_INCLUDE)

        # Créer le fichier XML filtré
        create_new_xml(filtered_events, "filtered_epg.xml")
    
    except Exception as e:
        print(f"Une erreur est survenue : {str(e)}")

if __name__ == "__main__":
    main()

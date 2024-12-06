import os
import zipfile
import xml.etree.ElementTree as ET
import requests

# URL du fichier ZIP contenant l'EPG
EPG_URL = "https://xmltvfr.fr/xmltv/xmltv.zip"

# Liste des chaînes à filtrer
CHANNELS_TO_INCLUDE = [
    "6ter.fr", "BX1.be", "BelRTL.be", "ClubRTL.be", "ClubbingTV.fr", 
    "Gulli.fr", "LN24.be", "LaDeux.be", "LaTrois.be", "LaUne.be", 
    "M6.fr", "NRJ12.fr", "NT1.fr", "PlugRTL.be", "RTLTVI.be", 
    "RadioContact.be", "TF1.fr", "TF1SeriesFilms.fr", "TMC.fr", "W9.fr"
]

# Fonction pour télécharger et extraire le fichier ZIP
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

    # Filtrer les programmes en fonction des chaînes demandées
    for channel in root.findall(".//channel"):
        channel_id = channel.get("id")
        if channel_id in channels_to_include:
            print(f"Chaîne incluse : {channel_id}")
            
            # Trouver tous les programmes associés à cette chaîne
            for programme in root.findall(f".//programme[@channel='{channel_id}']"):
                filtered_events.append(programme)

    print(f"Nombre d'événements filtrés : {len(filtered_events)}")
    return filtered_events

# Fonction pour créer un fichier XML filtré
def create_new_xml(filtered_events, output_file):
    print(f"Création du fichier XML filtré : {output_file}...")
    
    # Créer un nouvel élément racine <tv>
    root = ET.Element("tv")
    
    # Ajouter les chaînes filtrées et les programmes
    for event in filtered_events:
        # Créer l'élément <channel> pour chaque programme
        channel_id = event.get("channel")
        channel_element = ET.Element("channel", id=channel_id)

        # Ajouter les informations de la chaîne (display-name, icon, etc.)
        channel = next((ch for ch in root.findall(".//channel") if ch.get("id") == channel_id), None)
        if channel is not None:
            display_name = channel.find("display-name")
            icon = channel.find("icon")
            if display_name is not None:
                channel_element.append(display_name)
            if icon is not None:
                channel_element.append(icon)

        # Ajouter les programmes au fichier XML
        programme = ET.Element("programme")
        programme.attrib = event.attrib  # Inclure les attributs (start, stop, etc.)

        for child in event:
            child_copy = ET.Element(child.tag, child.attrib)
            child_copy.text = child.text
            programme.append(child_copy)

        root.append(programme)

    # Créer l'arbre XML et l'écrire dans le fichier
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    
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

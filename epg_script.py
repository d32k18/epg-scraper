import os
import zipfile
import xml.etree.ElementTree as ET
import requests
from io import BytesIO

# 1. Télécharger le fichier ZIP de l'EPG depuis l'URL
def download_zip(epg_url):
    response = requests.get(epg_url)
    response.raise_for_status()  # Lancer une exception si l'URL échoue
    return zipfile.ZipFile(BytesIO(response.content))

# 2. Extraire le fichier XML à partir du ZIP
def extract_xml(zip_file):
    for file_name in zip_file.namelist():
        if file_name.endswith(".xml"):
            return zip_file.open(file_name)
    raise FileNotFoundError("Aucun fichier XML trouvé dans l'archive.")

# 3. Filtrer les chaînes d'intérêt
def filter_channels(xml_file, channels_to_include):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Filtrer les programmes en fonction des chaînes désirées
    filtered_events = []
    for channel in root.findall(".//channel"):
        channel_id = channel.get("id")
        if channel_id in channels_to_include:
            for programme in channel.findall(".//programme"):
                filtered_events.append(programme)

    return filtered_events

# 4. Créer un nouveau fichier XML avec les chaînes filtrées
def create_new_xml(filtered_events, output_file):
    # Créer une nouvelle structure XML
    root = ET.Element("tv")
    for event in filtered_events:
        root.append(event)
    
    # Écrire le fichier XML
    tree = ET.ElementTree(root)
    tree.write(output_file)

# 5. URL de l'EPG et chaînes à inclure
EPG_URL = "https://xmltvfr.fr/xmltv/xmltv.zip"  # Remplace par l'URL de ton fichier .zip
CHANNELS_TO_INCLUDE = ["chaine1", "chaine2", "chaine3"]  # Remplace par les identifiants des chaînes qui t'intéressent

# 6. Télécharger, extraire, filtrer et enregistrer
def main():
    zip_file = download_zip(EPG_URL)
    xml_file = extract_xml(zip_file)
    filtered_events = filter_channels(xml_file, CHANNELS_TO_INCLUDE)
    create_new_xml(filtered_events, "filtered_epg.xml")

if __name__ == "__main__":
    main()

import os
import zipfile
import xml.etree.ElementTree as ET
import requests
from io import BytesIO
import subprocess

# 1. Télécharger le fichier ZIP de l'EPG depuis l'URL
def download_zip(epg_url):
    print("Téléchargement du fichier ZIP en cours...")
    response = requests.get(epg_url)
    response.raise_for_status()  # Lancer une exception si l'URL échoue
    
    # Sauvegarde le fichier ZIP localement pour pouvoir le vérifier
    with open('epg_file.zip', 'wb') as f:
        f.write(response.content)
    print("Fichier ZIP téléchargé sous le nom 'epg_file.zip'.")
    return zipfile.ZipFile(BytesIO(response.content))

# 2. Extraire le fichier XML à partir du ZIP
def extract_xml(zip_file):
    print("Extraction du fichier XML...")
    for file_name in zip_file.namelist():
        if file_name.endswith(".xml"):
            print(f"Fichier XML trouvé : {file_name}")  # Affiche le nom du fichier XML
            return zip_file.open(file_name)
    raise FileNotFoundError("Aucun fichier XML trouvé dans l'archive.")

# 3. Filtrer les chaînes d'intérêt
def filter_channels(xml_file, channels_to_include):
    print("Filtrage des chaînes en cours...")
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Filtrer les programmes en fonction des chaînes désirées
    filtered_events = []
    for channel in root.findall(".//channel"):
        channel_id = channel.get("id")
        if channel_id in channels_to_include:
            print(f"Chaîne incluse : {channel_id}")
            for programme in channel.findall(".//programme"):
                filtered_events.append(programme)
    
    print(f"Nombre d'événements filtrés : {len(filtered_events)}")
    return filtered_events

# 4. Créer un nouveau fichier XML avec les chaînes filtrées
def create_new_xml(filtered_events, output_file):
    print(f"Création du fichier XML filtré : {output_file}...")
    root = ET.Element("tv")
    for event in filtered_events:
        root.append(event)
    
    tree = ET.ElementTree(root)
    tree.write(output_file)
    
    print(f"Fichier XML créé avec succès sous le nom '{output_file}'.")

# 5. Ajouter les fichiers générés à Git, commettre et pousser
def commit_and_push_files():
    print("Ajout des fichiers générés à Git...")
    subprocess.run(["git", "add", "epg_file.zip", "filtered_epg.xml"], check=True)
    subprocess.run(["git", "commit", "-m", "Ajout du fichier ZIP et du fichier XML filtré"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("Fichiers ajoutés, commités et poussés avec succès sur GitHub.")

# 6. URL de l'EPG et chaînes à inclure
EPG_URL = "https://xmltvfr.fr/xmltv/xmltv.zip"  # Remplace par l'URL de ton fichier .zip
CHANNELS_TO_INCLUDE = ["LaUne.be", "LaDeux.be", "LaTrois.be", "LN24.be", "RadioContact.be", "BelRTL.be", "RTLTVI.be", "ClubRTL.be", "PlugRTL.be", "BX1.be", "ClubbingTV.fr", "TF1.fr", "TF1SeriesFilms.fr", "TMC.fr", "NT1.fr", "NRJ12.fr", "M6.fr", "W9.fr", "6ter.fr", "Gulli.fr"]  # Remplace par les identifiants des chaînes qui t'intéressent

# 7. Télécharger, extraire, filtrer et enregistrer
def main():
    print("Début de l'exécution du script...")
    try:
        zip_file = download_zip(EPG_URL)
        print("ZIP téléchargé et extrait.")
        
        xml_file = extract_xml(zip_file)
        
        filtered_events = filter_channels(xml_file, CHANNELS_TO_INCLUDE)
        
        create_new_xml(filtered_events, "filtered_epg.xml")
        print("Script terminé avec succès.")
        
        # Ajouter les fichiers générés à Git et pousser
        commit_and_push_files()
        
    except Exception as e:
        print(f"Une erreur est survenue : {e}")

if __name__ == "__main__":
    main()

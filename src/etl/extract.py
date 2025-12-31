import os
import requests
import zipfile
from io import BytesIO

import yaml

# Configuration
CONFIG_PATH = "config/players.yaml"
BASE_URL = "https://www.pgnmentor.com/players/"
RAW_DATA_PATH = "data/raw"

def download_and_extract_pgn(player_name, output_dir):
    """
    Downloads a zip file from PGN Mentor and extracts the PGN inside.
    """
    url = f"{BASE_URL}{player_name}.zip"
    print(f"Downloading {player_name} games from {url}...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to download {player_name}. Status code: {response.status_code}")
            return False
        
        print(f"Download complete for {player_name}. Extracting...")
        
        with zipfile.ZipFile(BytesIO(response.content)) as z:
            z.extractall(output_dir)
            print(f"Extracted {player_name}: {z.namelist()}")
        return True
    except Exception as e:
        print(f"Error processing {player_name}: {e}")
        return False

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs(RAW_DATA_PATH, exist_ok=True)
    
    # Load config
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    
    players = config.get('players', [])
    
    for player in players:
        p_name = player.get('name')
        if p_name:
            download_and_extract_pgn(p_name, RAW_DATA_PATH)

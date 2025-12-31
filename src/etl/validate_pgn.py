import chess.pgn
import os
import yaml

CONFIG_PATH = "config/players.yaml"
RAW_DATA_PATH = "data/raw"


def validate_pgn(file_path):
    """
    Validates the PGN file by counting games and checking for basic readability.
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return
    
    print(f"Validating {file_path}...")
    game_count = 0
    
    with open(file_path, encoding="utf-8", errors="replace") as pgn_file:
        while True:
            # Read only the headers to speed up validation
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                break
            game_count += 1
            if game_count % 1000 == 0:
                print(f"Parsed {game_count} games...")
                
    print(f"Validation complete. Total games found: {game_count}")
    return game_count

if __name__ == "__main__":
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    
    players = config.get('players', [])

    for player in players:
        game_count = validate_pgn(RAW_DATA_PATH + "/" + player['name'] + ".pgn")
        
        if game_count and game_count > 0:
            print("PGN integrity verified.")
        else:
            print("PGN seems empty or invalid.")

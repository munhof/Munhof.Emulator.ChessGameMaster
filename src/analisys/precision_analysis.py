import chess
import chess.pgn
import chess.engine
import os
import yaml
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm

# Configuración
DATA_PATH = "data/raw"
CONFIG_PATH = "config/players.yaml"
# Ruta detectada del motor
ENGINE_PATH = os.path.join("bin", "stockfish", "stockfish", "stockfish-windows-x86-64-avx2.exe")
OUTPUT_DIR = os.path.join("out", "analisys", "precision")
GAMES_LIMIT = 5  # Analizar solo 5 partidas por jugador para esta demostración
TIME_LIMIT = 0.1  # Tiempo de análisis por movimiento (en segundos)

def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

def analyze_precision(game, engine, player_name):
    """Analiza la precisión de una partida calculeando ACPL y coincidencias."""
    board = game.board()
    player_cp_losses = []
    top_move_matches = 0
    total_moves = 0

    # Determinar si el jugador es blancas o negras
    player_is_white = game.headers.get("White") == player_name
    
    # Evaluar la posición inicial
    info = engine.analyse(board, chess.engine.Limit(time=TIME_LIMIT))
    prev_eval = info["score"].relative.score(mate_score=10000)

    for move in game.mainline_moves():
        is_player_turn = board.turn == player_is_white
        
        if is_player_turn:
            total_moves += 1
            # Obtener la mejor jugada del motor antes de que el jugador mueva
            analysis = engine.analyse(board, chess.engine.Limit(time=TIME_LIMIT))
            best_move = analysis["pv"][0] if "pv" in analysis else None
            
            if move == best_move:
                top_move_matches += 1

        # El jugador hace su jugada
        board.push(move)

        # Evaluar después del movimiento
        info = engine.analyse(board, chess.engine.Limit(time=TIME_LIMIT))
        current_eval = info["score"].relative.score(mate_score=10000)

        if is_player_turn and current_eval is not None and prev_eval is not None:
            # Centipawn Loss = Eval antes - Eval después
            # (El score es relativo al bando que movió, por lo que una pérdida es positiva)
            loss = max(0, prev_eval - (-current_eval))
            player_cp_losses.append(loss)

        # Actualizar evaluación previa para el siguiente turno (siempre invertida para el oponente)
        prev_eval = current_eval

    acpl = sum(player_cp_losses) / len(player_cp_losses) if player_cp_losses else 0
    accuracy = (top_move_matches / total_moves * 100) if total_moves > 0 else 0
    
    return acpl, accuracy

def main():
    ensure_output_dir()
    
    if not os.path.exists(ENGINE_PATH):
        print(f"Error: No se encontró el motor en {ENGINE_PATH}. Ejecuta scripts/setup_stockfish.py")
        return

    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    
    players = config.get('players', [])
    results = []

    # Iniciar motor
    engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)

    try:
        for player in players:
            player_name = player.get('name')
            player_path = os.path.join(DATA_PATH, f"{player_name}.pgn")
            
            if not os.path.exists(player_path):
                print(f"Warning: No se encontró el archivo PGN para {player_name}")
                continue

            print(f"Analizando {GAMES_LIMIT} partidas de {player_name}...")
            
            with open(player_path, "r", encoding="utf-8", errors="replace") as pgn_file:
                for i in tqdm(range(GAMES_LIMIT)):
                    game = chess.pgn.read_game(pgn_file)
                    if game is None:
                        break
                    
                    acpl, accuracy = analyze_precision(game, engine, player_name)
                    results.append({
                        "Player": player_name,
                        "Game": i + 1,
                        "ACPL": acpl,
                        "Precision": accuracy
                    })

    finally:
        engine.quit()

    # Guardar resultados y generar gráficos
    if results:
        df = pd.DataFrame(results)
        df.to_csv(os.path.join(OUTPUT_DIR, "precision_results.csv"), index=False)
        print(f"Resultados guardados en {OUTPUT_DIR}/precision_results.csv")

        # Gráfico ACPL
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=df, x="Player", y="ACPL", palette="viridis")
        plt.title(f"Average Centipawn Loss (Lower is Better) - Precision Analysis (Sample: {GAMES_LIMIT})")
        plt.savefig(os.path.join(OUTPUT_DIR, "acpl_comparison.png"))
        
        # Gráfico Precision
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df, x="Player", y="Precision", palette="magma", errorbar="sd")
        plt.title(f"Precision: Match Rate with Top Engine Move (%) - Sample: {GAMES_LIMIT}")
        plt.savefig(os.path.join(OUTPUT_DIR, "precision_comparison.png"))
        
        print("Gráficos generados en el directorio out/analisys/precision/")

if __name__ == "__main__":
    main()

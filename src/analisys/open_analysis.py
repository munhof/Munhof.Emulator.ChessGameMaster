import chess.pgn
import os
import yaml
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

import json

DATA_PATH = "data/raw"
CONFIG_PATH = "config/players.yaml"
ECO_MAP_PATH = "src/analisys/eco_map.json"
OUTPUT_DIR = "out/analisys/openings"
TOP_K = 10  # Número de aperturas más usadas a mostrar

def load_eco_map():
    """Carga el mapeo de códigos ECO desde un archivo JSON."""
    if os.path.exists(ECO_MAP_PATH):
        with open(ECO_MAP_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    print(f"Warning: ECO map not found at {ECO_MAP_PATH}")
    return {}

ECO_MAP = load_eco_map()

def ensure_output_dir():
    """Crea el directorio de salida si no existe."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_all_games(player_path):
    """Lee todas las partidas de un archivo PGN."""
    games = []
    if not os.path.exists(player_path):
        print(f"Warning: File not found: {player_path}")
        return []
        
    with open(player_path, 'r', encoding='utf-8', errors='replace') as pgn_file:
        while True:
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                break
            games.append(game)
    return games

def get_opening_stats(games):
    """Extrae los códigos ECO y sus frecuencias de una lista de partidas."""
    # Usamos el código ECO y lo mapeamos a nombre si es posible
    eco_codes = [game.headers.get('ECO', 'Unknown') for game in games]
    return Counter(eco_codes)

def plot_individual_analysis(player_name, stats):
    """Genera visualizaciones individuales para un jugador."""
    ensure_output_dir()
    
    if not stats:
        return

    # Mapear ECO a nombres para el gráfico
    data = []
    for eco, freq in stats.items():
        name = ECO_MAP.get(eco, eco) # Usa el nombre si existe, sino el código
        data.append({'Opening': name, 'Frequency': freq, 'ECO': eco})

    df = pd.DataFrame(data).sort_values(by='Frequency', ascending=False)
    top_df = df.head(TOP_K)

    plt.figure(figsize=(12, 8))
    ax = sns.barplot(data=top_df, x='Frequency', y='Opening', palette='magma')
    
    plt.title(f'Top {TOP_K} Openings for {player_name}', fontsize=15)
    plt.xlabel('Number of Games', fontsize=12)
    plt.ylabel('Opening Name / ECO', fontsize=12)
    
    for i in ax.containers:
        ax.bar_label(i, padding=3)

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, f"{player_name}_openings.png")
    plt.savefig(output_path)
    plt.close()
    # print(f"Saved individual plot to {output_path}")

def plot_normalized_heatmap(all_stats, total_games):
    """Genera un heatmap 2D normalizado (Jugadores vs Aperturas en %)."""
    ensure_output_dir()
    
    players = list(all_stats.keys())
    # Obtener el top K de aperturas globales para el heatmap
    global_counter = Counter()
    for stats in all_stats.values():
        global_counter.update(stats)
    
    top_k_eco = [item[0] for item in global_counter.most_common(TOP_K)]
    top_k_names = [ECO_MAP.get(eco, eco) for eco in top_k_eco]

    # Construir matriz de datos normalizados (%)
    heatmap_data = []
    for eco in top_k_eco:
        row = []
        for player in players:
            count = all_stats[player].get(eco, 0)
            total = total_games.get(player, 1) # Evitar div por cero
            percent = (count / total) * 100
            row.append(percent)
        heatmap_data.append(row)

    df_heatmap = pd.DataFrame(heatmap_data, index=top_k_names, columns=players)

    plt.figure(figsize=(14, 10))
    sns.heatmap(df_heatmap, annot=True, fmt=".1f", cmap="YlGnBu", cbar_kws={'label': 'Usage Frequency (%)'})
    
    plt.title(f'Top {TOP_K} Opening Choice Heatmap (Normalized %)', fontsize=16)
    plt.xlabel('Players', fontsize=12)
    plt.ylabel('Openings', fontsize=12)
    plt.tight_layout()
    
    output_path = os.path.join(OUTPUT_DIR, "normalized_opening_heatmap.png")
    plt.savefig(output_path)
    plt.close()
    print(f"Saved normalized heatmap to {output_path}")

def plot_3d_comparison(all_stats, total_games):
    """Genera un cubo 3D con mejor alineación y etiquetas."""
    ensure_output_dir()
    
    players = list(all_stats.keys())
    global_counter = Counter()
    for stats in all_stats.values():
        global_counter.update(stats)
    
    top_k_eco = [item[0] for item in global_counter.most_common(TOP_K)]
    top_k_names = [ECO_MAP.get(eco, eco) for eco in top_k_eco]

    fig = plt.figure(figsize=(16, 12))
    ax = fig.add_subplot(111, projection='3d')

    x_pos = np.arange(len(players))
    y_pos = np.arange(len(top_k_eco))
    x_mesh, y_mesh = np.meshgrid(x_pos, y_pos)
    
    x_flat = x_mesh.flatten()
    y_flat = y_mesh.flatten()
    z_flat = np.zeros_like(x_flat)
    
    dx = 0.4 * np.ones_like(z_flat)
    dy = 0.4 * np.ones_like(z_flat)
    dz = []

    for y_idx in range(len(top_k_eco)):
        for x_idx in range(len(players)):
            player = players[x_idx]
            eco = top_k_eco[y_idx]
            count = all_stats[player].get(eco, 0)
            total = total_games.get(player, 1)
            dz.append((count / total) * 100) # Usar % también aquí

    colors = plt.cm.viridis(np.linspace(0, 1, len(players)))
    bar_colors = []
    for y_idx in range(len(top_k_eco)):
        for x_idx in range(len(players)):
            bar_colors.append(colors[x_idx])

    ax.bar3d(x_flat, y_flat, z_flat, dx, dy, dz, color=bar_colors, alpha=0.8)

    # REGLA: Ajustar etiquetas para evitar solapamiento
    ax.set_xticks(x_pos + 0.2)
    ax.set_xticklabels(players, rotation=35, ha='right')
    
    ax.set_yticks(y_pos + 0.2)
    ax.set_yticklabels(top_k_names, rotation=-15, ha='left', fontsize=9)
    
    ax.set_zlabel('Frequency (%)')
    ax.set_title(f'3D Comparison: Top {TOP_K} Normalized Opening Usage (%)')

    # Mejorar el ángulo de visión inicial
    ax.view_init(elev=30, azim=135)

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, "3d_normalized_comparison.png")
    plt.savefig(output_path)
    plt.close()
    print(f"Saved 3D normalized plot to {output_path}")

import plotly.graph_objects as go
import plotly.express as px

def create_3d_bar(x_val, y_val, z_val, x_idx, y_idx, color, player_name, opening_name, percent, count):
    """Crea los datos para un cubo 3D (Mesh3d) en Plotly."""
    width = 0.4
    # Definir los 8 vértices del cubo
    x = [x_idx-width, x_idx-width, x_idx+width, x_idx+width, x_idx-width, x_idx-width, x_idx+width, x_idx+width]
    y = [y_idx-width, y_idx+width, y_idx+width, y_idx-width, y_idx-width, y_idx+width, y_idx+width, y_idx-width]
    z = [0, 0, 0, 0, z_val, z_val, z_val, z_val]
    
    # Definir las caras con triángulos (i, j, k son índices de vértices)
    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]
    
    hover_text = f"Player: {player_name}<br>Opening: {opening_name}<br>Usage: {percent:.2f}% ({count} games)"
    
    return go.Mesh3d(
        x=x, y=y, z=z,
        i=i, j=j, k=k,
        color=color,
        opacity=0.8,
        name=player_name,
        text=hover_text,
        hoverinfo='text'
    )

def plot_interactive_3d(all_stats, total_games):
    """Genera un gráfico 3D interactivo con barras sólidas (Mesh3d)."""
    ensure_output_dir()
    
    players = list(all_stats.keys())
    global_counter = Counter()
    for stats in all_stats.values():
        global_counter.update(stats)
    
    top_k_eco = [item[0] for item in global_counter.most_common(TOP_K)]
    top_k_names = [ECO_MAP.get(eco, eco) for eco in top_k_eco]

    fig = go.Figure()
    
    # Colores profesionales
    player_colors = px.colors.qualitative.Plotly

    for x_idx, player in enumerate(players):
        for y_idx, eco in enumerate(top_k_eco):
            count = all_stats[player].get(eco, 0)
            if count == 0: continue
            
            total = total_games.get(player, 1)
            percent = (count / total) * 100
            
            color = player_colors[x_idx % len(player_colors)]
            
            fig.add_trace(create_3d_bar(
                player, top_k_names[y_idx], percent, 
                x_idx, y_idx, color, 
                player, top_k_names[y_idx], percent, count
            ))

    fig.update_layout(
        title=f'Interactive Opening Histogram Cube - Top {TOP_K} (%)',
        scene=dict(
            xaxis=dict(tickvals=list(range(len(players))), ticktext=players, title='Players'),
            yaxis=dict(tickvals=list(range(len(top_k_names))), ticktext=top_k_names, title='Openings'),
            zaxis=dict(title='Frequency (%)'),
            camera=dict(eye=dict(x=1.8, y=1.8, z=1.2))
        ),
        template='plotly_dark',
        showlegend=False,
        margin=dict(l=0, r=0, b=0, t=40)
    )

    output_path = os.path.join(OUTPUT_DIR, "interactive_opening_cube.html")
    fig.write_html(output_path)
    print(f"Saved interactive voxel plot to {output_path}")

def main():
    if not os.path.exists(CONFIG_PATH):
        print(f"Error: Config file not found at {CONFIG_PATH}")
        return

    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    
    players = config.get('players', [])
    all_player_stats = {}
    total_games_per_player = {}
    
    for player in players:
        player_name = player.get('name')
        player_path = os.path.join(DATA_PATH, f"{player_name}.pgn")
        
        print(f"Analyzing games for {player_name}...")
        games = get_all_games(player_path)
        num_games = len(games)
        print(f"Found {num_games} games.")
        
        if games:
            stats = get_opening_stats(games)
            all_player_stats[player_name] = stats
            total_games_per_player[player_name] = num_games
            plot_individual_analysis(player_name, stats)
            
    if all_player_stats:
        plot_normalized_heatmap(all_player_stats, total_games_per_player)
        plot_3d_comparison(all_player_stats, total_games_per_player)
        plot_interactive_3d(all_player_stats, total_games_per_player)

if __name__ == "__main__":
    main()

        
    
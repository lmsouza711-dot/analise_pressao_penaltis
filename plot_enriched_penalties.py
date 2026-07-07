import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

def generate_spaced_chart(file_path, output_img):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    df = pd.read_excel(file_path)
    
    # Style configuration for dark theme
    plt.rcParams['figure.facecolor'] = '#0f172a' # slate-900
    plt.rcParams['axes.facecolor'] = '#1e293b'   # slate-800
    plt.rcParams['text.color'] = '#f8fafc'       # slate-50
    plt.rcParams['axes.labelcolor'] = '#cbd5e1'  # slate-300
    plt.rcParams['xtick.color'] = '#cbd5e1'
    plt.rcParams['ytick.color'] = '#cbd5e1'
    plt.rcParams['font.sans-serif'] = 'Segoe UI'
    plt.rcParams['font.family'] = 'sans-serif'
    
    # Increase height to allow plenty of space for up/down labels
    fig, ax = plt.subplots(figsize=(12, 8.5), dpi=300)
    
    players = ['Rayan', 'Matheus Cunha', 'Bruno Guimarães', 'Vini Jr']
    # Double the Y gap between players (0, 2, 4, 6) to prevent overlap
    player_y_map = {player: idx * 2.0 for idx, player in enumerate(players)}
    
    df = df[df['Jogador'].isin(players)].copy()
    
    # Adding Y jitter
    np.random.seed(42)
    df['y_jittered'] = df['Jogador'].map(player_y_map) + np.random.uniform(-0.25, 0.25, len(df))
    
    # Plot converted
    df_conv = df[df['converteu'] == True]
    ax.scatter(df_conv['pressure_ahp'], df_conv['y_jittered'], 
               color='#10b981', s=240, label='Convertido', 
               edgecolors='#047857', linewidth=1.5, zorder=3, alpha=0.9)
    
    # Plot missed
    df_miss = df[df['converteu'] == False]
    ax.scatter(df_miss['pressure_ahp'], df_miss['y_jittered'], 
               color='#ef4444', s=260, label='Perdido', 
               marker='X', edgecolors='#b91c1c', linewidth=1.5, zorder=3, alpha=0.9)
    
    # Alternate labels up and down to prevent horizontal overlapping
    for player in players:
        df_player = df[(df['Jogador'] == player) & ((df['pressure_ahp'] >= 35.0) | (~df['converteu']))].copy()
        # Sort by X coordinate (pressure_ahp) to alternate logically
        df_player = df_player.sort_values(by='pressure_ahp')
        
        for i, (idx, row) in enumerate(df_player.iterrows()):
            opponent = row['Adversário']
            label = f"{opponent} ({row['minuto']}')\nScore: {row['pressure_ahp']:.1f}"
            
            # Alternate label offsets
            if i % 2 == 0:
                xytext = (0, 16)
                va = 'bottom'
            else:
                xytext = (0, -32)
                va = 'top'
                
            ax.annotate(label, 
                        (row['pressure_ahp'], row['y_jittered']),
                        textcoords="offset points", 
                        xytext=xytext, 
                        ha='center', 
                        va=va,
                        fontsize=7.5, 
                        color='#f1f5f9',
                        fontweight='bold' if row['pressure_ahp'] >= 50 else 'normal',
                        bbox=dict(boxstyle="round,pad=0.3", fc="#0f172a", alpha=0.75, ec="#334155", lw=0.5))
            
    ax.set_yticks([idx * 2.0 for idx in range(len(players))])
    ax.set_yticklabels(['Rayan Vitor' if p == 'Rayan' else p for p in players], 
                       fontsize=12, fontweight='bold')
    
    ax.set_xlabel('Pressure Score (AHP) - Escala de 0 a 100 (Cálculo Multicritério)', fontsize=12, labelpad=12)
    ax.set_title('Pênaltis Cobrados sob Pressão: Jogadores do Ataque da Seleção', fontsize=16, pad=20, fontweight='bold')
    
    ax.grid(True, linestyle='--', alpha=0.15, color='#cbd5e1', zorder=1)
    ax.set_xlim(-5, 105)
    ax.set_ylim(-1.2, len(players) * 2.0 - 0.8)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#334155')
    ax.spines['bottom'].set_color('#334155')
    
    ax.legend(loc='lower right', facecolor='#1e293b', edgecolor='#334155', framealpha=0.9)
    
    plt.figtext(0.05, 0.01, '* Pesos obtidos via AHP: Placar/GameState (41.8%), Tempo/Minuto (24.8%), Importância/Fase (22.5%), Nível Competitivo (10.9%).', 
                fontsize=8, color='#94a3b8', style='italic')
    
    plt.tight_layout()
    plt.savefig(output_img, dpi=300)
    print(f"Chart saved successfully to: {output_img}")
    plt.close()

if __name__ == "__main__":
    file_path = "Analise_Indice_Penalti_Enriquecido.xlsx"
    output_img = "docs/pressure_analysis.png"
    generate_spaced_chart(file_path, output_img)

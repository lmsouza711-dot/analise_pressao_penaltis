import pandas as pd
import numpy as np
import sys

def parse_emoji(val):
    if pd.isna(val):
        return False
    val_str = str(val)
    return '✅' in val_str

def clean_minute(val):
    if pd.isna(val):
        return 0
    val_str = str(val).replace("'", "").strip()
    try:
        return int(val_str)
    except ValueError:
        return 0

def enrich_dataset_no_norway(file_path):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    df = pd.read_excel(file_path, sheet_name=0)
    
    # 1. Fix the labeling error: Change 'Martinelli' to 'Bruno Guimarães'
    # Row 13, 14, 15 are Lyon vs Lorient (2021) and Newcastle vs Leeds/Brentford (2026), which are Bruno Guimarães' penalties.
    df.loc[df['Jogador'] == 'Martinelli', 'Jogador'] = 'Bruno Guimarães'
    
    # 2. Define new rows to append (Cunha and Rayan, excluding Norway match)
    new_rows = [
        # Matheus Cunha - Hertha vs Augsburg (Bundesliga)
        {
            'Jogador': 'Matheus Cunha',
            'Data': pd.to_datetime('2020-11-07'),
            'Competição': 'Bundesliga',
            'Etapa': 'Rodada 7',
            'Mata-mata?': '❌',
            'Seleção?': '❌',
            'Clássico?': '❌',
            'Adversário': 'Augsburg',
            'Resultado Final': '3-0',
            'Min.': "44'",
            'Placar no momento': '0x0',
            'Empate?': '✅',
            'Dif. Gols': 0,
            'Mudaria o resultado?': '✅',
            'Converteu?': '✅',
            'Pressão': np.nan
        },
        # Matheus Cunha - Hertha vs Dortmund (Bundesliga)
        {
            'Jogador': 'Matheus Cunha',
            'Data': pd.to_datetime('2020-11-21'),
            'Competição': 'Bundesliga',
            'Etapa': 'Rodada 8',
            'Mata-mata?': '❌',
            'Seleção?': '❌',
            'Clássico?': '❌',
            'Adversário': 'Dortmund',
            'Resultado Final': '2-5',
            'Min.': "79'",
            'Placar no momento': '1x4',
            'Empate?': '❌',
            'Dif. Gols': 3,
            'Mudaria o resultado?': '❌',
            'Converteu?': '✅',
            'Pressão': np.nan
        },
        # Matheus Cunha - Wolves vs Brentford (FA Cup)
        {
            'Jogador': 'Matheus Cunha',
            'Data': pd.to_datetime('2024-01-16'),
            'Competição': 'FA Cup',
            'Etapa': 'Oitavas (volta)',
            'Mata-mata?': '✅',
            'Seleção?': '❌',
            'Clássico?': '❌',
            'Adversário': 'Brentford',
            'Resultado Final': '3-2',
            'Min.': "105'",
            'Placar no momento': '2x2',
            'Empate?': '✅',
            'Dif. Gols': 0,
            'Mudaria o resultado?': '✅',
            'Converteu?': '✅',
            'Pressão': np.nan
        },
        # Matheus Cunha - Chelsea vs Wolves (Premier League)
        {
            'Jogador': 'Matheus Cunha',
            'Data': pd.to_datetime('2024-02-04'),
            'Competição': 'Premier League',
            'Etapa': 'Rodada 23',
            'Mata-mata?': '❌',
            'Seleção?': '❌',
            'Clássico?': '❌',
            'Adversário': 'Chelsea',
            'Resultado Final': '4-2',
            'Min.': "85'",
            'Placar no momento': '3x1',
            'Empate?': '❌',
            'Dif. Gols': 2,
            'Mudaria o resultado?': '❌',
            'Converteu?': '✅',
            'Pressão': np.nan
        },
        # Rayan - Vasco vs Santos (Brasileirão)
        {
            'Jogador': 'Rayan',
            'Data': pd.to_datetime('2025-08-24'),
            'Competição': 'Brasileirão',
            'Etapa': 'Rodada 22',
            'Mata-mata?': '❌',
            'Seleção?': '❌',
            'Clássico?': '❌',
            'Adversário': 'Santos',
            'Resultado Final': '2-1',
            'Min.': "65'",
            'Placar no momento': '1x1',
            'Empate?': '✅',
            'Dif. Gols': 0,
            'Mudaria o resultado?': '✅',
            'Converteu?': '✅',
            'Pressão': np.nan
        }
    ]
    
    new_df = pd.DataFrame(new_rows)
    df = pd.concat([df, new_df], ignore_index=True)
    
    # 3. Clean and process features
    df['is_mata_mata'] = df['Mata-mata?'].apply(parse_emoji)
    df['is_selecao'] = df['Seleção?'].apply(parse_emoji)
    df['is_classico'] = df['Clássico?'].apply(parse_emoji)
    df['is_empate'] = df['Empate?'].apply(parse_emoji)
    df['mudaria_resultado'] = df['Mudaria o resultado?'].apply(parse_emoji)
    df['converteu'] = df['Converteu?'].apply(parse_emoji)
    df['minuto'] = df['Min.'].apply(clean_minute)
    
    # Extract score details
    def get_score_details(row):
        placar = str(row['Placar no momento']).strip()
        try:
            parts = placar.split('x')
            a = int(parts[0])
            b = int(parts[1])
        except Exception:
            try:
                parts = placar.split('-')
                a = int(parts[0])
                b = int(parts[1])
            except Exception:
                a, b = 0, 0
            
        is_losing = a < b
        is_drawing = a == b
        diff = abs(a - b)
        
        # Competição
        comp_name = str(row['Competição']).lower()
        if 'champions' in comp_name:
            comp_score = 2
        elif row['is_selecao']:
            comp_score = 3
        else:
            comp_score = 1
            
        # Etapa
        etapa_name = str(row['Etapa']).lower()
        if 'oitavas' in etapa_name:
            etapa_score = 1
        elif 'quartas' in etapa_name:
            etapa_score = 2
        elif 'semifinal' in etapa_name:
            etapa_score = 3
        elif 'final' in etapa_name:
            etapa_score = 4
        else:
            etapa_score = 0
            
        classico_score = 1 if row['is_classico'] else 0
        matamata_score = 2 if row['is_mata_mata'] else 0
        empate_score = 2 if is_drawing else 0
        perdendo_score = 3 if is_losing else 0
        
        # Minuto
        m = row['minuto']
        if m >= 76:
            minuto_score = 3
        elif m >= 61:
            minuto_score = 2
        elif m >= 31:
            minuto_score = 1
        else:
            minuto_score = 0
            
        # Importância
        if is_drawing:
            importance_score = 3
        elif is_losing:
            importance_score = 2 if diff == 1 else 1
        else:
            importance_score = 0
            
        return pd.Series([
            comp_score, etapa_score, classico_score, matamata_score,
            empate_score, perdendo_score, minuto_score, importance_score
        ])

    df[[
        'h_comp', 'h_etapa', 'h_classico', 'h_matamata',
        'h_empate', 'h_perdendo', 'h_minuto', 'h_importance'
    ]] = df.apply(get_score_details, axis=1)
    
    # Calculate Heuristic Score
    df['pressure_heuristic'] = (
        df['h_comp'] + df['h_etapa'] + df['h_classico'] + df['h_matamata'] +
        df['h_empate'] + df['h_perdendo'] + df['h_minuto'] + df['h_importance']
    )
    
    # AHP weights
    w_comp = 0.109
    w_game = 0.225
    w_placar = 0.418
    w_time = 0.248
    
    # Dimension Scores normalized to 0-10
    df['dim_comp'] = ((df['h_comp'] + df['h_classico']) / 4.0) * 10.0
    df['dim_game'] = ((df['h_etapa'] + df['h_matamata']) / 6.0) * 10.0
    df['dim_placar'] = ((df['h_empate'] + df['h_perdendo'] + df['h_importance']) / 8.0) * 10.0
    df['dim_time'] = (df['h_minuto'] / 3.0) * 10.0
    
    # AHP Score (0-100)
    df['pressure_ahp'] = (
        w_comp * df['dim_comp'] +
        w_game * df['dim_game'] +
        w_placar * df['dim_placar'] +
        w_time * df['dim_time']
    ) * 10.0
    
    # Save files
    enriched_excel = file_path.replace(".xlsx", "_enriquecido.xlsx")
    df.to_excel(enriched_excel, index=False)
    
    print("--- Enriched Penalty Dataset Statistics (No Norway) ---")
    print(f"Total penalties recorded: {len(df)}")
    
    print("\n--- Recalculated CPI per Player ---")
    for player in df['Jogador'].unique():
        df_player = df[df['Jogador'] == player]
        sum_ahp_all = df_player['pressure_ahp'].sum()
        sum_ahp_conv = df_player[df_player['converteu'] == True]['pressure_ahp'].sum()
        cpi_ahp = sum_ahp_conv / sum_ahp_all if sum_ahp_all > 0 else 0
        
        # Calculate average pressure faced by player
        avg_pressure = df_player['pressure_ahp'].mean()
        max_pressure = df_player['pressure_ahp'].max()
        
        print(f"Player: {player:18s} | Penalties: {len(df_player)} | Converted: {df_player['converteu'].sum()} | Avg Pressure: {avg_pressure:.1f} | Max Pressure: {max_pressure:.1f} | CPI (AHP): {cpi_ahp:.3f}")

if __name__ == "__main__":
    file_path = r"C:\Users\Lucas Mesquita\Downloads\Analise - Indice de penalti (1).xlsx"
    enrich_dataset_no_norway(file_path)

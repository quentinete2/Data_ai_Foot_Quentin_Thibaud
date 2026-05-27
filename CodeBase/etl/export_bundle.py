"""
Export du bundle complet : modèle tuned + stats d'équipes
Réutilise le modèle de training_phase2_2.py et ajoute les stats du notebook
"""
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split

print("="*80)
print("EXPORT DU BUNDLE COMPLET")
print("="*80)

# 1. Chargement du modèle tuned de training_phase2_2.py
print("\n1️⃣ Chargement du modèle tuned...")
model_path_candidates = [
    "model_final.pkl",
    Path(__file__).parent / "model_final.pkl",
    Path(__file__).parents[1] / "model_final.pkl",
]
model_tuned = None
for path in model_path_candidates:
    if Path(path).exists():
        model_tuned = joblib.load(path)
        print(f"✓ Modèle tuned chargé de {path} : {type(model_tuned).__name__}")
        break

if model_tuned is None:
    print("❌ model_final.pkl non trouvé. Lancez training_phase2_2.py d'abord.")
    exit(1)

# 2. Chargement des données pour extraire stats
print("\n2️⃣ Chargement des données pour les stats...")
URL_MATCHES = "https://raw.githubusercontent.com/quentinete2/Data_ai_Foot_Quentin_Thibaud/master/Ressources/Data/matches.csv"
URL_TOURNAMENTS = "https://raw.githubusercontent.com/quentinete2/Data_ai_Foot_Quentin_Thibaud/master/Ressources/Data/tournaments.csv"

df_matches = pd.read_csv(URL_MATCHES)
df_tournaments = pd.read_csv(URL_TOURNAMENTS)
df_matches = df_matches.merge(
    df_tournaments[['tournament_id', 'year', 'host_country', 'count_teams']],
    on='tournament_id', how='left'
)
print(f"✓ {len(df_matches)} matchs chargés")

# 3. Création de la cible
conditions = [
    (df_matches['home_team_win'] == 1),
    (df_matches['draw'] == 1),
    (df_matches['away_team_win'] == 1)
]
df_matches['result'] = np.select(conditions, [0, 1, 2], default=np.nan)
df_matches = df_matches.dropna(subset=['result'])

# 4. Génération des stats par équipe
print("\n3️⃣ Calcul des statistiques d'équipes...")

def create_team_features(df, team_column, score_column):
    team_stats = {}
    for team in df[team_column].unique():
        team_data = df[df[team_column] == team]
        # Pour home_team_win, la cible est 0 = victoire à domicile
        wins_home = len(team_data[team_data['result'] == 0]) if team_column == 'home_team_name' else 0
        wins_away = len(team_data[team_data['result'] == 2]) if team_column == 'away_team_name' else 0
        total_wins = wins_home + wins_away
        
        team_stats[team] = {
            'avg_goals': float(team_data[score_column].mean()),
            'total_matches': int(len(team_data)),
            'wins': int(total_wins),
        }
    return team_stats

home_stats = create_team_features(
    df_matches[df_matches['home_team_score'].notna()], 
    'home_team_name', 
    'home_team_score'
)
away_stats = create_team_features(
    df_matches[df_matches['away_team_score'].notna()], 
    'away_team_name', 
    'away_team_score'
)
print(f"✓ {len(home_stats)} équipes analysées")

# 5. Calcul des médianes
median_year = float(df_matches['year'].median())
median_count_teams = float(df_matches['count_teams'].median())
print(f"  - Année médiane : {median_year}")
print(f"  - Équipes médiane : {median_count_teams}")

# 6. Création du bundle
print("\n4️⃣ Création du bundle...")
bundle = {
    "model": model_tuned,
    "home_stats": home_stats,
    "away_stats": away_stats,
    "median_year": median_year,
    "median_count_teams": median_count_teams,
}
print(f"✓ Bundle créé avec clés : {list(bundle.keys())}")

# 7. Export
output_path = Path(__file__).parents[1] / "backend" / "model.pkl"
joblib.dump(bundle, output_path)
print(f"\n✅ Bundle exporté vers : {output_path}")
print(f"   Taille : {output_path.stat().st_size / 1024:.1f} KB")
print("\nℹ️  main.py peut maintenant charger le modèle au démarrage.")

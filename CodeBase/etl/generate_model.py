"""Script de génération de model.pkl — extrait du notebook Data_ia_foot.ipynb."""
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# 1. Chargement des données
URL_MATCHES = "https://raw.githubusercontent.com/quentinete2/Data_ai_Foot_Quentin_Thibaud/master/Ressources/Data/matches.csv"
URL_TOURNAMENTS = "https://raw.githubusercontent.com/quentinete2/Data_ai_Foot_Quentin_Thibaud/master/Ressources/Data/tournaments.csv"

print("Chargement des données...")
df_matches = pd.read_csv(URL_MATCHES)
df_tournaments = pd.read_csv(URL_TOURNAMENTS)
df_matches = df_matches.merge(
    df_tournaments[['tournament_id', 'year', 'host_country', 'count_teams']],
    on='tournament_id', how='left'
)
print(f"✓ {len(df_matches)} matchs chargés")

# 2. Cible
conditions = [
    (df_matches['home_team_win'] == 1),
    (df_matches['draw'] == 1),
    (df_matches['away_team_win'] == 1)
]
df_matches['result'] = np.select(conditions, [0, 1, 2], default=np.nan)
df_matches = df_matches.dropna(subset=['result'])

# 3. Stats par équipe
def create_team_features(df, team_column, score_column):
    team_stats = {}
    for team in df[team_column].unique():
        team_data = df[df[team_column] == team]
        team_stats[team] = {
            'avg_goals': team_data[score_column].mean(),
            'total_matches': len(team_data),
            'wins': len(team_data[team_data['result'] == 0]) if 'result' in df.columns else 0,
        }
    return team_stats

home_stats = create_team_features(
    df_matches[df_matches['home_team_score'].notna()], 'home_team_name', 'home_team_score'
)
away_stats = create_team_features(
    df_matches[df_matches['away_team_score'].notna()], 'away_team_name', 'away_team_score'
)
print(f"✓ {len(home_stats)} équipes analysées")

# 4. Dataset features
df_model = df_matches[['home_team_name', 'away_team_name', 'home_team_score',
                        'away_team_score', 'year', 'count_teams']].copy()
df_model = df_model.dropna(subset=['home_team_score', 'away_team_score'])
df_model['home_team_score'] = df_model['home_team_score'].astype(int)
df_model['away_team_score'] = df_model['away_team_score'].astype(int)

conds = [
    (df_model['home_team_score'] > df_model['away_team_score']),
    (df_model['home_team_score'] == df_model['away_team_score']),
    (df_model['home_team_score'] < df_model['away_team_score']),
]
df_model['result'] = np.select(conds, [0, 1, 2])

def add_team_features_to_df(row, stats, prefix):
    team = row[f'{prefix}_team_name']
    s = stats.get(team, {'avg_goals': 0, 'total_matches': 0, 'wins': 0})
    return pd.Series({
        f'{prefix}_avg_goals': s['avg_goals'],
        f'{prefix}_total_matches': s['total_matches'],
        f'{prefix}_wins': s['wins'],
    })

home_feats = df_model.apply(lambda r: add_team_features_to_df(r, home_stats, 'home'), axis=1)
away_feats = df_model.apply(lambda r: add_team_features_to_df(r, away_stats, 'away'), axis=1)
df_model = pd.concat([df_model, home_feats, away_feats], axis=1)
df_model['goal_diff'] = df_model['home_avg_goals'] - df_model['away_avg_goals']
df_model['year'] = df_model['year'].fillna(df_model['year'].median()).astype(int)
df_model['count_teams'] = df_model['count_teams'].fillna(df_model['count_teams'].median()).astype(int)

median_year = float(df_model['year'].median())
median_count_teams = float(df_model['count_teams'].median())

# 5. Entraînement
features_cols = ['home_avg_goals', 'away_avg_goals', 'goal_diff',
                 'home_total_matches', 'away_total_matches',
                 'home_wins', 'away_wins', 'year', 'count_teams']
X = df_model[features_cols].fillna(0)
y = df_model['result']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
model.fit(X_train, y_train)

accuracy = accuracy_score(y_test, model.predict(X_test))
print(f"✓ Accuracy : {accuracy:.2%}")

# 6. Export du bundle
bundle = {
    "model": model,
    "home_stats": home_stats,
    "away_stats": away_stats,
    "median_year": median_year,
    "median_count_teams": median_count_teams,
}
output_path = Path(__file__).parents[1] / "backend" / "model.pkl"
joblib.dump(bundle, output_path)
print(f"✓ model.pkl exporté → {output_path}")

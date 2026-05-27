"""
Étape 2.2 — Itérer : Baseline → Comparaison → Tuning
Classification Multiclass (3 classes)
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
import warnings
warnings.filterwarnings('ignore')

print("\n" + "="*80)
print("ÉTAPE 2.2 — BASELINE → COMPARAISON → TUNING")
print("="*80)

# ============================================================================
# 1️⃣ CHARGEMENT ET PRÉPARATION DES DONNÉES
# ============================================================================

print("\n1️⃣ CHARGEMENT DES DONNÉES")
print("-" * 80)

url_matches = "https://raw.githubusercontent.com/quentinete2/Data_ai_Foot_Quentin_Thibaud/master/Ressources/Data/matches.csv"
url_tournaments = "https://raw.githubusercontent.com/quentinete2/Data_ai_Foot_Quentin_Thibaud/master/Ressources/Data/tournaments.csv"

df_matches = pd.read_csv(url_matches)
df_tournaments = pd.read_csv(url_tournaments)

df_matches = df_matches.merge(
    df_tournaments[['tournament_id', 'year', 'host_country', 'count_teams']],
    on='tournament_id',
    how='left'
)

# Créer cible
conditions = [
    (df_matches['home_team_win'] == 1),
    (df_matches['draw'] == 1),
    (df_matches['away_team_win'] == 1)
]
df_matches['result'] = np.select(conditions, [0, 1, 2], default=np.nan)
df_matches = df_matches.dropna(subset=['result'])

print(f"✓ {len(df_matches)} matchs chargés")

# ============================================================================
# 2️⃣ FEATURE ENGINEERING
# ============================================================================

print("\n2️⃣ FEATURE ENGINEERING")
print("-" * 80)

df_model = df_matches[['home_team_name', 'away_team_name', 'home_team_score',
                        'away_team_score', 'year', 'count_teams', 'result']].copy()
df_model = df_model.dropna(subset=['home_team_score', 'away_team_score'])
df_model['home_team_score'] = df_model['home_team_score'].astype(int)
df_model['away_team_score'] = df_model['away_team_score'].astype(int)

# Stats par équipe
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

home_stats = create_team_features(df_model, 'home_team_name', 'home_team_score')
away_stats = create_team_features(df_model, 'away_team_name', 'away_team_score')

def add_team_features_to_df(row, home_stats, away_stats, team_type='home'):
    team_col = 'home_team_name' if team_type == 'home' else 'away_team_name'
    team = row[team_col]
    stats = home_stats if team_type == 'home' else away_stats
    
    if team in stats:
        return pd.Series({
            f'{team_type}_avg_goals': stats[team]['avg_goals'],
            f'{team_type}_total_matches': stats[team]['total_matches'],
            f'{team_type}_wins': stats[team]['wins']
        })
    return pd.Series({
        f'{team_type}_avg_goals': 0,
        f'{team_type}_total_matches': 0,
        f'{team_type}_wins': 0
    })

home_features = df_model.apply(lambda row: add_team_features_to_df(row, home_stats, away_stats, 'home'), axis=1)
away_features = df_model.apply(lambda row: add_team_features_to_df(row, home_stats, away_stats, 'away'), axis=1)

df_model = pd.concat([df_model, home_features, away_features], axis=1)
df_model['goal_diff'] = df_model['home_avg_goals'] - df_model['away_avg_goals']

features_list = ['home_avg_goals', 'away_avg_goals', 'goal_diff', 'home_total_matches',
                 'away_total_matches', 'home_wins', 'away_wins', 'year', 'count_teams']

X = df_model[features_list].fillna(0)
y = df_model['result'].astype(int)

print(f"✓ {len(features_list)} features créées")
print(f"  Features : {', '.join(features_list[:3])}... ({len(features_list)} total)")

# ============================================================================
# 3️⃣ TRAIN/TEST SPLIT — ⚠️ FAIT UNE SEULE FOIS (pas de data leakage)
# ============================================================================

print("\n3️⃣ TRAIN/TEST SPLIT (80/20)")
print("-" * 80)

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y  # ← Important pour déséquilibre des classes
)

print(f"✓ Train : {len(X_train)} samples")
print(f"✓ Test  : {len(X_test)} samples")
print(f"✓ Stratification : {y_train.value_counts().to_dict()}")

# ============================================================================
# 4️⃣ BASELINE — LogisticRegression
# ============================================================================

print("\n4️⃣ BASELINE — LogisticRegression (simple, interpretable)")
print("-" * 80)

# Pipeline pour éviter data leakage
baseline_pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LogisticRegression(
        max_iter=1000,
        class_weight='balanced',  # ← Important pour déséquilibre
        random_state=42
    ))
])

# Cross-validation (CV) sur le train set
cv_scores_baseline = cross_val_score(
    baseline_pipe,
    X_train, y_train,
    cv=5,
    scoring='accuracy'
)

print(f"\n✓ LogisticRegression (5-fold CV)")
print(f"  Accuracy : {cv_scores_baseline.mean():.4f} ± {cv_scores_baseline.std():.4f}")
print(f"  Scores : {[f'{s:.4f}' for s in cv_scores_baseline]}")

# Entraîner une fois pour obtenir le modèle final
baseline_pipe.fit(X_train, y_train)
y_pred_baseline = baseline_pipe.predict(X_test)
acc_baseline = accuracy_score(y_test, y_pred_baseline)
f1_baseline = f1_score(y_test, y_pred_baseline, average='macro')

print(f"\n✓ Score TEST (évaluation finale) :")
print(f"  Accuracy : {acc_baseline:.4f}")
print(f"  F1-score (macro) : {f1_baseline:.4f}")

# ============================================================================
# 5️⃣ COMPARAISON — 3 Modèles sur même split
# ============================================================================

print("\n" + "="*80)
print("5️⃣ COMPARAISON — 3 Modèles")
print("="*80)

modeles = {
    "LogisticRegression": Pipeline([
        ('scaler', StandardScaler()),
        ('model', LogisticRegression(
            max_iter=1000,
            class_weight='balanced',
            random_state=42
        ))
    ]),
    
    "RandomForest": Pipeline([
        ('scaler', StandardScaler()),  # RF insensible mais inclus pour cohérence
        ('model', RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        ))
    ]),
    
    "GradientBoosting": Pipeline([
        ('scaler', StandardScaler()),
        ('model', GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        ))
    ])
}

print("\n📊 Cross-Validation (5-fold) sur TRAIN set :")
print("-" * 80)

results = {}
for nom, pipe in modeles.items():
    # CV Accuracy
    cv_acc = cross_val_score(pipe, X_train, y_train, cv=5, scoring='accuracy')
    
    # CV F1-score (macro)
    cv_f1 = cross_val_score(pipe, X_train, y_train, cv=5, scoring='f1_macro')
    
    # Entraîner une fois et évaluer sur TEST
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    test_acc = accuracy_score(y_test, y_pred)
    test_f1 = f1_score(y_test, y_pred, average='macro')
    
    results[nom] = {
        'cv_acc_mean': cv_acc.mean(),
        'cv_acc_std': cv_acc.std(),
        'cv_f1_mean': cv_f1.mean(),
        'cv_f1_std': cv_f1.std(),
        'test_acc': test_acc,
        'test_f1': test_f1,
        'model': pipe
    }
    
    print(f"\n{nom}:")
    print(f"  CV Accuracy      : {cv_acc.mean():.4f} ± {cv_acc.std():.4f}")
    print(f"  CV F1-score      : {cv_f1.mean():.4f} ± {cv_f1.std():.4f}")
    print(f"  Test Accuracy    : {test_acc:.4f}")
    print(f"  Test F1-score    : {test_f1:.4f}")

# ============================================================================
# 6️⃣ SÉLECTION DU MEILLEUR MODÈLE
# ============================================================================

print("\n" + "="*80)
print("6️⃣ SÉLECTION DU MEILLEUR MODÈLE")
print("="*80)

best_model_name = max(results, key=lambda x: results[x]['cv_acc_mean'])
best_result = results[best_model_name]

print(f"\n✓ Meilleur modèle (CV Accuracy) : {best_model_name}")
print(f"  CV Accuracy : {best_result['cv_acc_mean']:.4f}")
print(f"  Test Accuracy : {best_result['test_acc']:.4f}")

# ============================================================================
# 7️⃣ TUNING — GridSearchCV sur le meilleur modèle
# ============================================================================

print("\n" + "="*80)
print("7️⃣ TUNING — GridSearchCV")
print("="*80)

if best_model_name == "RandomForest":
    print("\n🔧 Tuning RandomForestClassifier...")
    
    param_grid = {
        'model__n_estimators': [50, 100, 150],
        'model__max_depth': [8, 10, 12, 15],
        'model__min_samples_split': [2, 5, 10],
    }
    
    base_pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('model', RandomForestClassifier(
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        ))
    ])
    
    grid_search = GridSearchCV(
        base_pipe,
        param_grid,
        cv=5,
        scoring='f1_macro',  # ← F1-score (macro) pour déséquilibre
        n_jobs=-1,
        verbose=1
    )
    
    print("\n  Tuning en cours (cela peut prendre quelques minutes)...")
    grid_search.fit(X_train, y_train)
    
    print(f"\n✓ Tuning complété")
    print(f"  Meilleurs hyperparamètres : {grid_search.best_params_}")
    print(f"  Meilleur CV F1-score : {grid_search.best_score_:.4f}")
    
    best_tuned_model = grid_search.best_estimator_
    
elif best_model_name == "GradientBoosting":
    print("\n🔧 Tuning GradientBoostingClassifier...")
    
    param_grid = {
        'model__n_estimators': [50, 100, 150],
        'model__max_depth': [3, 5, 7],
        'model__learning_rate': [0.01, 0.1, 0.2],
    }
    
    base_pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('model', GradientBoostingClassifier(random_state=42))
    ])
    
    grid_search = GridSearchCV(
        base_pipe,
        param_grid,
        cv=5,
        scoring='f1_macro',
        n_jobs=-1,
        verbose=1
    )
    
    print("\n  Tuning en cours (cela peut prendre quelques minutes)...")
    grid_search.fit(X_train, y_train)
    
    print(f"\n✓ Tuning complété")
    print(f"  Meilleurs hyperparamètres : {grid_search.best_params_}")
    print(f"  Meilleur CV F1-score : {grid_search.best_score_:.4f}")
    
    best_tuned_model = grid_search.best_estimator_

else:
    print(f"\n⚠️ Pas de tuning requis pour {best_model_name}")
    best_tuned_model = best_result['model']

# ============================================================================
# 8️⃣ ÉVALUATION FINALE SUR TEST SET — UNE SEULE FOIS
# ============================================================================

print("\n" + "="*80)
print("8️⃣ ÉVALUATION FINALE SUR TEST SET")
print("="*80)

y_pred_final = best_tuned_model.predict(X_test)

print(f"\n✓ Modèle final : {best_model_name} (après tuning)")
print(f"\n📊 RÉSULTATS FINALS :")
print(f"\n  Accuracy : {accuracy_score(y_test, y_pred_final):.4f}")
print(f"  F1-score (macro) : {f1_score(y_test, y_pred_final, average='macro'):.4f}")

print(f"\n📋 Confusion Matrix :")
cm = confusion_matrix(y_test, y_pred_final)
print(cm)

print(f"\n📈 Classification Report :")
print(classification_report(y_test, y_pred_final, 
                          target_names=['Home Win', 'Draw', 'Away Win']))

# ============================================================================
# 9️⃣ RÉSUMÉ COMPARATIF
# ============================================================================

print("\n" + "="*80)
print("9️⃣ RÉSUMÉ COMPARATIF")
print("="*80)

print("\n📊 Tableau Récapitulatif :")
print("\nModèle                  | CV Accuracy | CV F1       | Test Acc | Test F1")
print("-" * 75)

for nom, res in results.items():
    marker = "✓" if nom == best_model_name else " "
    print(f"{marker} {nom:20s} | {res['cv_acc_mean']:.4f}±{res['cv_acc_std']:.3f}  | "
          f"{res['cv_f1_mean']:.4f}±{res['cv_f1_std']:.3f}  | "
          f"{res['test_acc']:.4f}   | {res['test_f1']:.4f}")

print("\n✓ Baseline (LogisticRegression) :")
print(f"    Accuracy : {acc_baseline:.4f}")
print(f"    F1-score : {f1_baseline:.4f}")

print(f"\n✓ Meilleur modèle ({best_model_name}) :")
print(f"    Accuracy : {accuracy_score(y_test, y_pred_final):.4f}")
print(f"    F1-score : {f1_score(y_test, y_pred_final, average='macro'):.4f}")

improvement_acc = (accuracy_score(y_test, y_pred_final) - acc_baseline) * 100
improvement_f1 = (f1_score(y_test, y_pred_final, average='macro') - f1_baseline) * 100

print(f"\n📈 Amélioration vs Baseline :")
print(f"    Accuracy : {improvement_acc:+.2f}%")
print(f"    F1-score : {improvement_f1:+.2f}%")

print("\n" + "="*80)
print("✅ ÉTAPE 2.2 COMPLÉTÉE")
print("="*80 + "\n")

# ============================================================================
# 🔟 EXPORT MODÈLE (optionnel)
# ============================================================================

print("\n🔟 EXPORT MODÈLE")
print("-" * 80)

import joblib
joblib.dump(best_tuned_model, 'model_final.pkl')
print("✓ Modèle exporté : model_final.pkl")
print("\nPour charger : model = joblib.load('model_final.pkl')")

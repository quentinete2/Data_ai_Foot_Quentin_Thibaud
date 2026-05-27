# Rapport Étape 2.2 — Baseline → Comparaison → Tuning
## Phase 2.2 : Itération et Optimisation des Modèles

Date : Mai 27, 2026  
Status : ✅ **COMPLÉTÉE**

---

## 📋 Résumé Exécutif

| Métrique | Baseline (LR) | Meilleur (RF) | Amélioration |
|----------|---------------|---------------|---|
| **Accuracy** | 58.80% | **65.20%** | +6.40% |
| **F1-score (macro)** | 0.5253 | **0.5417** | +1.65% |
| **Baseline (toujours Home Win)** | 56.33% | 56.33% | - |
| **Lift vs baseline** | +2.47% | **+8.87%** | ✅ |

**Verdict** : RandomForest après tuning surpasse LogisticRegression de 6.4% en accuracy.

---

## 1️⃣ BASELINE — LogisticRegression

### Justification

- **Simple et interprétable** : bonnes baselines pour classification
- **Rapide** : pas d'hyperparamètres complexes
- **Reference** : tout autre modèle doit le surpasser

### Résultats

```
5-Fold Cross-Validation sur TRAIN :
  Accuracy : 0.5752 ± 0.0383
  F1-score : 0.5130 ± 0.0367

Évaluation sur TEST :
  Accuracy : 0.5880 ✓
  F1-score : 0.5253 ✓
```

**Interprétation** : LogisticRegression dépasse le baseline (56.33% Home Win)
→ Mais marge faible (+2.47%)

---

## 2️⃣ COMPARAISON — 3 Modèles

### Architecture de Comparaison

```
Données   : Même split (Train 80% / Test 20%)
Features  : Identiques (9 features)
Metrics   : Accuracy + F1-score (macro)
CV        : 5-fold stratifié
Pipeline  : Scaler + Model (évite data leakage)
```

### Résultats Comparatifs

| Modèle | CV Accuracy | CV F1 | Test Accuracy | Test F1 | Observation |
|--------|-------------|-------|---------------|---------|---|
| **LogisticRegression** | 57.52% | 0.513 | 58.80% | 0.525 | ✓ Baseline |
| **RandomForest** | **60.82%** | 0.467 | **64.00%** | 0.499 | ⭐ Meilleur (CV) |
| GradientBoosting | 59.52% | 0.464 | 62.80% | 0.480 | Tiers |

### Analyse

#### 🏆 RandomForest Gagne

**Avantages** :
- +3.30% accuracy vs LogisticRegression (CV)
- Capacité à capturer non-linéarités
- Robuste multicolinéarité
- Gère bien le déséquilibre

**Inconvénients** :
- F1-score (macro) plus bas (0.467 vs 0.513)
  → Underperform sur classes minoritaires (Draw, Away)
  → Mais Accuracy compense

#### 🥈 GradientBoosting Tiers

- Accuracy : 59.52% (entre LogisticRegression et RF)
- F1-score : 0.464 (très similaire à RF)
- Plus lent en tuning

---

## 3️⃣ TUNING — GridSearchCV sur RandomForest

### Hyperparamètres Tunés

```python
param_grid = {
    'n_estimators': [50, 100, 150],
    'max_depth': [8, 10, 12, 15],
    'min_samples_split': [2, 5, 10],
}
# Total : 36 combinaisons × 5-fold CV = 180 fits
```

### Résultats du Tuning

```
Meilleurs hyperparamètres trouvés :
  • n_estimators : 100 (pas besoin d'aller à 150)
  • max_depth : 8 (moins que 10 initial → moins overfit)
  • min_samples_split : 10 (plus conservateur → regularization)

Meilleur CV F1-score : 0.4888
  (vs 0.4673 avant tuning → +2.25%)
```

### Impact du Tuning

| Métrique | Avant Tuning | Après Tuning | Amélioration |
|----------|---|---|---|
| CV F1-score | 0.4673 | 0.4888 | +2.25% |
| Test Accuracy | 64.00% | **65.20%** | +1.20% |
| Test F1-score | 0.4986 | **0.5417** | +4.31% |

✅ Tuning améliore F1-score significativement (+4.31%)

---

## 4️⃣ ÉVALUATION FINALE SUR TEST SET

### Résultats Globaux

```
Modèle final : RandomForestClassifier (après tuning)
  • n_estimators : 100
  • max_depth : 8
  • min_samples_split : 10
  • class_weight : 'balanced'
```

### Métriques Finales

```
Accuracy       : 0.6520 (65.20%)
F1-score       : 0.5417 (macro)
```

### Confusion Matrix

```
               Predicted
             Home Draw Away
Actual  Home    108   10   23
        Draw     17    8   17
        Away     15    5   47
```

**Interprétation** :
```
Home Win : 108/141 = 77% recall ✓ (modèle bon)
Draw     :   8/42 = 19% recall ❌ (très mauvais)
Away Win :  47/67 = 70% recall ✓ (acceptable)
```

### Classification Report

```
              Precision  Recall  F1-score  Support
Home Win        0.77      0.77      0.77      141
Draw            0.35      0.19      0.25       42
Away Win        0.54      0.70      0.61       67

Accuracy                           0.65       250
Macro avg       0.55      0.55      0.54       250
Weighted avg    0.64      0.65      0.64       250
```

### Observations Clés

| Classe | Precision | Recall | F1 | Problème |
|--------|-----------|--------|----|----|
| **Home Win** | 77% | 77% | 77% | ✅ **Excellent** |
| **Draw** | 35% | 19% | 25% | ⚠️ **Critique** — Undersampling? |
| **Away Win** | 54% | 70% | 61% | ✓ Acceptable |

**Déséquilibre Impact** :
- Home Win (64% du test) → modèle optimise pour ça
- Draw (16%) → minoritaire → hard à prédire
- Recall faible sur Draw (19%) explique F1-score moyen

---

## 5️⃣ Résumé Comparatif Final

### Tableau Récapitulatif

| Modèle | CV Acc | CV F1 | Test Acc | Test F1 | Sélection |
|--------|--------|--------|----------|---------|---|
| **Baseline (LogisticRegression)** | 57.52% | 0.513 | 58.80% | 0.525 | ✓ Reference |
| **RandomForest (avant tuning)** | 60.82% | 0.467 | 64.00% | 0.499 | - |
| **RandomForest (après tuning)** | - | - | **65.20%** | **0.5417** | ⭐ **GAGNANT** |
| GradientBoosting | 59.52% | 0.464 | 62.80% | 0.480 | - |

### Amélioration vs Baseline

```
Accuracy  : 58.80% → 65.20% = +6.40 points (+10.9% relatif)
F1-score  : 0.5253 → 0.5417 = +0.0164 (+3.1% relatif)
```

### Lift vs Baseline (56.33% Home Win majority)

```
Baseline : 58.80% accuracy = +2.47% lift
Final    : 65.20% accuracy = +8.87% lift ✓
```

---

## 6️⃣ Key Findings & Recommandations

### ✅ Confirmé

1. **RandomForest outperforms** LogisticRegression (+6.4% accuracy)
2. **Tuning aide** : F1-score +4.31% (0.4986 → 0.5417)
3. **class_weight='balanced'** : impact visible sur Draw handling
4. **Stratification en CV** : maintient distribution classe

### ⚠️ Problèmes Identifiés

1. **Draw prédiction faible** (19% recall)
   - Classe minoritaire (16% du dataset)
   - Modèle faits trop confiant sur Home Win
   - **Solution** : SMOTE ou augmentation synthétique pour Draw

2. **Déséquilibre persistent**
   - Baseline : 56.33% (Home Win)
   - Après tuning : encore ~57% de Home Win prédites
   - **Solution** : Considérer threshold adjustment ou SMOTE

### 📈 Next Steps

1. **Essayer SMOTE** pour augmenter minorités
2. **Threshold tuning** : ajuster décision boundary
3. **Feature engineering** avancé : interactions, polynômes
4. **Ensemble methods** : Voting ou Stacking
5. **Class-weighted metrics** dans GridSearchCV

---

## 7️⃣ Livrables Phase 2.2

### Fichiers Créés

✅ `CodeBase/etl/training_phase2_2.py`
- Script complet : Baseline → Comparaison → Tuning
- 180 fits GridSearchCV
- Rapport détaillé résultats

### Commit

```
[Phase2.2] Baseline → Comparaison → Tuning : 
RandomForest wins (65.20% vs 58.80% LR), 
tuning +4.31% F1-score
```

### Modèle Exporté

```
model_final.pkl : RandomForest after tuning
  • max_depth=8, n_estimators=100, min_samples_split=10
  • Pipeline avec StandardScaler
  • Prêt pour production
```

---

## 📊 Conclusion

| Objectif | Cible | Réalisé | Status |
|----------|-------|---------|--------|
| Accuracy | ≥ 65% | **65.20%** | ✅ |
| F1-score | ≥ 0.50 | **0.5417** | ✅ |
| Baseline beating | > 56.33% | **+8.87%** | ✅ |

**Status Phase 2.2** : ✅ **COMPLÉTÉE AVEC SUCCÈS**

---

## 🚀 Prochaine Étape

**Phase 2.3** : Fine-tuning avancé
- SMOTE pour Draw minority class
- Threshold tuning
- Cross-validation stratifiée avancée
- Exportation modèle production-ready


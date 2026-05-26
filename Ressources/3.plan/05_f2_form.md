# F2 — Formulaire de prédiction (`PredictionForm.tsx`)

## Objectif

Remplacer le TODO par 8 champs `<input>` typés, initialisés avec des valeurs par défaut représentatives, et afficher le résultat avec `predicted_stage` + `stage_label`.

## Fichier cible

`CodeBase/frontend/src/PredictionForm.tsx`

## État initial du formulaire (valeurs par défaut)

```typescript
const INITIAL: Features = {
  nb_participations: 10,
  taux_victoire_historique: 0.5,
  buts_marques_moy: 1.2,
  buts_encaisses_moy: 1.0,
  diff_buts_moy: 0.2,
  meilleur_stade_atteint: 3,
  stade_dernier_tournoi: 2,
  est_hote: 0,
}
```

## Structure de chaque champ

Chaque feature a :
- un label lisible en français
- un `input type="number"` avec `step` adapté (0.01 pour les floats, 1 pour les entiers)
- une plage min/max cohérente avec les données réelles

```typescript
const FIELDS: Array<{
  key: keyof Features
  label: string
  step: string
  min: number
  max: number
}> = [
  { key: "nb_participations",        label: "Nombre de participations",       step: "1",    min: 1,  max: 24 },
  { key: "taux_victoire_historique", label: "Taux de victoire historique",    step: "0.01", min: 0,  max: 1  },
  { key: "buts_marques_moy",         label: "Buts marqués (moy/match)",       step: "0.01", min: 0,  max: 6  },
  { key: "buts_encaisses_moy",       label: "Buts encaissés (moy/match)",     step: "0.01", min: 0,  max: 6  },
  { key: "diff_buts_moy",            label: "Différentiel de buts (moy)",     step: "0.01", min: -4, max: 4  },
  { key: "meilleur_stade_atteint",   label: "Meilleur stade atteint (1–6)",   step: "1",    min: 1,  max: 6  },
  { key: "stade_dernier_tournoi",    label: "Stade dernier tournoi (1–6)",    step: "1",    min: 1,  max: 6  },
  { key: "est_hote",                 label: "Pays hôte (0 = non, 1 = oui)",  step: "1",    min: 0,  max: 1  },
]
```

## Rendu des inputs (à l'intérieur du formulaire)

```tsx
{FIELDS.map(({ key, label, step, min, max }) => (
  <div key={key} className="flex flex-col gap-1">
    <label className="text-sm font-medium" htmlFor={key}>{label}</label>
    <input
      id={key}
      type="number"
      step={step}
      min={min}
      max={max}
      value={valeurs[key]}
      onChange={(e) =>
        setValeurs((prev) => ({ ...prev, [key]: Number(e.target.value) }))
      }
      className="rounded border px-2 py-1 text-sm"
      required
    />
  </div>
))}
```

## Affichage du résultat

Remplacer l'affichage actuel (qui cherche `prediction`) par :

```tsx
{mutation.data && (
  <div className="rounded-lg bg-green-50 p-4">
    <p className="text-sm text-gray-600">Stade prédit</p>
    <p className="text-2xl font-bold">{mutation.data.stage_label}</p>
    <p className="text-sm text-gray-500">Score : {mutation.data.predicted_stage.toFixed(2)}</p>
  </div>
)}
```

## Validation

- Tous les champs ont `required` → le navigateur bloque la soumission si vide
- `npm run typecheck` → 0 erreur (après F1 qui définit le type `Features`)

## Dépendances

- F1 doit être terminé (type `Features` et `PredictResponse` dans `api.ts`)
- B2 doit fonctionner pour tester la soumission

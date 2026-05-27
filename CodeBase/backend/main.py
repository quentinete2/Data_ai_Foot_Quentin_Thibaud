"""API FastAPI -- Dashboard FIFA WC 2026."""
from pathlib import Path

import numpy as np
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

app = FastAPI(title="Dashboard B3 -- API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost",
        "https://*.hf.space",
    ],
    allow_origin_regex=r"https://.*\.hf\.space",
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chargement du bundle une seule fois au demarrage
REQUIRED_BUNDLE_KEYS = {"model", "home_stats", "away_stats", "median_year", "median_count_teams"}

bundle = None
try:
    bundle = joblib.load(Path(__file__).parent / "model.pkl")
    missing = REQUIRED_BUNDLE_KEYS - set(bundle.keys())
    if missing:
        raise KeyError(f"Clés manquantes dans model.pkl : {missing}")
except FileNotFoundError:
    pass
except Exception as exc:
    print(f"[WARN] bundle invalide : {exc}")
    bundle = None

RESULT_LABELS = {0: "home_win", 1: "draw", 2: "away_win"}
MODEL_METRICS = {"accuracy": 0.6520}
MIN_MATCHES = 5


# --- B1 : Modèle d'entrée ---

class MatchInput(BaseModel):
    home_team: str
    away_team: str

    @field_validator("home_team", "away_team", mode="before")
    @classmethod
    def strip_and_reject_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Le nom de l'équipe ne peut pas être vide")
        return v


# --- Helpers ---

def get_team_stats(stats_dict: dict, team: str) -> dict:
    return stats_dict.get(team, {"avg_goals": 0, "total_matches": 0, "wins": 0, "weighted_win_rate": 0, "last_wc_year": 0})


# --- Endpoints ---

@app.get("/api/health")
def health():
    return {"status": "ok", "model_loaded": bundle is not None}


# --- B2 : POST /api/predict ---

@app.post("/api/predict")
def predict(match: MatchInput):
    if bundle is None:
        raise HTTPException(status_code=503, detail="model.pkl manquant -- exportez-le depuis le notebook")

    model = bundle["model"]
    home_stats_dict = bundle["home_stats"]
    away_stats_dict = bundle["away_stats"]
    median_year = bundle["median_year"]
    median_count_teams = bundle["median_count_teams"]

    home_stat = get_team_stats(home_stats_dict, match.home_team)
    away_stat = get_team_stats(away_stats_dict, match.away_team)

    features = np.array([[
        home_stat["avg_goals"],
        away_stat["avg_goals"],
        home_stat["avg_goals"] - away_stat["avg_goals"],
        home_stat["total_matches"],
        away_stat["total_matches"],
        home_stat["weighted_win_rate"],
        away_stat["weighted_win_rate"],
        median_year,
        median_count_teams,
    ]])

    try:
        prediction_class = int(model.predict(features)[0])
        probabilities = model.predict_proba(features)[0]
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prédiction : {exc}",
        )

    label = (
        f"Victoire {match.home_team}" if prediction_class == 0
        else "Match Nul" if prediction_class == 1
        else f"Victoire {match.away_team}"
    )

    return {
        "prediction": label,
        "confidence": float(probabilities[prediction_class]),
        "probabilities": {
            "home_win": float(probabilities[0]),
            "draw": float(probabilities[1]),
            "away_win": float(probabilities[2]),
        },
        "home_stats": home_stat,
        "away_stats": away_stat,
    }


# --- B3 : GET /api/stats ---

def _normalize(values: list[float]) -> list[float]:
    min_v, max_v = min(values), max(values)
    if max_v == min_v:
        return [0.5] * len(values)
    return [(v - min_v) / (max_v - min_v) for v in values]


@app.get("/api/stats")
def stats():
    top_teams_wins: list = []
    top_teams_goals: list = []
    form_scores: list = []

    if bundle is not None:
        home_stats_dict = bundle["home_stats"]

        eligible = [
            (team, s) for team, s in home_stats_dict.items()
            if s["total_matches"] >= MIN_MATCHES
        ]

        for team, s in eligible:
            top_teams_wins.append({"label": team, "value": round(s["weighted_win_rate"] * 100, 2)})
            top_teams_goals.append({"label": team, "value": round(s["avg_goals"], 3)})

        top_teams_wins = sorted(top_teams_wins, key=lambda x: x["value"], reverse=True)[:10]
        top_teams_goals = sorted(top_teams_goals, key=lambda x: x["value"], reverse=True)[:10]

        if eligible:
            win_rates = [s["weighted_win_rate"] for _, s in eligible]
            avg_goals_list = [s["avg_goals"] for _, s in eligible]
            matches_list = [s["total_matches"] for _, s in eligible]

            win_norm = _normalize(win_rates)
            goals_norm = _normalize(avg_goals_list)
            exp_norm = _normalize(matches_list)

            for i, (team, _) in enumerate(eligible):
                score = (0.5 * win_norm[i] + 0.3 * goals_norm[i] + 0.2 * exp_norm[i]) * 100
                form_scores.append({"label": team, "value": round(score, 1)})

            form_scores = sorted(form_scores, key=lambda x: x["value"], reverse=True)[:15]

    return {
        "top_teams_wins": top_teams_wins,
        "top_teams_goals": top_teams_goals,
        "form_scores": form_scores,
        "metrics": MODEL_METRICS,
    }


# --- Prod : servir le build React (decommenter apres docker-compose) ---
# from fastapi.staticfiles import StaticFiles
# DIST = Path(__file__).parents[1] / "frontend" / "dist"
# if DIST.exists():
#     app.mount("/", StaticFiles(directory=DIST, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=7860, reload=False)

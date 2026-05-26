"""API FastAPI -- squelette du dashboard B3 (a completer avec Claude Code)."""
from pathlib import Path

import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Dashboard B3 -- API")

# CORS : autorise le front Vite (dev, port 5173) a appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chargement du modele J2 une seule fois au demarrage (pas a chaque requete)
MODEL_PATH = Path(__file__).parent / "model.pkl"
model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None


class Features(BaseModel):
    # TODO (Claude Code) : 1 champ par feature de VOTRE modele J2.
    # Exemple : surface: float ; pieces: int ; arrondissement: str
    pass


@app.get("/api/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/api/predict")
def predict(features: Features):
    if model is None:
        return {"error": "model.pkl manquant -- exportez-le depuis le notebook J2"}
    # TODO : construire l'entree dans le MEME ordre qu'a l'entrainement, puis :
    # x = [[features.surface, features.pieces, ...]]
    # pred = model.predict(x)[0]
    # return {"prediction": float(pred)}
    return {"prediction": None, "todo": "completer predict()"}


@app.get("/api/stats")
def stats():
    # TODO : renvoyer des agregats du dataset (ex : moyenne de la cible par categorie)
    # sous forme de liste d'objets JSON, ex : [{"cat": "75011", "valeur": 9500}, ...]
    return {"todo": "completer /api/stats"}


# --- PROD (J4) : decommenter pour servir le build React (dist/) en un seul process ---
# from fastapi.staticfiles import StaticFiles
# DIST = Path(__file__).parents[1] / "frontend" / "dist"
# if DIST.exists():
#     app.mount("/", StaticFiles(directory=DIST, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

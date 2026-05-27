"""Fixtures partagées pour les tests de l'API."""
import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from starlette.testclient import TestClient


@pytest.fixture()
def mock_bundle():
    """Bundle minimal qui mime la structure de model.pkl."""
    model = MagicMock()
    model.predict.return_value = np.array([0])
    model.predict_proba.return_value = np.array([[0.60, 0.25, 0.15]])

    home_stats = {
        "France":  {"avg_goals": 2.1, "total_matches": 80, "wins": 55},
        "Brazil":  {"avg_goals": 2.3, "total_matches": 90, "wins": 60},
        "Germany": {"avg_goals": 1.9, "total_matches": 75, "wins": 45},
    }
    away_stats = {
        "France":  {"avg_goals": 1.8, "total_matches": 80, "wins": 40},
        "Brazil":  {"avg_goals": 2.0, "total_matches": 90, "wins": 50},
        "Germany": {"avg_goals": 1.7, "total_matches": 75, "wins": 35},
    }

    return {
        "model": model,
        "home_stats": home_stats,
        "away_stats": away_stats,
        "median_year": 2010.0,
        "median_count_teams": 32.0,
    }


@pytest.fixture()
def client(mock_bundle):
    """TestClient avec le bundle mocké injecté dans main.bundle."""
    import main

    with patch.object(main, "bundle", mock_bundle):
        with TestClient(main.app) as c:
            yield c


@pytest.fixture()
def client_no_bundle():
    """TestClient sans bundle (simule modèle manquant)."""
    import main

    with patch.object(main, "bundle", None):
        with TestClient(main.app) as c:
            yield c

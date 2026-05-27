"""Tests unitaires pour les endpoints FastAPI."""
import pytest
from main import get_team_stats


# ─── /api/health ──────────────────────────────────────────────────────────────

class TestHealth:
    def test_health_returns_ok(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200

    def test_health_model_loaded_true(self, client):
        data = client.get("/api/health").json()
        assert data["status"] == "ok"
        assert data["model_loaded"] is True

    def test_health_model_loaded_false_when_no_bundle(self, client_no_bundle):
        data = client_no_bundle.get("/api/health").json()
        assert data["model_loaded"] is False


# ─── /api/predict — happy paths ───────────────────────────────────────────────

class TestPredictHappyPath:
    def test_predict_known_teams_status_200(self, client):
        r = client.post("/api/predict", json={"home_team": "France", "away_team": "Brazil"})
        assert r.status_code == 200

    def test_predict_response_has_required_keys(self, client):
        data = client.post(
            "/api/predict", json={"home_team": "France", "away_team": "Brazil"}
        ).json()
        assert set(data.keys()) == {"prediction", "confidence", "probabilities", "home_stats", "away_stats"}

    def test_predict_probabilities_sum_to_one(self, client):
        probs = client.post(
            "/api/predict", json={"home_team": "France", "away_team": "Brazil"}
        ).json()["probabilities"]
        total = probs["home_win"] + probs["draw"] + probs["away_win"]
        assert abs(total - 1.0) < 1e-6

    def test_predict_confidence_in_range(self, client):
        data = client.post(
            "/api/predict", json={"home_team": "France", "away_team": "Brazil"}
        ).json()
        assert 0.0 <= data["confidence"] <= 1.0

    def test_predict_same_team_home_and_away(self, client):
        """Même équipe des deux côtés : 200 sans erreur."""
        r = client.post("/api/predict", json={"home_team": "France", "away_team": "France"})
        assert r.status_code == 200

    def test_predict_calls_model_predict(self, client, mock_bundle):
        client.post("/api/predict", json={"home_team": "France", "away_team": "Brazil"})
        mock_bundle["model"].predict.assert_called_once()

    def test_predict_calls_model_predict_proba(self, client, mock_bundle):
        client.post("/api/predict", json={"home_team": "France", "away_team": "Brazil"})
        mock_bundle["model"].predict_proba.assert_called_once()


# ─── /api/predict — unknown teams ─────────────────────────────────────────────

class TestPredictUnknownTeams:
    def test_unknown_teams_returns_200(self, client):
        r = client.post("/api/predict", json={"home_team": "Narnia", "away_team": "Wakanda"})
        assert r.status_code == 200

    def test_unknown_home_team_stats_are_zero(self, client):
        data = client.post(
            "/api/predict", json={"home_team": "Narnia", "away_team": "Brazil"}
        ).json()
        assert data["home_stats"]["avg_goals"] == 0
        assert data["home_stats"]["total_matches"] == 0
        assert data["home_stats"]["wins"] == 0

    def test_unknown_away_team_stats_are_zero(self, client):
        data = client.post(
            "/api/predict", json={"home_team": "France", "away_team": "Wakanda"}
        ).json()
        assert data["away_stats"]["avg_goals"] == 0


# ─── /api/predict — validation 422 ────────────────────────────────────────────

class TestPredictValidation:
    def test_empty_home_team_returns_422(self, client):
        r = client.post("/api/predict", json={"home_team": "", "away_team": "Brazil"})
        assert r.status_code == 422

    def test_whitespace_only_home_team_returns_422(self, client):
        r = client.post("/api/predict", json={"home_team": "   ", "away_team": "Brazil"})
        assert r.status_code == 422

    def test_empty_away_team_returns_422(self, client):
        r = client.post("/api/predict", json={"home_team": "France", "away_team": ""})
        assert r.status_code == 422

    def test_whitespace_tab_away_team_returns_422(self, client):
        r = client.post("/api/predict", json={"home_team": "France", "away_team": "  \t  "})
        assert r.status_code == 422

    def test_missing_home_team_field_returns_422(self, client):
        r = client.post("/api/predict", json={"away_team": "Brazil"})
        assert r.status_code == 422

    def test_valid_names_with_surrounding_spaces_returns_200(self, client):
        """Noms valides entourés d'espaces → 200 après strip."""
        r = client.post("/api/predict", json={"home_team": " France ", "away_team": " Brazil "})
        assert r.status_code == 200


# ─── /api/predict — bundle manquant 503 ───────────────────────────────────────

class TestPredictMissingBundle:
    def test_predict_without_bundle_returns_503(self, client_no_bundle):
        r = client_no_bundle.post(
            "/api/predict", json={"home_team": "France", "away_team": "Brazil"}
        )
        assert r.status_code == 503

    def test_predict_503_has_detail_key(self, client_no_bundle):
        data = client_no_bundle.post(
            "/api/predict", json={"home_team": "France", "away_team": "Brazil"}
        ).json()
        assert "detail" in data


# ─── /api/predict — erreur modèle 500 ─────────────────────────────────────────

class TestPredictModelError:
    def test_predict_model_runtime_error_returns_500(self, client, mock_bundle):
        mock_bundle["model"].predict.side_effect = RuntimeError("sklearn broke")
        r = client.post("/api/predict", json={"home_team": "France", "away_team": "Brazil"})
        assert r.status_code == 500

    def test_predict_500_has_detail_key(self, client, mock_bundle):
        mock_bundle["model"].predict.side_effect = ValueError("feature mismatch")
        data = client.post(
            "/api/predict", json={"home_team": "France", "away_team": "Brazil"}
        ).json()
        assert "detail" in data


# ─── /api/stats ───────────────────────────────────────────────────────────────

class TestStats:
    def test_stats_status_200(self, client):
        assert client.get("/api/stats").status_code == 200

    def test_stats_has_required_keys(self, client):
        data = client.get("/api/stats").json()
        assert "top_teams_wins" in data
        assert "top_teams_goals" in data
        assert "form_scores" in data
        assert "metrics" in data

    def test_stats_metrics_has_accuracy_float(self, client):
        metrics = client.get("/api/stats").json()["metrics"]
        assert "accuracy" in metrics
        assert isinstance(metrics["accuracy"], float)

    def test_stats_top_teams_wins_max_10(self, client):
        assert len(client.get("/api/stats").json()["top_teams_wins"]) <= 10

    def test_stats_top_teams_goals_max_10(self, client):
        assert len(client.get("/api/stats").json()["top_teams_goals"]) <= 10

    def test_stats_without_bundle_returns_empty_lists(self, client_no_bundle):
        data = client_no_bundle.get("/api/stats").json()
        assert data["top_teams_wins"] == []
        assert data["top_teams_goals"] == []
        assert data["form_scores"] == []

    def test_stats_items_have_label_and_value(self, client):
        items = client.get("/api/stats").json()["top_teams_wins"]
        if items:
            assert "label" in items[0]
            assert "value" in items[0]

    def test_stats_wins_sorted_descending(self, client):
        items = client.get("/api/stats").json()["top_teams_wins"]
        values = [i["value"] for i in items]
        assert values == sorted(values, reverse=True)

    def test_stats_form_scores_max_15(self, client):
        assert len(client.get("/api/stats").json()["form_scores"]) <= 15

    def test_stats_form_scores_sorted_descending(self, client):
        items = client.get("/api/stats").json()["form_scores"]
        values = [i["value"] for i in items]
        assert values == sorted(values, reverse=True)

    def test_stats_form_scores_items_have_label_and_value(self, client):
        items = client.get("/api/stats").json()["form_scores"]
        if items:
            assert "label" in items[0]
            assert "value" in items[0]


# ─── get_team_stats helper ────────────────────────────────────────────────────

class TestGetTeamStats:
    def test_known_team_returns_correct_stats(self):
        stats = {"France": {"avg_goals": 2.1, "total_matches": 80, "wins": 55, "weighted_win_rate": 0.65, "last_wc_year": 2022}}
        result = get_team_stats(stats, "France")
        assert result["avg_goals"] == 2.1
        assert result["total_matches"] == 80
        assert result["wins"] == 55
        assert result["weighted_win_rate"] == 0.65

    def test_unknown_team_returns_zeros(self):
        result = get_team_stats({}, "Narnia")
        assert result["avg_goals"] == 0
        assert result["total_matches"] == 0
        assert result["wins"] == 0
        assert result["weighted_win_rate"] == 0
        assert result["last_wc_year"] == 0

    def test_empty_stats_dict_returns_zeros(self):
        result = get_team_stats({}, "France")
        assert result["avg_goals"] == 0

    def test_lookup_is_case_sensitive(self):
        """Le lookup est sensible à la casse — 'france' ≠ 'France'."""
        stats = {"France": {"avg_goals": 2.1, "total_matches": 80, "wins": 55}}
        result = get_team_stats(stats, "france")
        assert result["avg_goals"] == 0

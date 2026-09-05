from app.services.incident.scoring import (
    ScoreComponents,
    TOTAL_WEIGHT,
    communication_component,
    incident_evidence_score,
    normalize_dormancy,
    normalize_historical_novelty,
    normalize_robust_z,
    normalize_velocity,
)


def test_weights_sum_to_100():
    assert TOTAL_WEIGHT == 100


def test_score_is_zero_for_all_zero_components():
    components = ScoreComponents(0, 0, 0, 0, 0, 0)
    assert incident_evidence_score(components) == 0.0


def test_score_is_100_for_all_maxed_components():
    components = ScoreComponents(1, 1, 1, 1, 1, 1)
    assert incident_evidence_score(components) == 100.0


def test_score_never_exceeds_100():
    components = ScoreComponents(1, 1, 1, 1, 1, 1)
    assert incident_evidence_score(components) <= 100.0


def test_normalize_robust_z_negative_is_zero():
    assert normalize_robust_z(-5.0) == 0.0


def test_normalize_robust_z_saturates():
    assert normalize_robust_z(1000.0, saturate_at=40.0) == 1.0


def test_normalize_historical_novelty_new_beneficiary_is_max():
    assert normalize_historical_novelty(0) == 1.0


def test_normalize_historical_novelty_decreases_with_history():
    assert normalize_historical_novelty(5) < normalize_historical_novelty(1)


def test_normalize_dormancy_zero_for_fresh_activity():
    assert normalize_dormancy(0) == 0.0


def test_communication_component_mapping():
    assert communication_component("CORROBORATED") == 1.0
    assert communication_component("POSSIBLE") == 0.5
    assert communication_component("UNCORRELATED") == 0.0


def test_flagship_style_incident_scores_high():
    """Reproduces the flagship scenario's component shape directly (not via
    the DB) and checks the resulting score would clearly warrant escalation."""
    components = ScoreComponents(
        new_beneficiary=1.0,
        amount_anomaly=normalize_robust_z(1500),
        velocity_anomaly=normalize_velocity(3, 3_00_00_000, 18400),
        historical_novelty=normalize_historical_novelty(0),
        dormant_entity=0.0,
        communication_correlation=communication_component("CORROBORATED"),
    )
    score = incident_evidence_score(components)
    assert score >= 80.0

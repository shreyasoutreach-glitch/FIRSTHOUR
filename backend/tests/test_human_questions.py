from app.services.human.questions import candidate_questions_for_incident, next_question


def test_authorization_question_outranks_others_when_high_amount():
    candidates = candidate_questions_for_incident(
        has_new_beneficiary=True, has_communication_evidence=True,
        is_high_amount=True, has_dormant_reactivation=True,
    )
    assert candidates[0].question_id == "q_authorized_payouts"


def test_only_relevant_questions_are_generated():
    candidates = candidate_questions_for_incident(
        has_new_beneficiary=False, has_communication_evidence=False,
        is_high_amount=False, has_dormant_reactivation=False,
    )
    ids = {c.question_id for c in candidates}
    assert "q_authorized_payouts" not in ids
    assert "q_recognize_beneficiary" not in ids
    assert "q_device_control" in ids  # always relevant


def test_next_question_skips_answered():
    candidates = candidate_questions_for_incident(
        has_new_beneficiary=True, has_communication_evidence=True,
        is_high_amount=True, has_dormant_reactivation=False,
    )
    top = candidates[0]
    remaining = next_question(candidates, already_answered_ids={top.question_id})
    assert remaining is not None
    assert remaining.question_id != top.question_id


def test_next_question_none_when_all_answered():
    candidates = candidate_questions_for_incident(
        has_new_beneficiary=False, has_communication_evidence=False,
        is_high_amount=False, has_dormant_reactivation=False,
    )
    all_ids = {c.question_id for c in candidates}
    assert next_question(candidates, already_answered_ids=all_ids) is None

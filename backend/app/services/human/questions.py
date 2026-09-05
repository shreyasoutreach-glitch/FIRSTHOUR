"""
Human question prioritization. Generates unresolved predicates from the
evidence gaps a given incident actually has, scores each candidate by
impact_on_case x uncertainty x actionability, and always surfaces exactly
one question at a time -- the highest-value one first -- rather than a
ten-item form. Answering never rewrites a financial fact; it is stored as
its own attestation row (see models.HumanAttestation).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CandidateQuestion:
    question_id: str
    question_text: str
    affected_predicate: str
    impact_on_case: float  # 0..1 -- how much this changes the case if answered
    uncertainty: float  # 0..1 -- how unresolved this currently is
    actionability: float  # 0..1 -- how directly the answer changes next steps

    @property
    def priority(self) -> float:
        return round(self.impact_on_case * self.uncertainty * self.actionability, 4)


def candidate_questions_for_incident(*, has_new_beneficiary: bool, has_communication_evidence: bool,
                                      is_high_amount: bool, has_dormant_reactivation: bool) -> list[CandidateQuestion]:
    candidates: list[CandidateQuestion] = []

    if is_high_amount:
        candidates.append(CandidateQuestion(
            question_id="q_authorized_payouts",
            question_text="Did you personally authorize these payouts?",
            affected_predicate="authorization_status",
            impact_on_case=1.0, uncertainty=1.0, actionability=1.0,
        ))

    if has_new_beneficiary:
        candidates.append(CandidateQuestion(
            question_id="q_recognize_beneficiary",
            question_text="Do you recognize this beneficiary from your own records?",
            affected_predicate="beneficiary_familiarity",
            impact_on_case=0.8, uncertainty=0.9, actionability=0.7,
        ))

    if has_communication_evidence:
        candidates.append(CandidateQuestion(
            question_id="q_sent_instruction",
            question_text="Did you or your team send the instruction in this message?",
            affected_predicate="instruction_origin",
            impact_on_case=0.75, uncertainty=0.85, actionability=0.6,
        ))

    candidates.append(CandidateQuestion(
        question_id="q_device_control",
        question_text="Do you still have control of the device or account that sent this?",
        affected_predicate="device_control",
        impact_on_case=0.6, uncertainty=0.7, actionability=0.65,
    ))

    if has_dormant_reactivation:
        candidates.append(CandidateQuestion(
            question_id="q_dormant_relationship",
            question_text="Has this vendor been inactive for a reason you're aware of?",
            affected_predicate="dormancy_explanation",
            impact_on_case=0.4, uncertainty=0.5, actionability=0.3,
        ))

    return sorted(candidates, key=lambda q: q.priority, reverse=True)


def next_question(candidates: list[CandidateQuestion], already_answered_ids: set[str]) -> CandidateQuestion | None:
    for q in candidates:
        if q.question_id not in already_answered_ids:
            return q
    return None

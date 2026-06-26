"""
RED tests for promptverge/flows/verdicts_workflow.py — run_verdicts_flow (P1c).

All tests in this file are expected to FAIL (ImportError) until the module is
implemented.  Once implemented the tests assert the six load-bearing behaviors
cataloged in tests/verdicts_workflow.bug-catalog.md.

Bug catalog: tests/verdicts_workflow.bug-catalog.md
Finding: P1c-draftflow-absent — audit/02-static-audit.md L222
Intent: https://github.com/ImmortalDemonGod/PromptVerge/blob/7a176bd66d7427bd01167ba5f0ee7759dcae5db6/audit/02-static-audit.md#L222
"""

from __future__ import annotations

# RED until verdicts_workflow.py is created — ImportError on every test.
from promptverge.flows.verdicts_workflow import (  # noqa: F401 — RED import
    convert_card_dict_to_flashcore,
    run_verdicts_flow,
)


# ---------------------------------------------------------------------------
# Bug 1 — Flow absent: module import itself is the RED signal
# ---------------------------------------------------------------------------

def test_module_importable_guards_against_b1_flow_absent():
    """Bug 1 — run_verdicts_flow importable; guards against absent verdicts module.

    Catches: ImportError when promptverge.flows.verdicts_workflow does not exist.
    RED reason: the module does not exist at the time of writing.
    """
    # If the import at module scope above did not raise, this test body passes.
    assert callable(run_verdicts_flow), "run_verdicts_flow must be a callable Prefect flow"


# ---------------------------------------------------------------------------
# Bug 2 — front/back not clamped: ValidationError for long rationale
# ---------------------------------------------------------------------------

def test_convert_clamps_front_to_1024_guards_against_b2_overflow():
    """Bug 2 — front clamped to ≤1024; guards against ValidationError on long rationale.

    Catches: pydantic.ValidationError raised by flashcore.models.Card(front=<>1024)
    when the converter passes raw (unclamped) to_flashcards() output.

    The caller (this test) supplies a card dict with front exceeding the limit.
    The converter is the unit-under-test; it must clamp, not propagate.
    RED reason: convert_card_dict_to_flashcore does not exist yet.
    """
    long_front = "Q" * 1025  # one char over Card.front max_length=1024
    card_dict = {
        "deck": "SVP::Verdicts",
        "front": long_front,
        "back": "Short answer.",
        "tags": ["svp-verdict", "concept", "my-repo", "pr-1"],
        "origin_task": "SVP:owner/my-repo#1",
    }

    from flashcore.models import Card
    result: Card = convert_card_dict_to_flashcore(card_dict)

    assert len(result.front) <= 1024, (
        f"front must be clamped to ≤1024 chars; got {len(result.front)}"
    )
    assert result.front == long_front[:1024], (
        "front must be left-truncated to first 1024 chars"
    )


def test_convert_clamps_back_to_1024_guards_against_b2_overflow():
    """Bug 2 — back clamped to ≤1024; guards against ValidationError on long rationale.

    Same as front — back has the same max_length=1024 constraint on Card.
    RED reason: convert_card_dict_to_flashcore does not exist yet.
    """
    long_back = "A" * 2048
    card_dict = {
        "deck": "SVP::Verdicts",
        "front": "Short question.",
        "back": long_back,
        "tags": ["svp-verdict", "concept", "my-repo", "pr-1"],
        "origin_task": "SVP:owner/my-repo#1",
    }

    from flashcore.models import Card
    result: Card = convert_card_dict_to_flashcore(card_dict)

    assert len(result.back) <= 1024, (
        f"back must be clamped to ≤1024 chars; got {len(result.back)}"
    )


# ---------------------------------------------------------------------------
# Bug 3 — repo-slug tag not normalized to kebab-case: ValidationError
# ---------------------------------------------------------------------------

def test_convert_normalizes_underscore_repo_slug_to_kebab_guards_against_b3():
    """Bug 3 — repo-slug with underscore converted to kebab-case tag.

    flashcore.models.Card.validate_tags_kebab_case rejects 'my_repo'
    (underscore is not allowed).  The converter must replace '_' with '-'.

    The caller supplies the raw tag set from to_flashcards() which uses
    repo.split('/')[1].lower() — producing 'my_repo' for 'owner/my_repo'.
    The converter is the unit-under-test; it must normalize.

    RED reason: convert_card_dict_to_flashcore does not exist yet.
    """
    card_dict = {
        "deck": "SVP::Verdicts",
        "front": "What is the fix?",
        "back": "Apply the patch.",
        "tags": ["svp-verdict", "concept", "my_repo", "pr-5"],  # underscore tag
        "origin_task": "SVP:owner/my_repo#5",
    }

    from flashcore.models import Card
    result: Card = convert_card_dict_to_flashcore(card_dict)

    assert "my-repo" in result.tags, (
        f"Expected 'my-repo' (kebab) in tags, got: {result.tags}"
    )
    assert "my_repo" not in result.tags, (
        f"Underscore tag 'my_repo' must be replaced; got: {result.tags}"
    )


# ---------------------------------------------------------------------------
# Bug 4 — Watermark not advanced: duplicate POSTs on re-run
# ---------------------------------------------------------------------------

def test_watermark_skips_already_seen_verdict_guards_against_b4(mocker):
    """Bug 4 — watermark skips already-triaged verdicts on re-run.

    A second call to run_verdicts_flow with the same bundle must not POST
    a second task to tasks_api.  The watermark is the unit-under-test;
    the POST mock records how many times it is called.

    RED reason: run_verdicts_flow does not exist yet.
    """
    bundle = {
        "comparison": {
            "ai": {
                "approach_match": "different",
                "rationale": "The verifier missed the root cause.",
            }
        },
        "review": {"comments": []},
        "session": {},
        "repo": "owner/my-repo",
        "pr_number": 7,
    }

    mock_post = mocker.patch(
        "promptverge.flows.verdicts_workflow.post_pending_task",
        return_value={"id": "task-001", "status": "pending"},
    )
    mocker.patch(
        "promptverge.flows.verdicts_workflow.write_cards_to_flashdb",
        return_value=0,
    )

    run_verdicts_flow([bundle])
    first_call_count = mock_post.call_count

    # Second run with same bundle — watermark must prevent duplicate POST
    run_verdicts_flow([bundle])
    second_call_count = mock_post.call_count

    assert first_call_count >= 1, "First run must POST at least one task"
    assert second_call_count == first_call_count, (
        f"Second run must not POST again (watermark must skip); "
        f"first={first_call_count}, second={second_call_count}"
    )


# ---------------------------------------------------------------------------
# Bug 5 — POST /tasks not called: candidates never surface on approval board
# ---------------------------------------------------------------------------

def test_post_pending_task_called_per_candidate_guards_against_b5(mocker):
    """Bug 5 — POST /tasks called once per generated candidate.

    One bundle with a non-empty rationale produces one Card dict from
    to_flashcards().  The flow must call post_pending_task exactly once.

    RED reason: run_verdicts_flow does not exist yet.
    """
    bundle = {
        "comparison": {
            "ai": {
                "approach_match": "different",
                "rationale": "Verifier correctly identified the race condition.",
            }
        },
        "review": {"comments": []},
        "session": {},
        "repo": "owner/myrepo",
        "pr_number": 10,
    }

    mock_post = mocker.patch(
        "promptverge.flows.verdicts_workflow.post_pending_task",
        return_value={"id": "task-abc", "status": "pending"},
    )
    mocker.patch(
        "promptverge.flows.verdicts_workflow.write_cards_to_flashdb",
        return_value=0,
    )

    run_verdicts_flow([bundle])

    assert mock_post.call_count == 1, (
        f"Expected exactly 1 POST /tasks call for 1 candidate; got {mock_post.call_count}"
    )
    call_kwargs = mock_post.call_args
    # The posted task must carry pending status
    posted = call_kwargs[0][0] if call_kwargs[0] else call_kwargs[1]
    assert posted.get("status") == "pending", (
        f"Task POSTed with wrong status; expected 'pending', got: {posted.get('status')}"
    )


# ---------------------------------------------------------------------------
# Bug 6 — Reconcile writes without approval: ADR 0002 violated
# ---------------------------------------------------------------------------

def test_reconcile_does_not_write_pending_task_guards_against_b6(mocker):
    """Bug 6 — reconcile must NOT write to flash.db when task status is 'pending'.

    ADR 0002: cards reach flash.db only after operator approval (task status='done').
    Supplying a candidate whose task is still 'pending' must result in zero
    write_cards_to_flashdb calls.

    RED reason: run_verdicts_flow does not exist yet.
    """
    mocker.patch(
        "promptverge.flows.verdicts_workflow.post_pending_task",
        return_value={"id": "task-xyz", "status": "pending"},
    )
    mock_write = mocker.patch(
        "promptverge.flows.verdicts_workflow.write_cards_to_flashdb",
        return_value=0,
    )
    mocker.patch(
        "promptverge.flows.verdicts_workflow.get_task_status",
        return_value="pending",
    )

    bundle = {
        "comparison": {
            "ai": {
                "approach_match": "different",
                "rationale": "The fix addresses the null-pointer dereference.",
            }
        },
        "review": {"comments": []},
        "session": {},
        "repo": "owner/myrepo",
        "pr_number": 11,
    }

    run_verdicts_flow([bundle])

    assert mock_write.call_count == 0, (
        f"write_cards_to_flashdb must NOT be called for a pending task; "
        f"got {mock_write.call_count} call(s) — ADR 0002 violated"
    )


def test_reconcile_writes_when_task_done_guards_against_b6(mocker):
    """Bug 6 (positive case) — reconcile MUST write to flash.db when task status='done'.

    Supplying a candidate whose task has reached 'done' must trigger exactly one
    write_cards_to_flashdb call.

    RED reason: run_verdicts_flow does not exist yet.
    """
    mocker.patch(
        "promptverge.flows.verdicts_workflow.post_pending_task",
        return_value={"id": "task-done", "status": "done"},
    )
    mock_write = mocker.patch(
        "promptverge.flows.verdicts_workflow.write_cards_to_flashdb",
        return_value=1,
    )
    mocker.patch(
        "promptverge.flows.verdicts_workflow.get_task_status",
        return_value="done",
    )

    bundle = {
        "comparison": {
            "ai": {
                "approach_match": "different",
                "rationale": "Operator approved: root cause correctly identified.",
            }
        },
        "review": {"comments": []},
        "session": {},
        "repo": "owner/myrepo",
        "pr_number": 12,
    }

    run_verdicts_flow([bundle])

    assert mock_write.call_count == 1, (
        f"write_cards_to_flashdb must be called exactly once for a done task; "
        f"got {mock_write.call_count}"
    )

"""Auto-draft: turn minted SVP verdicts into Verdict Cards without a manual run.

The producer (`run_verdicts_flow` / `reconcile_verdicts`) is proven but
**manual-only** (issue #22). This module is the missing trigger layer:

    scan  ~/svp-console/.svp-sessions/<slug>/.svp/{session,comparison,review}-pr<N>.json
      ->  skip verdicts already drafted (verdict-level watermark = the pending
          store, keyed by origin_task 'SVP:{repo}#{pr}')
      ->  draft the new ones (run_verdicts_flow, enrichment on)
      ->  reconcile any operator-approved tasks into flash.db

Idempotent and side-effect-light: re-running drafts only verdicts not yet
drafted, and reconcile only writes tasks the operator has marked ``done``. That
makes it safe to fire two ways (identical code, only the trigger differs):

  * **immediate** — an svp-mint hook runs ``python -m promptverge.auto_draft``
    right after a verdict lands;
  * **daily fallback** — a launchd plist runs the same command, catching
    anything the hook missed.

Approval stays **manual** (ADR-0002): this drafts ``pending`` tasks and
reconciles approved ones; it never auto-approves.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
from typing import Optional

from promptverge.emit import VerdictBundle
from promptverge.flows import reconcile_verdicts, run_verdicts_flow
from promptverge.flows._verdicts_store import VerdictsPendingStore

log = logging.getLogger(__name__)

_DEFAULT_SESSIONS_DIR = Path.home() / "svp-console" / ".svp-sessions"


def _sessions_dir(override: Optional[Path] = None) -> Path:
    """Resolve the `.svp-sessions` root: arg > SVP_SESSIONS_DIR env > default."""
    if override is not None:
        return override
    return Path(os.environ.get("SVP_SESSIONS_DIR", str(_DEFAULT_SESSIONS_DIR)))


def parse_slug(slug: str) -> Optional[tuple[str, int]]:
    """``ImmortalDemonGod__cultivation-os-pr74`` -> ``('ImmortalDemonGod/cultivation-os', 74)``.

    Parsed from the right so repo names containing ``-`` survive. Returns
    ``None`` when the slug is not a ``<owner>__<repo>-pr<N>`` verdict directory.
    """
    head, sep, pr_str = slug.rpartition("-pr")
    if not sep or not pr_str.isdigit():
        return None
    owner, sep2, repo = head.partition("__")
    if not sep2 or not owner or not repo:
        return None
    return f"{owner}/{repo}", int(pr_str)


def load_bundle(session_dir: Path) -> Optional[VerdictBundle]:
    """Read the three sidecars in ``<session_dir>/.svp/`` into a ``VerdictBundle``.

    Returns ``None`` (skip, do not crash the run) when the directory is not a
    complete verdict: an unparseable slug, a missing sidecar, or unreadable JSON.
    """
    parsed = parse_slug(session_dir.name)
    if parsed is None:
        return None
    repo, pr = parsed
    svp = session_dir / ".svp"
    paths = {
        "comparison": svp / f"comparison-pr{pr}.json",
        "review": svp / f"review-pr{pr}.json",
        "session": svp / f"session-pr{pr}.json",
    }
    if not all(p.exists() for p in paths.values()):
        return None
    try:
        return {
            "comparison": json.loads(paths["comparison"].read_text()),
            "review": json.loads(paths["review"].read_text()),
            "session": json.loads(paths["session"].read_text()),
            "repo": repo,
            "pr_number": pr,
        }
    except (json.JSONDecodeError, OSError) as exc:
        log.warning("auto-draft: skipping %s — unreadable sidecar: %s", session_dir.name, exc)
        return None


def scan_new_bundles(sessions_dir: Path, store: VerdictsPendingStore) -> list[VerdictBundle]:
    """Verdict bundles under ``sessions_dir`` whose verdict has NOT been drafted.

    Verdict-level watermark: a verdict is skipped when any of its cards is already
    submitted (``is_submitted(origin_task, None)``). This avoids re-reading and —
    critically — re-ENRICHING (LLM cost + a nondeterministic re-draft that would
    dodge the per-card hash) verdicts already processed.
    """
    if not sessions_dir.is_dir():
        return []
    new: list[VerdictBundle] = []
    for session_dir in sorted(sessions_dir.iterdir()):
        if not session_dir.is_dir():
            continue
        bundle = load_bundle(session_dir)
        if bundle is None:
            continue
        origin_task = f"SVP:{bundle['repo']}#{bundle['pr_number']}"
        if store.is_submitted(origin_task, None):
            continue
        new.append(bundle)
    return new


def scan_and_draft(
    sessions_dir: Optional[Path] = None,
    *,
    db_path: Optional[str] = None,
    tasks_api_base_url: Optional[str] = None,
    enrich: bool = True,
) -> dict:
    """Scan minted verdicts, draft the new ones, reconcile approved ones.

    One ``VerdictsPendingStore`` is shared (via ``store_override``) across the
    watermark scan, the draft flow, and reconcile, so all three read/write the
    same DB by construction. Reconcile runs unconditionally — it picks up tasks
    you approved since the last run even when there are no new verdicts.

    Returns ``{"new_verdicts", "submitted", "written", "reconciled", "skipped"}``.
    """
    sdir = _sessions_dir(sessions_dir)
    store = VerdictsPendingStore(db_path)

    flow_kwargs: dict = {"store_override": store, "enrich_concepts": enrich}
    recon_kwargs: dict = {"store_override": store}
    if tasks_api_base_url:
        flow_kwargs["tasks_api_base_url"] = tasks_api_base_url
        recon_kwargs["tasks_api_base_url"] = tasks_api_base_url

    new_bundles = scan_new_bundles(sdir, store)
    flow_result = {"submitted": 0, "written": 0}
    if new_bundles:
        log.info("auto-draft: %d new verdict(s) -> drafting", len(new_bundles))
        flow_result = run_verdicts_flow(new_bundles, **flow_kwargs)

    recon_result = reconcile_verdicts(**recon_kwargs)

    return {
        "new_verdicts": len(new_bundles),
        "submitted": int(flow_result.get("submitted", 0)),
        "written": int(flow_result.get("written", 0)),
        "reconciled": int(recon_result.get("reconciled", 0)),
        "skipped": int(recon_result.get("skipped", 0)),
    }


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="promptverge.auto_draft",
        description="Scan minted SVP verdicts, draft new Verdict Cards, reconcile approved ones.",
    )
    parser.add_argument("--sessions-dir", help="override the .svp-sessions root")
    parser.add_argument("--db-path", help="override the verdicts pending store path")
    parser.add_argument("--tasks-api-base-url", help="override the tasks_api base URL")
    parser.add_argument(
        "--no-enrich",
        action="store_true",
        help="skip LLM concept enrichment (draft the structural cards as-is)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="log at INFO")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s auto-draft %(levelname)s %(message)s",
    )

    summary = scan_and_draft(
        sessions_dir=Path(args.sessions_dir) if args.sessions_dir else None,
        db_path=args.db_path,
        tasks_api_base_url=args.tasks_api_base_url,
        enrich=not args.no_enrich,
    )
    log.info("auto-draft summary: %s", summary)
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

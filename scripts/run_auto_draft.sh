#!/bin/zsh
# Wrapper that runs the auto-draft trigger with the right env, for both callers:
#   - the svp-console autosave hook (immediate: fires after a new verdict is saved)
#   - the com.blackbox.svp-autodraft launchd job (daily fallback)
#
# It sources OPENROUTER_API_KEY (for concept enrichment) from the operator .env and
# uses the pinned PromptVerge venv. Idempotent: drafts only un-watermarked verdicts
# and reconciles only operator-approved tasks (ADR-0002 — never auto-approves).
export PATH="/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"

ENV_FILE="$HOME/.openclaw/workspace/.env"
VENV_PY="$HOME/.promptverge-venv/bin/python"

# Load secrets (OPENROUTER_API_KEY, etc.) without echoing them.
if [ -f "$ENV_FILE" ]; then
  set -a
  . "$ENV_FILE" >/dev/null 2>&1
  set +a
fi

if [ ! -x "$VENV_PY" ]; then
  echo "auto-draft: venv python not found at $VENV_PY" >&2
  exit 1
fi

# enrichment ON by default (golden cards); pass --no-enrich to skip the LLM.
exec "$VENV_PY" -m promptverge.auto_draft -v "$@"

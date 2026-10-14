#!/usr/bin/env bash
# Initialise le dépôt GitHub : labels, milestones, issues.
# Prérequis : GitHub CLI (https://cli.github.com), `gh auth login`, dépôt déjà créé et cloné.
# Usage : ./scripts/setup_github.sh [owner/repo]
set -euo pipefail

REPO="${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"
cd "$(dirname "$0")"
echo "Dépôt : $REPO"

# --- Labels ---
declare -A LABELS=(
  ["area:car"]="1f77b4" ["area:base"]="17becf" ["area:pc"]="2ca02c" ["area:unity"]="9467bd"
  ["area:hardware"]="ff7f0e" ["area:infra"]="7f7f7f" ["area:docs"]="bcbd22" ["area:test"]="d62728"
  ["task"]="ededed" ["bug"]="d73a4a"
)
for l in "${!LABELS[@]}"; do
  gh label create "$l" --color "${LABELS[$l]}" --repo "$REPO" --force >/dev/null
done

# --- Milestones ---
for m in "M0 Setup" "M1 CAN banc" "M2 Trame + radio" "M3 PC + parseur" "M4 Dashboard v1" "M5 Intégration voiture" "M6 Fiabilisation"; do
  gh api "repos/$REPO/milestones" -f title="$m" >/dev/null 2>&1 || echo "Milestone déjà présent : $m"
done

# --- Issues (idempotent sur le titre) ---
EXISTING="$(gh issue list --repo "$REPO" --state all --limit 500 --json title -q '.[].title')"
while IFS=$'\t' read -r milestone label title body; do
  [ -z "$title" ] && continue
  if grep -Fxq "$title" <<<"$EXISTING"; then echo "Existe : $title"; continue; fi
  gh issue create --repo "$REPO" --title "$title" --body "$body" \
    --label "task,$label" --milestone "$milestone" >/dev/null
  echo "Créée : $title"
done < backlog.tsv

echo "Terminé. Créer ensuite un board : gh project create --owner <org|@me> --title 'FS Telemetry'"
echo "Colonnes conseillées : Backlog / Ready / In progress / Review / Done"

#!/usr/bin/env bash
# Human-assisted reproduction template.
# Copy to a disposable location, replace the example steps, and run it there.

set -euo pipefail

step() {
  printf '\n>>> %s\n' "$1"
  read -r -p "    [Press Enter when complete] " _
}

capture() {
  local variable="$1" question="$2" answer
  printf '\n>>> %s\n' "$question"
  read -r -p "    > " answer
  printf -v "$variable" '%s' "$answer"
}

# Replace these examples with actions that reach the reported symptom.
step "Perform the smallest action that triggers the problem."
capture REPRODUCED "Was the exact reported symptom reproduced? (yes/no)"
capture OBSERVATION "Enter the precise error, output, or timing observed:"

printf '\n--- Captured ---\n'
printf 'REPRODUCED=%s\n' "$REPRODUCED"
printf 'OBSERVATION=%s\n' "$OBSERVATION"

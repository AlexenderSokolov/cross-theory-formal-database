#!/bin/sh
set -eu
work=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
controller_id=${CORPUS_CONTROLLER_ID:-}
generation=${CORPUS_CONTROLLER_GENERATION:-}
case "${1:-status}" in
 install)
  [ -n "$generation" ] || { echo "CORPUS_CONTROLLER_GENERATION required" >&2; exit 2; }
  [ -n "$controller_id" ] || { echo "CORPUS_CONTROLLER_ID required for service install" >&2; exit 2; }
  "$work/corpusctl" --controller-id "$controller_id" --generation "$generation" collect --json
  loginctl enable-linger "$(id -un)"
  mkdir -p "$HOME/.config/systemd/user"
  cp "$work/scripts/corpusctl-runtime.service" "$HOME/.config/systemd/user/corpusctl.service"
  mkdir -p "$HOME/.config/systemd/user/corpusctl.service.d"
  printf '[Service]\nExecStart=\nExecStart=%s/corpusctl --controller-id %s --generation %s serve --max-jobs 3 --poll-seconds 10\nRestart=no\n' "$work" "$controller_id" "$generation" > "$HOME/.config/systemd/user/corpusctl.service.d/owner.conf"
  systemctl --user daemon-reload
  systemctl --user enable --now corpusctl.service
  ;;
 status) ;;
 *) echo 'Usage: run_corpusctl_service.sh [install|status]' >&2; exit 2 ;;
esac
systemctl --user show corpusctl.service -p ActiveState -p SubState -p MainPID
exec "$work/corpusctl" status --json

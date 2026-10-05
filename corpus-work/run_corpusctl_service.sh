#!/bin/sh
set -eu
work=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
case "${1:-status}" in
 install)
  loginctl enable-linger "$(id -un)"
  mkdir -p "$HOME/.config/systemd/user"
  cp "$work/scripts/corpusctl-runtime.service" "$HOME/.config/systemd/user/corpusctl.service"
  systemctl --user daemon-reload
  systemctl --user enable --now corpusctl.service
  ;;
 status) ;;
 *) echo 'Usage: run_corpusctl_service.sh [install|status]' >&2; exit 2 ;;
esac
systemctl --user show corpusctl.service -p ActiveState -p SubState -p MainPID
exec "$work/corpusctl" status --json

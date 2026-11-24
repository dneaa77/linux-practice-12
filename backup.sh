#!/usr/bin/env bash
set -euo pipefail
if [[ $# != 3 ]]; then echo 'Usage: backup.sh backup|restore SOURCE DESTINATION' >&2; exit 1; fi
mode=$1
case "$mode" in backup|restore) ;; *) exit 2;; esac
src=$(realpath "$2")
dst=$(realpath -m "$3")
[[ -d "$src" ]] || { echo 'Source missing'; exit 1; }
if [[ "$src/" == "$dst/"* || "$dst/" == "$src/"* ]]; then echo 'Directories must not overlap'; exit 1; fi
mkdir -p "$dst"
log="${BACKUP_LOG:-$PWD/backup.log}"
printf '\n%s %s %s -> %s\n' "$(date -Is)" "$mode" "$src" "$dst" | tee -a "$log"
rsync -a --checksum --itemize-changes -- "$src/" "$dst/" | tee -a "$log"

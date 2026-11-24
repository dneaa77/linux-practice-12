#!/usr/bin/env bash
set -euo pipefail
D=$(mktemp -d)
IMG=$D/disk.img
MNT=$D/mnt
mkdir "$MNT"
cleanup(){ if mountpoint -q "$MNT"; then sudo umount "$MNT" || return; fi; rm -rf -- "$D"; }
trap cleanup EXIT
sudo -v
dd if=/dev/zero of="$IMG" bs=1M count=16 status=none
mkfs.ext4 -q -N 128 -F "$IMG"
sudo mount -o loop "$IMG" "$MNT"
sudo chown "$(id -u):$(id -g)" "$MNT"
df -h "$MNT"; df -i "$MNT"
i=0
while touch "$MNT/file_$i"; do
  i=$((i+1))
  if (( i % 20 == 0 )); then df -i "$MNT"; fi
done
printf 'Created %s empty files\n' "$i"
df -i "$MNT"; df -h "$MNT"

#!/usr/bin/env bash
set -eu
D=$(mktemp -d "$PWD/demo.XXXXXX")
chmod 755 "$D"
cd "$D"
mkdir -p docs data
printf 'Hello Ubuntu\n' > docs/original.txt
ls -li docs
ln docs/original.txt docs/hard.txt
ln -s original.txt docs/symbolic.txt
ls -li docs
rm docs/original.txt
ls -li docs
cat docs/hard.txt
if ! cat docs/symbolic.txt; then echo 'Symbolic link is broken'; fi
printf 'private data\n' > docs/access.txt
chmod u=rw,g=r,o= docs/access.txt
chmod 640 docs/access.txt
ls -li docs/access.txt
if command -v sudo >/dev/null; then
  sudo -u nobody -- cat docs/access.txt || echo 'Read denied for nobody'
  sudo -u nobody -- sh -c 'echo test >> "$1"' sh "$PWD/docs/access.txt" || echo 'Write denied for nobody'
fi
# 2 MiB logical size
truncate -s 2M data/large.bin
find . -type f -size +1048576c -mtime -1 -print
printf 'Demo: %s\n' "$D"

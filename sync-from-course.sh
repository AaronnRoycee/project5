#!/usr/bin/env bash
set -euo pipefail
src="$HOME/Documents/6332/coursecontainer/data/word-count-app/"
dst="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/word-count-app/"
rsync -a --delete --exclude node_modules --exclude books --exclude .DS_Store "$src" "$dst"
echo "synced $src -> $dst"

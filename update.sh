#!/bin/bash
set -e -o pipefail

python commandnotfound-list.py > commandlist.csv~
LC_ALL=C sort commandlist.csv~ > commandlist.csv
rm -f commandlist.csv~
git diff --quiet commandlist.csv && exit
make bumpnogit
latest=$(curl -sSf "https://download.clearlinux.org/update/version/formatstaging/latest")
if [ -z "$latest" ]; then exit 1; fi
git commit -m "update command list for $latest" -a
make koji-nowait

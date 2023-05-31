#!/usr/bin/env sh

set -euo pipefail

readonly nexus_contrib_path="/nexus-contrib"

git clone -n --depth=1 --filter=tree:0 https://"$TOKEN"@$(echo "$BRANCH" | sed -r 's/@([a-z]+)$/ -b \1/') $nexus_contrib_path

cd $nexus_contrib_path

for d in "$@"
do
  git sparse-checkout set --no-cone "$d"
  git checkout
done

rm -rf .git

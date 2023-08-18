#!/usr/bin/env sh

set -euo pipefail

readonly nexus_app_stack_contrib_path="/nexus-app-stack-contrib"

git clone -n --depth=1 --filter=tree:0 https://"$TOKEN"@$(echo "$BRANCH" | sed -r 's/@([a-z]+)$/ -b \1/') $nexus_app_stack_contrib_path

cd $nexus_app_stack_contrib_path

git sparse-checkout set --no-cone "$@"
git checkout

ls -d "$@" > /dev/null

rm -rf .git

#!/usr/bin/env sh

set -euo pipefail

readonly nexus_app_stack_contrib_path="/nexus-app-stack-contrib"

git clone -n --depth=1 --filter=tree:0 https://$(echo "$BRANCH" | sed -r 's/@([a-z]+)$/ -b \1/') $nexus_app_stack_contrib_path

cd $nexus_app_stack_contrib_path

cone_pattern_set=$*

case $* in
  "api/"*|*" api/"*)
    cone_pattern_set="/api/* !/api/*/ $cone_pattern_set"
    ;;
esac
case $* in
  "cli/"*|*" cli/"*)
    cone_pattern_set="/cli/* !/cli/*/ $cone_pattern_set"
    ;;
esac
case $* in
  "ui/"*|*" ui/"*)
    cone_pattern_set="/ui/* !/ui/*/ $cone_pattern_set"
    ;;
esac

git sparse-checkout set --no-cone $cone_pattern_set
git checkout

ls -d "$@" > /dev/null

if [ "$ENVIRONMENT" = "Production" ]
then
  rm -rf .git
fi

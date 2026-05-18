#!/usr/bin/env bash

cd $(dirname "${BASH_SOURCE[0]}")
cmd="nix-shell --run 'python ./solution.py run $1'"
eval "$cmd"


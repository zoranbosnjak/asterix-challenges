#!/usr/bin/env bash

cd $(dirname "${BASH_SOURCE[0]}")
nix-shell --run 'ghc -O2 solution.hs'
cmd="nix-shell --run './solution run $1'"
eval "$cmd"


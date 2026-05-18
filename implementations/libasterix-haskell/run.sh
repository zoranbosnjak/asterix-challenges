#!/usr/bin/env bash

cd $(dirname "${BASH_SOURCE[0]}")
cmd="nix-shell --run 'runhaskell solution.hs run $1'"
eval "$cmd"


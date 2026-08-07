# Running examples

```bash
nix-shell

# monitor with ghcid
ghcid --no-title --lint "--command=ghci -Wall solution.hs"

challenge={some-challenge-id}
gen=../../bin/testing-framework.py

# run examples (interpreted)
runhaskell solution.hs manifest

$gen samples $challenge | runhaskell solution.hs run $challenge

# run examples (compiled)
ghc -O2 solution.hs
$gen samples $challenge | ./solution run $challenge

# experiments with threading and threadscope
ghc -O2 -threaded -rtsopts solution.hs
$gen samples $challenge | ./solution run $challenge +RTS -N -l
threadscope solution.eventlog

exit # out of nix-shell
```


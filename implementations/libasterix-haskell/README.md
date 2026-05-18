# Running examples

```bash
nix-shell

# monitor with ghcid
ghcid --no-title --lint "--command=ghci -Wall solution.hs"

# run examples (interpreted)
runhaskell solution.hs manifest
cat ../../samples.txt | runhaskell solution.hs run {challenge-id}

# run examples (compiled)
ghc -O2 solution.hs
cat ../../samples.txt | ./solution run {challenge-id}

# experiments with threading and threadscope
ghc -O2 -threaded -rtsopts solution.hs
cat ../../samples.txt | ./solution run {challenge-id} +RTS -N -l
threadscope solution.eventlog

exit # out of nix-shell
```


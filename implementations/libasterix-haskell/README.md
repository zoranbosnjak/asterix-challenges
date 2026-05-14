# Running examples

```bash
nix-shell

# monitor with ghcid
ghcid --no-title "--command=ghci -Wall solution.hs"

# run examples (interpreted)
runhaskell solution.hs -t ../../samples.txt

# run examples (compiled)
ghc -O2 solution.hs
./solution -t ../../samples.txt

# experiments with threading and threadscope
ghc -O2 -threaded -rtsopts solution.hs
./solution -t ../../samples.txt +RTS -N -l
threadscope solution.eventlog

exit # out of nix-shell
```


# Running examples

```bash
nix-shell

# monitor with ghcid
ghcid --no-title "--command=ghci -Wall solution.hs"

# run examples (interpreted)
runhaskell solution.hs ../../samples.txt

# run examples (compiled)
ghc -O2 solution.hs
./solution ../../samples.txt

exit # out of nix-shell
```


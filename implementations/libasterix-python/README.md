# Running examples

```bash
nix-shell

# monitor with mypy
find . | grep "\.py$" | entr sh -c 'clear && date && mypy'

# run examples
./solution.py ../../samples.txt

exit # out of nix-shell
```


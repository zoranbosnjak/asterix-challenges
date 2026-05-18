# Running examples

```bash
nix-shell

# monitor with mypy
find . | grep "\.py$" | entr sh -c 'clear && date && mypy'

# run examples
./solution.py manifest
cat ../../samples.txt | ./solution.py run WJLXIXEB

exit # out of nix-shell
```


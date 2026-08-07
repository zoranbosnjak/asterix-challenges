# Running examples

```bash
nix-shell

# monitor code warnings with mypy
find . | grep "\.py$" | entr sh -c 'clear && date && mypy'

# run examples

challenge={some-challenge-id}
gen=../../bin/testing-framework.py

./solution.py manifest
$gen samples $challenge | ./solution.py run $challenge

exit # out of nix-shell
```


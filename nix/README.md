# Remarks

```bash
# update reference to asterix-libs if necessary
nix-prefetch-git https://github.com/zoranbosnjak/asterix-libs.git > asterix-libs.json

# update reference to asterix-tool
hsh=HEAD
nix-prefetch-git --rev $hsh https://github.com/zoranbosnjak/asterix-tool.git \
    > asterix-tool.json
```


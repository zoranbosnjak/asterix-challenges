# Asterix challenges

This repository contains several asterix related data processing tasks. A main
purpose is:

- to check interoperability between several codec implementations
- to check/compare performance and explore possible optimizations

All tasks/examples include reading random asterix samples from disk or from the
network and producing a simple result (such as plain integer) which is easy to
compare between different implementations. A first priority for all
implementations is to agree on the result (assuming the same input samples and
asterix category/edition selections).

Input samples might also contain errors. Each implementation shall handle
errors according to specific task (for example: count errors, ignore
errors,...).

## Asterix sample generator and reference decoder

A simple (random) sample generator is possible using
[ast-tool-py](https://pypi.org/project/ast-tool-py/) tool.

```bash
# save some samples to a file
categories="--cat 48 1.32 --cat 62 1.21 --cat 63 1.7 --cat 65 1.6"
samples=1000
errinject=1000
ast-tool-py -s --empty-selection $categories \
    random --seed 0 --error-bit-flip $errinject \
    | head -n $samples \
    | tee samples.txt

# reference docoder
cat samples.txt | ast-tool-py -s decode

# parameters must match on all comparable tests
sha1sum samples.txt
ast-tool-py --version
```

## Examples

### Example 01

Return number of decoding errors in given samples.

### Example 02

Return total number of valid records in given samples.

### Example 03

Extract all items (if present) and sum them up, using modulo 256 (the final
result shall be in range `[0..255]`).

- I048/010/SAC
- I062/015
- I062/010/SIC
- I062/080/SRC
- I062/080/MD5
- I062/510/IDENT
- I062/290/MDS

### Example 04

Return number of 'spare' bits abuses. That is: number of times that spare bits
are not zero.


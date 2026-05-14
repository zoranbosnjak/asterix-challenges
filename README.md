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
[ast-tool-py](https://pypi.org/project/ast-tool-py/).

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

### Example 00

Do nothing. An example shall return constant 0.

The purpose of this example is to measure a function call overhead, when given
a list of samples as argument.

### Example 01

Return number of datagrams in given samples.

There is no real asterix processing, just determining input list length.

### Example 02

Return number of valid datagrams in given samples.

A datagram is considered valid if all datablocks are correctly parsed. This
example does not need to process records inside datablocks.

### Example 03

Return number of valid datablocks in given samples.

Each datagram might contain one or more datablocks. Datablocks are considered
valid (counted) only when a complete datagram is properly processed. That is:
if the last datablock can not be parsed correctly, a complete datablock shall
be rejected. This example does not need to process records inside datablocks.

### Example 04

Return number of decoding errors in given samples.

### Example 05

Return total number of valid records in given samples.

### Example 06

Process valid records.

Extract all items (if present) and sum them up, using modulo 256 (the final
result shall be in range `[0..255]`).

- I048/010/SAC
- I062/015
- I062/010/SIC
- I062/080/SRC
- I062/080/MD5
- I062/510/IDENT
- I062/290/MDS

### Example 07

Process valid records.

Return number of 'spare' bits abuses. That is: number of times that spare bits
are not zero.

## Implementations

The `/implementations` folder contains solutions for the examples. Each
individual subfolder also contains the `README.md` file with the instructions
how to run programs.


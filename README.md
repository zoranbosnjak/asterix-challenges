# Asterix challenges

This repository contains asterix related data processing tasks/challenges. A
main purpose is:

- to check interoperability (result matching) between different codec
  implementations
- to check/compare performance and explore possible optimizations
- to check codec/application robustness (stable operation with any input)

## API

Each challenge is implemented in a form of a data filter with a single input
and a single output. Inputs are fed to the filter as a stream of values and the
filter must produce a stream of outputs.

In general, input is an arbitrary value and the filters are classified in the
following groups:

- decoding filter, receiving asterix encoded datagrams and producing some
  simple structure, such as plain integer or JSON encoded simple structures;
- encoding filters, receiving simple structure such as JSON and producing
  asterix encoded datagrams;
- asterix to asterix filters, where both input and output are asterix encoded
  datagrams;

Some high level asterix related application tests might require a stateful
filter, where a particular output depends on a current input and previous
inputs. For example: WX picture encoded in asterix contains messages like
"start of picture", "WX vectors", "end of picture"..., which are dispersed over
several datagrams. In this case, the filter would still produce some result on
every input datagram (a null value), to mark the progress. But the final result
is produced only after receiving an "end of picture" message, where the
filtering process starts over.

Input samples might also contain errors. Each implementation shall handle
errors according to a specific task (for example: count errors, ignore
errors,...).

When the input samples represent asterix encoding, a filter is tipically
required to handle each containing datablock separately, which should be
reflected in a resulting value (for example `null` on error or list of
datablock results). Furthermore, datablocks normally contain many asterix
records, which are required to be handled record by record. In this case the
result might include nested list structure, representing result for each
record.

On the first level of asterix, datablocks are considered valid only when a
complete datagram is properly processed. That is: if the last datablock can not
be decoded correctly, a complete datablock shall be rejected.

## Input/output format

Interfacing with the filter shall be possible either in text or binary format.
To simplify the interface, input/output values are either:

- a bytestring
- or simple values, which can be encoded in [JSON](https://www.json.org/)

### Text format

A text format assumes newline `\n` character as a delimitter.

- Bytestring is encoded as hex, where each byte is encoded as two characters,
  from '00' to 'ff. For example, a 4-byte datagram: `"001122ff\n"`
- Other values are encoded as unformatted single line JSON, such as:
  `"[null, 1, 2, 3]\n"`.

Under this setup, the implementation under test (IUT) can be tested with a
bash pipeline, for example:

```bash
cat input-samples | run-some-filter > results
```

### Binary format

Binary format is similar, but is based on [MessagePack](https://msgpack.org/),
instead of JSON. This format is more compact and in general faster in
comparison to JSON.

TODO: define details...

## Challenges

To avoid sequencing/renaming... confusion, each challenge is identified with a
random string identifier, rather than sequentially. A new random value can be
obtained for example with the following shell command:

```bash
cat /dev/urandom | tr -dc A-Z | head -c8 | xargs echo
```

The challenges are described in <./CHALLENGES.org>.

## Implementations

The `/implementations` folder contains solutions for the challenges. Each
individual subfolder also contains the `README.md` file with the instructions
how to run programs.

## Asterix sample generator and reference decoder

A simple (pseudo random) asterix sample generator is possible using
[ast-tool-py](https://pypi.org/project/ast-tool-py/).

```bash
# category/edition selection
categories="--cat 62 1.21 --cat 63 1.7 --cat 65 1.6"

# number of required samples
samples=1000

# error injection ratio
errinject=1000

# run random asterix generator, save samples to a file
ast-tool-py -s --empty-selection $categories \
    random --seed 0 --error-bit-flip $errinject \
    | head -n $samples \
    | tee samples.txt

# decode samples with the reference docoder
cat samples.txt | ast-tool-py -s decode
```

## Running individual tests

Implementations shall be able to be tested from the shell, for example:

```bash
# run filter on the first 'N' samples
cat samples.txt | run-some-filter | head -n 100 > results.txt

# run filter on an infinite stream, ignore results, observe stability
infinite-sample-generator | run-some-filter > /dev/null
```

## Running tests with the framework

A testing framework `./bin/testing-framework.py` is a support program for
running interoperability tests. Features:
- generate random samples, relevant for the challenge;
- feed the same sample to all implementations and compare the results;
- focus on one challenge at the time;
- run all challenges automatically, one after another;
- provide a simple performance comparison between implementations;

Example:

```bash
# get basic help and list of supported tests
./bin/testing-framework.py -h
./bin/testing-framework.py manifest

# example challenge
challenge=WJLXIXEB

# generate some random samples
./bin/testing-framework.py samples $challenge | head -n 20

# run infinite test on selected implementations, interrupt with CTRL-C
./bin/testing-framework.py \
    --impl "./implementations/libasterix-python/run.sh" \
    --impl "./implementations/libasterix-haskell/run.sh" \
    --print-progress \
    --error 0.001 \
    run --append-challenge $challenge

# auto run all tests, interrupt with CTRL-C
./bin/testing-framework.py \
    --impl "./implementations/libasterix-python/run.sh" \
    --impl "./implementations/libasterix-haskell/run.sh" \
    --print-progress \
    --error 0.001 \
    autorun

# run simple benchmark test
./bin/testing-framework.py --seed 0 \
    --impl "./implementations/libasterix-python/run.sh" \
    --impl "./implementations/libasterix-haskell/run.sh" \
    benchmark
```


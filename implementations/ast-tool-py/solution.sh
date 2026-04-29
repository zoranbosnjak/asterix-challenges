#!/usr/bin/env bash

wd=$(realpath $0 | xargs dirname)
samples=$@

# solution to example 00 (dummy output)
echo "0"

# solution to example 01
cat $samples | ast-tool-py -s decode | grep "^Error!" | wc -l

# solution to example 02
cat $samples | ast-tool-py -s decode -l 3 | grep "record: len" | wc -l

# solution to example 03
cat $samples | ast-tool-py -s custom --script $wd/custom.py --call custom

# solution to example 04
cat $samples | ast-tool-py -s decode | grep "(Spare).*bin.*1" | wc -l


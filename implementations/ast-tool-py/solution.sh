#!/usr/bin/env bash

wd=$(realpath $0 | xargs dirname)
samples=$@

echo "--- example 00 - do nothing ---"
echo "0"

echo "--- example 01 - num of all datagrams ---"
cat $samples | wc -l

echo "--- example 02 - num of valid datagrams ---"
cat $samples | ast-tool-py -s custom --script $wd/custom.py --call example02

echo "--- example 03 - num of datablocks ---"
cat $samples | ast-tool-py -s custom --script $wd/custom.py --call example03

echo "--- example 04 - decoding errors ---"
cat $samples | ast-tool-py -s decode | grep "^Error!" | wc -l

echo "--- example 05 - valid records ---"
cat $samples | ast-tool-py -s decode -l 3 | grep "record: len" | wc -l

echo "--- example 06 - item extraction ---"
cat $samples | ast-tool-py -s custom --script $wd/custom.py --call example06

echo "--- example 07 - spare abuses ---"
cat $samples | ast-tool-py -s decode | grep "(Spare).*bin.*1" | wc -l


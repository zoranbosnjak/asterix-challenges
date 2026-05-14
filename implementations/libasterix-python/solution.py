#!/usr/bin/env python3

from typing import *
import argparse
import datetime

from asterix.base import *
import asterix.generated as gen

Cat048 = gen.Cat_048_1_32
Cat062 = gen.Cat_062_1_21
Cat063 = gen.Cat_063_1_7
Cat065 = gen.Cat_065_1_6

specs = {
    48: Cat048,
    62: Cat062,
    63: Cat063,
    65: Cat065,
}

def load_samples(paths: List[str]) -> List[bytes]:
    result: List[bytes] = []
    for p in paths:
        with open(p) as f:
            for line in f:
                result.append(bytes.fromhex(line.strip()))
    return result

# do nothing
def example00(samples: List[bytes]) -> int:
    return 0

# number of all datagrams
def example01(samples: List[bytes]) -> int:
    return len(samples)

# number of valid datagrams
def example02(samples: List[bytes]) -> int:
    def check_sample(sample: bytes) -> int:
        raw_datablocks = RawDatablock.parse(Bits.from_bytes(sample))
        if isinstance(raw_datablocks, ValueError):
            return 0
        return 1
    return sum([check_sample(sample) for sample in samples])

# number of datablocks
def example03(samples: List[bytes]) -> int:
    def check_sample(sample: bytes) -> int:
        raw_datablocks = RawDatablock.parse(Bits.from_bytes(sample))
        if isinstance(raw_datablocks, ValueError):
            return 0
        return len(raw_datablocks)
    return sum([check_sample(sample) for sample in samples])

# number of decoding errors
def example04(samples: List[bytes]) -> int:
    def check_datablock(db: Any) -> int:
        cat = db.get_category()
        Spec = specs.get(cat)
        if Spec is None:
            return 0
        result = Spec.cv_uap.parse(db.get_raw_records()) # type: ignore
        if isinstance(result, ValueError):
            return 1
        return 0
    def check_sample(sample: bytes) -> int:
        raw_datablocks = RawDatablock.parse(Bits.from_bytes(sample))
        if isinstance(raw_datablocks, ValueError):
            return 1
        return sum([check_datablock(db) for db in raw_datablocks])
    return sum([check_sample(sample) for sample in samples])

# number of valid records
def example05(samples: List[bytes]) -> int:
    def check_datablock(db: Any) -> int:
        cat = db.get_category()
        Spec = specs.get(cat)
        if Spec is None:
            return 0
        result = Spec.cv_uap.parse(db.get_raw_records()) # type: ignore
        if isinstance(result, ValueError):
            return 0
        return len(result)
    def check_sample(sample: bytes) -> int:
        raw_datablocks = RawDatablock.parse(Bits.from_bytes(sample))
        if isinstance(raw_datablocks, ValueError):
            return 0
        return sum([check_datablock(db) for db in raw_datablocks])
    return sum([check_sample(sample) for sample in samples])

class Accumulator:
    def __init__(self) -> None: self.val: int = 0
    def bump(self, val: int) -> None: self.val = (self.val + val) % 256

# custom item extraction
def example06(samples: List[bytes]) -> int:
    acc = Accumulator()

    def hander048(rec: Cat048.cv_record) -> None:
        i010 = rec.get_item('010')
        if i010 is not None:
            acc.bump(i010.variation.get_item('SAC').as_uint())

    def hander062(rec: Cat062.cv_record) -> None:
        i015 = rec.get_item('015')
        if i015 is not None:
            acc.bump(i015.variation.as_uint())
        i010 = rec.get_item('010')
        if i010 is not None:
            acc.bump(i010.variation.get_item('SIC').as_uint())
        i080 = rec.get_item('080')
        if i080 is not None:
            acc.bump(i080.variation.get_item('SRC').as_uint())
        if i080 is not None:
            iMD5 = i080.variation.get_item('MD5')
            if iMD5 is not None:
                acc.bump(iMD5.as_uint())
        i510 = rec.get_item('510')
        if i510 is not None:
            for i in i510.variation.get_list():
                acc.bump(i.get_item('IDENT').as_uint())
        i290 = rec.get_item('290')
        if i290 is not None:
            iMDS = i290.variation.get_item('MDS')
            if iMDS is not None:
                acc.bump(iMDS.as_uint())

    def handle_datablocks(raw_datablocks: Any, d: Any) -> None:
        for raw_db in raw_datablocks:
            cat = raw_db.get_category()
            lookup = d.get(cat)
            if lookup is None: continue
            Spec, handler = lookup
            records = Spec.cv_uap.parse(raw_db.get_raw_records())
            if isinstance(records, ValueError): continue
            for rec in records:
                handler(rec)

    for sample in samples:
        raw_datablocks = RawDatablock.parse(Bits.from_bytes(sample))
        if isinstance(raw_datablocks, ValueError):
            continue
        handle_datablocks(raw_datablocks, {
            48: (Cat048, hander048),
            62: (Cat062, hander062),
        })

    return acc.val

# number of abused spare bits
def example07(samples: List[bytes]) -> int:
    def check_item(i: Any) -> int:
        if not isinstance(i, Spare):
            return 0
        return 0 if i.as_uint() == 0 else 1
    def check_mitem(i: Any) -> int:
        if i is None:
            return 0
        return check_item(i)
    def check_variation(var: Any) -> int:
        if isinstance(var, Element):
            return 0
        elif isinstance(var, Group):
            return sum([check_item(i) for i in var.arg])
        elif isinstance(var, Extended):
            def check_ext_group(g: Any) -> int:
                return sum([check_mitem(i) for i in g])
            return sum([check_ext_group(g) for g in var.arg])
        elif isinstance(var, Repetitive):
            return sum([check_variation(v) for v in var.arg])
        elif isinstance(var, Explicit):
            return 0
        elif isinstance(var, Compound):
            return sum([check_nsp(n) for n in var.arg.values()])
        else:
            raise Exception('unexpected subclass', var)
    def check_nsp(nsp: Any) -> int:
        return check_variation(nsp.variation)
    def check_record(r: Any) -> int:
        return sum([check_nsp(nsp) for (name, nsp) in r.items_regular.items()])
    def check_datablock(db: Any) -> int:
        cat = db.get_category()
        Spec = specs.get(cat)
        if Spec is None:
            return 0
        result = Spec.cv_uap.parse(db.get_raw_records()) # type: ignore
        if isinstance(result, ValueError):
            return 0
        return sum([check_record(r) for r in result])
    def check_sample(sample: bytes) -> int:
        raw_datablocks = RawDatablock.parse(Bits.from_bytes(sample))
        if isinstance(raw_datablocks, ValueError):
            return 0
        return sum([check_datablock(db) for db in raw_datablocks])
    return sum([check_sample(sample) for sample in samples])

def time_it(show_time: bool, name: str, example: Any, samples: List[bytes]) -> None:
    if show_time:
        print ("--- " + name + " ---")
    t1 = datetime.datetime.now()
    print(example(samples))
    t2 = datetime.datetime.now()
    dt = t2 - t1
    if show_time:
        print('{:.9f}s'.format(dt.total_seconds()))

parser = argparse.ArgumentParser(prog='Test')
parser.add_argument('-t', '--time-it', action='store_true')
parser.add_argument('files', nargs='*', help='path to input files')
args = parser.parse_args()

# main
samples = load_samples(args.files)
time_it(args.time_it, "example 00 - do nothing", example00, samples)
time_it(args.time_it, "example 01 - num of all datagrams", example01, samples)
time_it(args.time_it, "example 02 - num of valid datagrams", example02, samples)
time_it(args.time_it, "example 03 - num of datablocks", example03, samples)
time_it(args.time_it, "example 04 - decoding errors", example04, samples)
time_it(args.time_it, "example 05 - valid records", example05, samples)
time_it(args.time_it, "example 06 - item extraction", example06, samples)
time_it(args.time_it, "example 07 - spare abuses", example07, samples)


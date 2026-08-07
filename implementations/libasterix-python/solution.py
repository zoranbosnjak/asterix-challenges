#!/usr/bin/env python3

from typing import *
import json
import sys
import argparse
import datetime
import binascii
import signal

from asterix.base import *
import asterix.generated as gen

signal.signal(signal.SIGPIPE, signal.SIG_DFL)

Cat062 = gen.Cat_062_1_21
Cat063 = gen.Cat_063_1_7
Cat065 = gen.Cat_065_1_6

specs = {
    62: Cat062,
    63: Cat063,
    65: Cat065,
}


class Filter():
    def run(self) -> None:
        for line in sys.stdin:
            print(self.process(line.strip()))
            sys.stdout.flush()

    def process(self, sample: str) -> str:
        return ''

    def dump(self, val: Any) -> str:
        return json.dumps(val, separators=(',', ':'), sort_keys=True)


class WJLXIXEB(Filter):
    """identity filter"""

    def process(self, sample: str) -> str:
        try:
            bs = binascii.unhexlify(sample)
        except (binascii.Error):
            return ''
        return binascii.hexlify(bs).decode('utf-8')


class TXHWAQHG(Filter):
    """determine length of input"""

    def process(self, sample: str) -> str:
        try:
            bs = binascii.unhexlify(sample)
            n = len(bs)
        except (binascii.Error):
            n = -1
        return str(n)


class GCMEDPFW(Filter):
    """encode constant datagram"""

    def process(self, sample: str) -> str:
        try:
            n = int(sample)
        except ValueError:
            return ''
        return bytes(n).hex()


class CAOXOESE(Filter):
    """decode first level of asterix"""

    def process(self, sample: str) -> str:
        try:
            bs = binascii.unhexlify(sample)
        except (binascii.Error):
            return self.dump(None)

        def check_datagram(bs: bytes) -> Any:
            dbs = RawDatablock.parse(Bits.from_bytes(bs))
            if isinstance(dbs, ValueError):
                return None
            return [[db.get_category(), db.get_length()] for db in dbs]

        return self.dump(check_datagram(bs))


class JWOONFHI(Filter):
    """encode first level of asterix"""

    def process(self, sample: str) -> str:
        try:
            lst = json.loads(sample)
        except json.decoder.JSONDecodeError:
            return ''
        if not isinstance(lst, list):
            return ''
        result = Bits.from_bytes(b'')
        for item in lst:
            if not isinstance(item, list):
                return ''
            if len(item) != 2:
                return ''
            cat, ln = item
            if cat < 0 or cat > 255:
                return ''
            if ln < 3:
                return ''
            result += Bits.from_uinteger(cat, 0, 8)
            result += Bits.from_uinteger(ln, 0, 16)
            result += Bits.from_bytes(bytes(ln - 3))
        return result.to_bytes().hex()


class FCYKLBBQ(Filter):
    """reverse datablocks"""

    def process(self, sample: str) -> str:
        try:
            bs = binascii.unhexlify(sample)
        except (binascii.Error):
            return self.dump(None)
        dbs = RawDatablock.parse(Bits.from_bytes(bs))
        if isinstance(dbs, ValueError):
            return ''
        result = b''
        for db in reversed(dbs):
            result += db.unparse().to_bytes()
        return result.hex()


class MVQCOXZJ(Filter):
    """full asterix record decoding, count records"""

    def process(self, sample: str) -> str:
        try:
            bs = binascii.unhexlify(sample)
        except (binascii.Error):
            return self.dump(None)
        dbs = RawDatablock.parse(Bits.from_bytes(bs))
        if isinstance(dbs, ValueError):
            return self.dump(None)

        def check_datablock(db: Any) -> Optional[int]:
            cat = db.get_category()
            result: Any
            if cat == 62:
                result = Cat062.cv_uap.parse(db.get_raw_records())
            elif cat == 63:
                result = Cat063.cv_uap.parse(db.get_raw_records())
            elif cat == 65:
                result = Cat065.cv_uap.parse(db.get_raw_records())
            else:
                return -1
            if isinstance(result, ValueError):
                return None
            return len(result)

        return self.dump([check_datablock(db) for db in dbs])


class VNRPNTIV(Filter):
    """make single record datablocks"""

    def process(self, sample: str) -> str:
        try:
            bs = binascii.unhexlify(sample)
        except (binascii.Error):
            return self.dump(None)
        dbs = RawDatablock.parse(Bits.from_bytes(bs))
        if isinstance(dbs, ValueError):
            return sample

        def handle_datablock(db: Any) -> str:
            cat = db.get_category()
            orig = db.unparse().to_bytes().hex()
            Spec = specs.get(cat)
            if Spec is None:
                return orig # type: ignore
            result = Spec.cv_uap.parse(db.get_raw_records())  # type: ignore
            if isinstance(result, ValueError):
                return orig # type: ignore
            dbs2 = [Spec.create([r]) for r in result] # type: ignore
            return ''.join([x.unparse().to_bytes().hex() for x in dbs2])

        return ''.join([handle_datablock(db) for db in dbs])


class CQNBMHNB(Filter):
    """asterix record item extraction to json"""

    def process(self, sample: str) -> str:
        try:
            bs = binascii.unhexlify(sample)
        except (binascii.Error):
            return self.dump(None)
        dbs = RawDatablock.parse(Bits.from_bytes(bs))
        if isinstance(dbs, ValueError):
            return self.dump(None)

        def check62(xs: Union[ValueError, List[Cat062.cv_record]]) -> Any:
            if isinstance(xs, ValueError):
                return None
            result = []
            for r in xs:
                i010 = r.get_item('010')
                i015 = r.get_item('015')
                i080 = r.get_item('080')
                iMD5 = None if i080 is None else i080.variation.get_item('MD5')
                i510 = r.get_item('510')
                i290 = r.get_item('290')
                iMDS = None if i290 is None else i290.variation.get_item('MDS')
                result.append({
                    'I062/010/SAC': None if i010 is None else
                    i010.variation.get_item('SAC').as_uint(),
                    'I062/015': i015.as_uint() if i015 is not None else None,
                    'I062/080/SRC': None if i080 is None else
                    i080.variation.get_item('SRC').as_uint(),
                    'I062/080/MD5': None if iMD5 is None else iMD5.as_uint(),
                    'I062/510/IDENT': None if i510 is None else
                    [x.get_item('IDENT').as_uint()
                     for x in i510.variation.get_list()],
                    'I062/290/MDS': None if iMDS is None else iMDS.as_uint(),
                })
            return result

        def check63(xs: Union[ValueError, List[Cat063.cv_record]]) -> Any:
            if isinstance(xs, ValueError):
                return None
            result = []
            for r in xs:
                i010 = r.get_item('010')
                result.append({
                    'I063/010/SIC': None if i010 is None else
                    i010.variation.get_item('SIC').as_uint(),
                })
            return result

        def check65(xs: Union[ValueError, List[Cat065.cv_record]]) -> Any:
            if isinstance(xs, ValueError):
                return None
            result = []
            for r in xs:
                i000 = r.get_item('000')
                result.append({
                    'I065/000': None if i000 is None else i000.as_uint(),
                })
            return result

        def check_datablock(db: Any) -> Any:
            cat = db.get_category()
            result: Any
            if cat == 62:
                result = check62(Cat062.cv_uap.parse(db.get_raw_records()))
            elif cat == 63:
                result = check63(Cat063.cv_uap.parse(db.get_raw_records()))
            elif cat == 65:
                result = check65(Cat065.cv_uap.parse(db.get_raw_records()))
            else:
                return None
            return result

        return self.dump([check_datablock(db) for db in dbs])


class RWVTCOAU(Filter):
    """asterix record construction"""

    def process(self, sample: str) -> str:
        try:
            x = json.loads(sample)
        except json.decoder.JSONDecodeError:
            return ''
        cat = x.get('cat')
        if cat is None:
            return ''

        r: Any
        db: Any
        if cat == 62:
            r = Cat062.cv_record.create({})
            i010 = x.get('010')
            i040 = x.get('040')
            iPSR = x.get('290/PSR')
            i510 = x.get('510')
            iBDS = x.get('380/BDSDATA')

            if i010 is not None:
                if not isinstance(i010, int):
                    return ''
                r = r.set_item('010', i010)

            if i040 is not None:
                if not isinstance(i040, int):
                    return ''
                r = r.set_item('040', i040)

            if iPSR is not None:
                if not isinstance(iPSR, int):
                    return ''
                r = r.set_item('290', {'PSR': iPSR})

            if i510 is not None:
                if not isinstance(i510, list):
                    return ''
                y = []
                for x in i510:
                    if not isinstance(x, dict): return ''
                    iIDENT = x.get('IDENT')
                    iTRACK = x.get('TRACK')
                    if not isinstance(iIDENT, int): return ''
                    if not isinstance(iTRACK, int): return ''
                    if not isinstance(x.get('TRACK'), int): return ''
                    y.append((('IDENT', iIDENT), ('TRACK', iTRACK)))
                r = r.set_item('510', y)

            if iBDS is not None:
                if not isinstance(iBDS, list):
                    return ''
                if not all([isinstance(x, int) for x in iBDS]):
                    return ''
                r = r.set_item('380', {'BDSDATA': iBDS})

            db = Cat062.create([r])

        elif cat == 63:
            r = Cat063.cv_record.create({})
            i010 = x.get('010')
            i015 = x.get('015')

            if i010 is not None:
                if not isinstance(i010, int):
                    return ''
                r = r.set_item('010', i010)

            if i015 is not None:
                if not isinstance(i015, int):
                    return ''
                r = r.set_item('015', i015)

            db = Cat063.create([r])

        elif cat == 65:
            r = Cat065.cv_record.create({})
            i010 = x.get('010')
            i020 = x.get('020')

            if i010 is not None:
                if not isinstance(i010, int):
                    return ''
                r = r.set_item('010', i010)

            if i020 is not None:
                if not isinstance(i020, int):
                    return ''
                r = r.set_item('020', i020)

            db = Cat065.create([r])

        else:
            return ''

        return db.unparse().to_bytes().hex()  # type: ignore


class AYTIGDAT(Filter):
    """spare bits abuse detection"""

    def process(self, sample: str) -> str:
        try:
            bs = binascii.unhexlify(sample)
        except (binascii.Error):
            return self.dump(False)

        def check_item(i: Any) -> bool:
            if not isinstance(i, Spare):
                return False
            return not i.as_uint() == 0

        def check_mitem(i: Any) -> bool:
            if i is None:
                return False
            return check_item(i)

        def check_variation(var: Any) -> bool:
            if isinstance(var, Element):
                return False
            elif isinstance(var, Group):
                return any([check_item(i) for i in var.arg])
            elif isinstance(var, Extended):
                def check_ext_group(g: Any) -> bool:
                    return any([check_mitem(i) for i in g])
                return any([check_ext_group(g) for g in var.arg])
            elif isinstance(var, Repetitive):
                return any([check_variation(v) for v in var.arg])
            elif isinstance(var, Explicit):
                return False
            elif isinstance(var, Compound):
                return any([check_nsp(n) for n in var.arg.values()])
            else:
                raise Exception('unexpected subclass', var)

        def check_nsp(nsp: Any) -> bool:
            return check_variation(nsp.variation)

        def check_record(r: Any) -> bool:
            return any([check_nsp(nsp)
                       for (name, nsp) in r.items_regular.items()])

        def check_datablock(db: Any) -> bool:
            cat = db.get_category()
            Spec = specs.get(cat)
            if Spec is None:
                return False
            result = Spec.cv_uap.parse(db.get_raw_records())  # type: ignore
            if isinstance(result, ValueError):
                return False
            return any([check_record(r) for r in result])

        def check_sample(sample: bytes) -> bool:
            dbs = RawDatablock.parse(Bits.from_bytes(bs))
            if isinstance(dbs, ValueError):
                return False
            return any([check_datablock(db) for db in dbs])

        return self.dump(check_sample(bs))


class RKMIVFTJ(Filter):
    """conversion to 'quantity"""

    def process(self, sample: str) -> str:
        try:
            bs = binascii.unhexlify(sample)
        except (binascii.Error):
            return self.dump([])

        def check_record(r: Cat062.cv_record) -> List[float]:
            i070 = r.get_item('070')
            if i070 is None:
                return []
            return [i070.variation.content.as_quantity('s')]

        def check_datablock(db: Any) -> List[float]:
            cat = db.get_category()
            if cat != Cat062.cv_category:
                return []
            result = Cat062.cv_uap.parse(db.get_raw_records())
            if isinstance(result, ValueError):
                return []
            return sum([check_record(r) for r in result], [])

        def check_sample(sample: bytes) -> List[float]:
            dbs = RawDatablock.parse(Bits.from_bytes(bs))
            if isinstance(dbs, ValueError):
                return []
            return sum([check_datablock(db) for db in dbs], [])

        results = ['{:.3f}'.format(x) for x in check_sample(bs)]
        return self.dump(results)

class BIQUTYDD(Filter):
    """conversion from 'quantity'"""

    def process(self, sample: str) -> str:
        try:
            lst = json.loads(sample)
        except json.decoder.JSONDecodeError:
            return ''
        if not isinstance(lst, list):
            return ''
        for item in lst:
            if not isinstance(item, float):
                return ''

        def mk_record(val: float) -> Cat062.cv_record:
            return Cat062.cv_record.create({
                '010': 0x1234,
                '070': (val, 's'),
            })
        db = Cat062.create([mk_record(val) for val in lst])
        return db.unparse().to_bytes().hex()

class KUPKVSJU(Filter):
    """conversion to 'string'"""

    def process(self, sample: str) -> str:
        try:
            bs = binascii.unhexlify(sample)
        except (binascii.Error):
            return self.dump([])

        def check_record(r: Cat062.cv_record) -> List[str]:
            results: List[str] = []

            i060 = r.get_item('060')
            i380 = r.get_item('380')
            i390 = r.get_item('390')

            if i060 is not None:
                m3a = i060.variation.get_item('MODE3A')
                results.append(m3a.variation.content.as_string())

            if i380 is not None:
                iID = i380.variation.get_item('ID')
                if iID is not None:
                    results.append(iID.variation.content.as_string())

            if i390 is not None:
                iCS = i390.variation.get_item('CS')
                if iCS is not None:
                    results.append(iCS.variation.content.as_string())

            return results

        def check_datablock(db: Any) -> List[str]:
            cat = db.get_category()
            if cat != Cat062.cv_category:
                return []
            result = Cat062.cv_uap.parse(db.get_raw_records())
            if isinstance(result, ValueError):
                return []
            return sum([check_record(r) for r in result], [])

        def check_sample(sample: bytes) -> List[str]:
            dbs = RawDatablock.parse(Bits.from_bytes(bs))
            if isinstance(dbs, ValueError):
                return []
            return sum([check_datablock(db) for db in dbs], [])

        return self.dump(check_sample(bs))

solutions = { Cls.__name__: Cls() for Cls in Filter.__subclasses__() }

def cmd_show_manifest(args: Any) -> None:
    for name in solutions:
        print(name)


def cmd_run(args: Any) -> None:
    obj = solutions.get(args.ident)
    if obj is None:
        print(args.ident + " not implemented!")
        sys.exit(1)

    try:
        obj.run()
    except KeyboardInterrupt:
        pass


# main
parser = argparse.ArgumentParser(prog='Asterix challenges implementation')
subparsers = parser.add_subparsers(required=True)

parser_manifest = subparsers.add_parser('manifest',
                                        help='show implemented challenges')
parser_manifest.set_defaults(func=cmd_show_manifest)

parser_run = subparsers.add_parser('run',
                                   help='run challenge')
parser_run.set_defaults(func=cmd_run)
parser_run.add_argument('ident')

args = parser.parse_args()
args.func(args)

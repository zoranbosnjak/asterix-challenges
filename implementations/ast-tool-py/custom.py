# file: custom.py

def example02(base, gen, io, args):
    cnt = 0
    for event in io.rx():
        (t_mono, t_utc, channel, data) = event
        bits = base.Bits.from_bytes(data)
        raw_datablocks = base.RawDatablock.parse(bits)
        if not isinstance(raw_datablocks, ValueError):
            cnt += 1
    print(cnt)

def example03(base, gen, io, args):
    cnt = 0
    for event in io.rx():
        (t_mono, t_utc, channel, data) = event
        bits = base.Bits.from_bytes(data)
        raw_datablocks = base.RawDatablock.parse(bits)
        if not isinstance(raw_datablocks, ValueError):
            cnt += len(raw_datablocks)
    print(cnt)

def append(acc, rec, *names):
    i = rec
    for name in names:
        i = i.get_item(name)
        if i is None: return
        i = i.variation
    acc.bump(i.as_uint())

def hander048(acc, rec):
    append(acc, rec, '010', 'SAC')

def hander062(acc, rec):
    append(acc, rec, '015')
    append(acc, rec, '010', 'SIC')
    append(acc, rec, '080', 'SRC')
    append(acc, rec, '080', 'MD5')
    i510 = rec.get_item('510')
    if i510 is not None:
        for i in i510.variation.get_list():
            acc.bump(i.get_item('IDENT').as_uint())
    append(acc, rec, '290', 'MDS')

def handle_datablocks(acc, raw_datablocks, d):
    for raw_db in raw_datablocks:
        cat = raw_db.get_category()
        lookup = d.get(cat)
        if lookup is None: continue
        Spec, handler = lookup
        records = Spec.cv_uap.parse(raw_db.get_raw_records())
        if isinstance(records, ValueError): continue
        for rec in records:
            handler(acc, rec)

class Word8:
    def __init__(self): self.val = 0
    def bump(self, val): self.val = (self.val + val) % 256

def example06(base, gen, io, args):
    Cat048 = gen.Cat_048_1_32
    Cat062 = gen.Cat_062_1_21
    acc = Word8()
    for event in io.rx():
        (t_mono, t_utc, channel, data) = event
        bits = base.Bits.from_bytes(data)
        raw_datablocks = base.RawDatablock.parse(bits)
        if isinstance(raw_datablocks, ValueError): continue
        handle_datablocks(acc, raw_datablocks, {
            48: (Cat048, hander048),
            62: (Cat062, hander062),
        })
    print(acc.val)


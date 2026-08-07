#!/usr/bin/env python3

from typing import *
import json
import sys
import argparse
import fileinput
import subprocess
import datetime
import random
import string
import gc


class RandomGenerator:
    def __init__(self, seed: Optional[int], error: Optional[float]):
        self.seed = seed
        self.error = error
        self.on_init()

    def on_init(self) -> None:
        self.rap = self.random_asterix_process()

    def sample(self) -> str:
        return ''

    def __iter__(self) -> Any:
        while True:
            yield self.sample()

    def random_string(self) -> str:
        characters = string.ascii_letters + string.digits
        n = random.randint(0, 40)
        return ''.join(random.choices(characters, k=n))

    def random_bytes(self) -> str:
        if self.error is not None:
            p = random.random()
            if p < self.error:
                return self.random_string()
        n = random.randint(0, 40)
        x = random.randbytes(n)
        return x.hex()

    def random_int(self) -> str:
        if self.error is not None:
            p = random.random()
            if p < self.error:
                return self.random_string()
        n = random.randint(0, 40)
        return str(n)

    def random_asterix_process(self,
            category_selection: Optional[List[Tuple[int, str]]]=None) -> Any:
        cmd = 'ast-tool-py --simple-output'
        if category_selection is not None:
            cmd += ' --empty-selection'
            for (cat, ed) in category_selection:
                cmd += ' --cat {} {}'.format(cat, ed)
        cmd += ' random'
        if self.seed is not None:
            cmd += ' --seed ' + str(self.seed)
        if self.error is not None:
            cmd += ' --error-bit-flip ' + str(round(1.0 / self.error))
        return subprocess.Popen(cmd, shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL)

    def random_asterix(self) -> str:
        status = self.rap.poll()
        if status is not None:
            print('Asterix generator terminated')
            print('To reproduce, use seed value:', self.seed)
            sys.exit(1)
        line = self.rap.stdout.readline()
        return line.decode('utf-8')  # type: ignore

    def random_bool(self, probability: float) -> bool:
        val = random.random()
        return val <= probability


class WJLXIXEB(RandomGenerator):
    """identity filter"""
    def sample(self) -> str:
        return self.random_bytes()


class TXHWAQHG(RandomGenerator):
    """determine length of input"""
    def sample(self) -> str:
        return self.random_bytes()


class GCMEDPFW(RandomGenerator):
    """encode constant datagram"""
    def sample(self) -> str:
        return self.random_int()


class CAOXOESE(RandomGenerator):
    """decode first level of asterix"""
    def sample(self) -> str:
        return self.random_asterix()


class JWOONFHI(RandomGenerator):
    """encode first level of asterix"""
    def sample(self) -> str:
        if self.error is not None:
            p = random.random()
            if p < self.error:
                return self.random_string()
        result = []
        for i in range(random.randint(0, 5)):
            cat = random.randint(0, 300)
            ln = random.randint(0, 200)
            result.append([cat, ln])
        return json.dumps(result)


class FCYKLBBQ(RandomGenerator):
    """reverse datablocks"""
    def sample(self) -> str:
        return self.random_asterix()


class MVQCOXZJ(RandomGenerator):
    """full asterix record decoding, count records"""
    def on_init(self) -> None:
        self.rap = self.random_asterix_process([
            (62, '1.21'),
            (63, '1.7'),
            (65, '1.6'),
        ])

    def sample(self) -> str:
        return self.random_asterix()

class VNRPNTIV(RandomGenerator):
    """make single record datablocks"""
    def on_init(self) -> None:
        self.rap = self.random_asterix_process([
            (62, '1.21'),
            (63, '1.7'),
            (65, '1.6'),
        ])

    def sample(self) -> str:
        return self.random_asterix()

class CQNBMHNB(RandomGenerator):
    """asterix record item extraction to json"""
    def on_init(self) -> None:
        self.rap = self.random_asterix_process([
            (62, '1.21'),
            (63, '1.7'),
            (65, '1.6'),
        ])

    def sample(self) -> str:
        return self.random_asterix()


class RWVTCOAU(RandomGenerator):
    """asterix record construction"""
    def sample(self) -> str:
        cat = random.choice([62, 63, 65])
        result = {
            'cat': cat,
        }
        if cat == 62:
            if self.random_bool(0.5):
                result['010'] = random.randint(0, 0xffff)
            if self.random_bool(0.5):
                result['040'] = random.randint(0, 0xffff)
            if self.random_bool(0.5):
                result['290/PSR'] = random.randint(0, 0xff)
            if self.random_bool(0.5):
                val = []
                for i in range(random.randint(1, 5)):
                    val.append({
                        'IDENT': random.randint(0, pow(2, 8)),
                        'TRACK': random.randint(0, pow(2, 15)),
                    })
                result['510'] = val  # type: ignore
            if self.random_bool(0.5):
                val = []
                for i in range(random.randint(1, 5)):
                    val.append(random.randint(0, pow(2, 23))) # type: ignore
                result['380/BDSDATA'] = val  # type: ignore
        elif cat == 63:
            if self.random_bool(0.5):
                result['010'] = random.randint(0, 0xffff)
            if self.random_bool(0.5):
                result['015'] = random.randint(0, 0xff)
        elif cat == 65:
            if self.random_bool(0.5):
                result['010'] = random.randint(0, 0xffff)
            if self.random_bool(0.5):
                result['020'] = random.randint(0, 0xff)
        else:
            raise ValueError('Unexpected cat')
        return json.dumps(result)


class AYTIGDAT(RandomGenerator):
    """spare bits abuse detection"""
    def on_init(self) -> None:
        self.rap = self.random_asterix_process([
            (62, '1.21'),
            (63, '1.7'),
            (65, '1.6'),
        ])

    def sample(self) -> str:
        return self.random_asterix()

class RKMIVFTJ(RandomGenerator):
    """conversion to 'quantity'"""
    def on_init(self) -> None:
        self.rap = self.random_asterix_process([
            (62, '1.21'),
        ])

    def sample(self) -> str:
        return self.random_asterix()

class BIQUTYDD(RandomGenerator):
    """conversion from 'quantity'"""

    def sample(self) -> str:
        result: List[float] = []
        for i in range(random.randint(0, 5)):
            result.append(round(random.random()*100+1, 2))
        return json.dumps(result)

class _KUPKVSJU(RandomGenerator):
    """conversion to 'string'"""
    def on_init(self) -> None:
        self.rap = self.random_asterix_process([
            (62, '1.21'),
        ])

    def sample(self) -> str:
        return self.random_asterix()

class Implementation:
    def __init__(self, challenge: Optional[str], cmd: str) -> None:
        self.cmd = cmd if challenge is None else cmd + ' ' + challenge
        self.p = subprocess.Popen(self.cmd, shell=True,
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL)
        self.accumulated_time = 0.0

        # Send empty string and wait for the first result.
        # This is to wait and ignore initialization time and make sure that
        # the implementation is ready to process packages
        self.p.stdin.write('\n'.encode('utf-8'))  # type: ignore
        self.p.stdin.flush()  # type: ignore
        self.p.stdout.readline()  # type: ignore

    def __del__(self) -> None:
        self.p.kill()

    def call(self, seed: int, sample: str) -> Tuple[bytes, datetime.timedelta]:
        status = self.p.poll()
        if status is not None:
            print('Process terminated:', self.cmd)
            print('To reproduce, use seed value:', seed)
            sys.exit(1)
        x = (sample + '\n').encode('utf-8')
        encoded = (sample + '\n').encode('utf-8')
        self.p.stdin.write(encoded)  # type: ignore
        self.p.stdin.flush()  # type: ignore
        t1 = datetime.datetime.now()
        result = self.p.stdout.readline()  # type: ignore
        t2 = datetime.datetime.now()
        dt = t2 - t1
        self.accumulated_time += dt.total_seconds()
        return (result, dt)


def check_sample(seed: int,
                 implementations: List[Implementation],
                 sample: str) -> List[datetime.timedelta]:
    results = []
    time_required = []
    for i in implementations:
        (result, dt) = i.call(seed, sample)
        results.append(result)
        time_required.append(dt)
    if len(set(results)) != 1:
        print()
        print('Error!')
        print('To reproduce, use seed value:', seed)
        print('Different results on input sample:')
        print(repr(sample))
        print('Got:')
        for r in results:
            print('  - {}'.format(repr(r.decode('utf-8').rstrip())))
        sys.exit(1)
    return time_required

all_challenges = {Cls.__name__: Cls for Cls in RandomGenerator.__subclasses__() \
    if Cls.__name__[0] != '_' }

def cmd_show_manifest(seed: Any, args: Any) -> None:
    for name in all_challenges:
        Cls = all_challenges[name]
        out = name
        if Cls.__doc__ is not None:
            out += ' - ' + Cls.__doc__.splitlines()[0]
        print(out)

def cmd_samples(seed: int, args: Any) -> None:
    name = args.challenge
    Rnd = all_challenges.get(name)
    if Rnd is None:
        print('Random generator for', name, 'is not defined')
        print('To reproduce, use seed value:', seed)
        sys.exit(1)
    rnd = Rnd(seed, args.error)
    for line in rnd:
        print(line.strip())

def cmd_run(seed: int, args: Any) -> None:
    name = args.challenge
    Rnd = all_challenges.get(name)
    if Rnd is None:
        print('Random generator for', name, 'is not defined')
        print('To reproduce, use seed value:', seed)
        sys.exit(1)
    cnt = 0
    append_challenge = name if args.append_challenge else None
    implementations = [Implementation(append_challenge, i) for i in args.impl]

    rnd = Rnd(seed, args.error)
    try:
        for line in rnd:
            line = line.strip()
            if implementations:
                time_required = check_sample(seed, implementations, line)
                cnt += 1
                if args.print_progress:
                    s = ['{:.6f}'.format(dt.total_seconds())
                         for dt in time_required]
                    print(cnt, s)
                if args.samples is not None:
                    if cnt >= args.samples:
                        break
            else:
                print(line)
    except KeyboardInterrupt:
        pass

    print('done... {} samples'.format(cnt))
    print('Time required per implementation:')
    for i in implementations:
        print('{:.6f}s'.format(i.accumulated_time))

def cmd_autorun(seed: int, args: Any) -> None:
    names = args.challenges
    if not names:
        names = list(all_challenges.keys())
    try:
        challenges= {name: all_challenges[name] for name in names}
    except KeyError:
        print('Challenge not implemented!')
        print('To reproduce, use seed value:', seed)
        sys.exit(1)

    if not args.impl:
        print('Some implementation argument is required')
        print('To reproduce, use seed value:', seed)
        sys.exit(1)

    while True:
        name = random.choice(list(challenges.keys()))
        Rnd = challenges[name]
        rnd = Rnd(seed, args.error)
        t = datetime.datetime.now()
        print(t, 'running:', name)
        # forget about previous run and force deleting objects
        implementations = []
        gc.collect()
        implementations = [Implementation(name, i) for i in args.impl]
        for i in range(args.samples):
            line = rnd.sample().strip()
            time_required = check_sample(seed, implementations, line)
            if args.print_progress:
                s = ['{:.6f}'.format(dt.total_seconds())
                     for dt in time_required]
                print(i+1, s)

parser = argparse.ArgumentParser(prog='asterix-challange-runner')

parser.add_argument('--seed', help='Random generator seed value',
                    metavar='INT', type=int)
parser.add_argument('-p', '--print-progress', action='store_true',
                    help='Print some output on each sample')
parser.add_argument('-e', '--error',
                    help='Sample generator error ratio 0.0 - 1.0',
                    type=float, metavar='ERROR')
parser.add_argument('-i', '--impl', action='append', default=[],
                    help='Implementation(s) to run')

subparsers = parser.add_subparsers(required=True)

parser_manifest = subparsers.add_parser('manifest',
                                        help='show supported challenges')
parser_manifest.set_defaults(func=cmd_show_manifest)

parser_samples = subparsers.add_parser('samples',
                                        help='generate samples')
parser_samples.set_defaults(func=cmd_samples)
parser_samples.add_argument('challenge', help='Challenge ID')

parser_run = subparsers.add_parser('run', help='run selected challenge')
parser_run.set_defaults(func=cmd_run)
parser_run.add_argument('challenge', help='Challenge ID')
parser_run.add_argument('-c', '--append-challenge',
                    help='Pass challenge identifier to each implementation',
                    action='store_true')
parser_run.add_argument('-n', '--samples', type=int,
    metavar='INT',
    help='Stop after number of samples')

parser_autorun = subparsers.add_parser('autorun',
                                        help='cycle between set of tests')
parser_autorun.set_defaults(func=cmd_autorun)
parser_autorun.add_argument('challenges', nargs='*', default=[],
    help='challenge selection or all if not spcified')
parser_autorun.add_argument('-n', '--samples', type=int, default=100_000,
    metavar='INT',
    help='Number of samples, before switching to the next test (default: %(default)s)')

args = parser.parse_args()

seed = random.randrange(sys.maxsize) if args.seed is None else args.seed
random.seed(seed)

try:
    args.func(seed, args)
except (BrokenPipeError, KeyboardInterrupt):
    sys.exit(0)


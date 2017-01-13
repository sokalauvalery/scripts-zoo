import os
import errno
import argparse


def get_tail(file, n, bsize=2048):
    with open(file, 'rU') as f:
        if not f.readline():
            return
        sep = f.newlines
        assert isinstance(sep, str), 'multiple newline types found, aborting'

    with open(file, 'rb') as f:
        f.seek(0, os.SEEK_END)
        line_count = 0
        pos = 0

        while line_count <= n + 1:
            try:
                f.seek(-bsize, os.SEEK_CUR)
                line_count += f.read(bsize).count(sep.encode())
                f.seek(-bsize, os.SEEK_CUR)
            except IOError as e:
                if e.errno == errno.EINVAL:
                    bsize = f.tell()
                    f.seek(0, os.SEEK_SET)
                    line_count += f.read(bsize).count(sep.encode())
                    break
                raise
            pos = f.tell()

    with open(file, 'r') as hfile:
        hfile.seek(pos, os.SEEK_SET)
        for line in hfile:
            if line_count > n:
                line_count -= 1
                continue
            yield line


def run():
    SCRIPT_DESCRIPTION = 'Print the last 10 lines of each FILE to standard output. ' \
                         'With more than one FILE, precede each with a header giving the file name.'
    parser = argparse.ArgumentParser(description=SCRIPT_DESCRIPTION)
    parser.add_argument('files', metavar='[FILE]', type=str, nargs='+', help='One or more files')
    parser.add_argument('-n', type=int, default=10,
                        help='output the last NUM lines, instead of the last 10')
    parser.add_argument('-q', default=False, action='store_true',
                        help='never output headers giving file names')
    args = parser.parse_args()
    for file in args.files:
        if len(args.files) > 1 and not args.q:
            print('==>{}<=='.format(file))
        for line in get_tail(file, args.n):
            print(line, end="")
    pass


if __name__ == '__main__':
    run()
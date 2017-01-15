import os
import errno
import argparse
import asyncio

SCRIPT_DESCRIPTION = 'Print the last 10 lines of each FILE to standard output. ' \
                     'With more than one FILE, precede each with a header giving the file name.'
HELP_STRING = {
    'files': 'One or more files',
    'n': 'output the last NUM lines, instead of the last 10',
    'q': 'never output headers giving file names',
    'f': 'output appended data as the file grows'
}


class TailScriptException(Exception):
    pass


class Tail:
    default_lines_count = 10

    def __init__(self, files, n=10, quiet=False, bsize=2048, follow=False):
        self.n = n if n is not None else self.default_lines_count
        self.files = files
        self.print_file_name = len(self.files) > 1 and not quiet
        self.loop = asyncio.get_event_loop()
        self.bsize = bsize
        self.follow = follow

    def printer(self):
        raise NotImplemented

    def exception_hander(self, exception):
        raise NotImplemented

    def tail_file(self, file, target):
        try:
            with open(file, 'rU') as f:
                if not f.readline():
                    return
                sep = f.newlines
                assert isinstance(sep, str), 'multiple newline types found, cannot tail file with multiple newline types'

            with open(file, 'rb') as f:
                f.seek(0, os.SEEK_END)
                line_count = 0
                pos = 0

                while line_count <= self.n + 1:
                    try:
                        f.seek(-self.bsize, os.SEEK_CUR)
                        line_count += f.read(self.bsize).count(sep.encode())
                        f.seek(-self.bsize, os.SEEK_CUR)
                    except IOError as e:
                        if e.errno == errno.EINVAL:
                            bsize = f.tell()
                            f.seek(0, os.SEEK_SET)
                            line_count += f.read(bsize).count(sep.encode())
                            break
                        raise
                    pos = f.tell()

            target.send(None)
            with open(file, 'r') as f:
                f.seek(pos, os.SEEK_SET)
                file_name = file
                for line in f:
                    if line_count > self.n:
                        line_count -= 1
                        continue
                    target.send((file_name, line))
                    file_name = None

                if self.follow:
                    while True:
                        line = f.readline()
                        if line:
                            target.send((file, line))
                        yield from asyncio.sleep(0.1)

        except FileNotFoundError:
            self.exception_hander(TailScriptException("No such file {}".format(file)))
        except UnicodeDecodeError:
            self.exception_hander(TailScriptException("Unable to  decode file with utf-8 encoding."))

    def run(self):
        if not isinstance(self.n, int):
            raise TailScriptException('Number of lines should be positive integer')
        tasks = asyncio.gather(*[asyncio.ensure_future(self.tail_file(file, target=self.printer())) for file in
                                                       self.files])
        self.loop.run_until_complete(tasks)


class StdoutTail(Tail):
    def printer(self):
        while True:
            file_name, line = (yield)
            if self.print_file_name and file_name:
                print('==>{}<=='.format(file_name))
            print(line.rstrip(), end="\n")

    def exception_hander(self, exception):
        print('DEBUG !!!!!!!!!!!!')
        print(str(exception))
        # TODO: we can comment re-raising exception if we don't want to see traces in output
        raise exception


def run():
    parser = argparse.ArgumentParser(description=SCRIPT_DESCRIPTION)
    parser.add_argument('files', metavar='[FILE]', type=str, nargs='+', help=HELP_STRING['files'])
    parser.add_argument('-n', type=int, default=10, help=HELP_STRING['n'])
    parser.add_argument('-q', default=False, action='store_true', help=HELP_STRING['q'])
    parser.add_argument('-f', default=False, action='store_true', help=HELP_STRING['f'])
    args = parser.parse_args()
    tail = StdoutTail(args.files, follow=args.f, quiet=args.q)
    tail.run()


if __name__ == '__main__':
    run()
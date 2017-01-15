from behave import *
from random import choice
from pytail.tests.features.environment import TMP_DIR, FILE_NAME_BACKLIGHT
import string
import os
import contextlib
from io import StringIO
from pytail.tail import StdoutTail
from pytail.tail import TailScriptException


def get_last_lines(path, n):
    with open(path, 'r') as f:
        expected_lines = [line.rstrip() for line in f.readlines()[-n:]] if n else []
        return expected_lines


def tail_test(file, expected_count, n=None):
    try:
        n = int(n) if n else n
    except ValueError:
        n = n
    path = os.path.join(TMP_DIR, file)
    expected_count = int(expected_count)
    temp_stdout = StringIO()
    with contextlib.redirect_stdout(temp_stdout):
        StdoutTail([path], n=n).run()
    output = [line for line in temp_stdout.getvalue().strip().split('\n') if line]
    output_lines_count = len(output)
    assert output_lines_count == expected_count, 'Got unexpected lines count. ' \
                                     'Expected {ec}, actual {ac}'.format(ec=expected_count, ac=output_lines_count)
    expected_lines = get_last_lines(path, expected_count)
    assert output == expected_lines, 'Returned lines are different from expected. \n' \
                                         'Expected << {e} >> \n\n Actual << {a} >>'.format(e=expected_lines, a=output)


@given('Generate "{name}" text file of "{n}" lines')
def step_impl(context, name, n):
    n = int(n)
    with open(os.path.join(TMP_DIR, name), 'w') as f:
        for i in range(n):
            random = ''.join([choice(string.ascii_letters + string.digits + string.punctuation) for n in range(100)])
            f.write(random + '\n')


@given('Generate "{name}" binary file')
def step_impl(context, name):
    context.path = os.path.join(TMP_DIR, name)
    n = 100
    with open(context.path, 'wb') as f:
        for i in range(n):
            f.write(os.urandom(1024))


@then('Tail "{file}" "{n}" lines returns "{expected_count}" lines from given file')
def step_impl(context, file, n, expected_count):
    tail_test(file, expected_count=expected_count, n=n)


@then('Tail "{file}" returns "{expected_count}" lines from given file')
def step_impl(context, file, expected_count):
    tail_test(file, expected_count=expected_count, n=None)


@then('Tail "{file}" "{n}" lines returns "{message}" exception message')
def step_impl(context, file, n, message):
    try:
        tail_test(file, expected_count=0, n=n)
    except TailScriptException as e:
        assert str(e) == message, 'incorrect exception message. \n Expected: \n << {e} >> \n Actual: \n {a}'.format(
            e=message, a=str(e))


@then('Tail nonexistent file "{path}" return exception "{message}"')
def step_impl(context, path, message):
    context.path = path
    try:
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            StdoutTail([context.path]).run()
    except TailScriptException as e:
        assert str(e) == message, 'incorrect exception message. \n Expected: \n << {e} >> \n Actual: \n {a}'.format(
            e=message, a=str(e))


def multi_line_tail_test(files, n=None, q=False):
    try:
        n = int(n) if n else n
    except ValueError:
        n = n
    files = files.split(',') if ',' in files else [files]
    files = [os.path.join(TMP_DIR, file.strip()) for file in files]
    temp_stdout = StringIO()
    with contextlib.redirect_stdout(temp_stdout):
        StdoutTail(files, n=n, quiet=q).run()
    with open(os.path.join(TMP_DIR, 'stdout.ouput'), 'w') as f:
        f.write(temp_stdout.getvalue().strip())


@when('Run tail command for files "{files}" with default parameters')
def step_impl(context, files):
    multi_line_tail_test(files)


@when('Tail "{n}" lines for files "{files}" with default parameters')
def step_impl(context, n, files):
    multi_line_tail_test(files, n=int(n))


@then('Output contains filename and last "{n}" lines from "{file}" file')
def step_impl(context, n, file):
    with open(os.path.join(TMP_DIR, 'stdout.ouput'), 'r') as f:
        output = f.readlines()
    expected_lines = get_last_lines(os.path.join(TMP_DIR, file), int(n))
    assert file in '\n'.join(output), 'Missing file name in output. {}'.format(file)
    file_lines_in_output = []
    file_name_from_output = None

    for line in output:
        if file in line:
            file_name_from_output = line
            continue
        if file_name_from_output and FILE_NAME_BACKLIGHT in line:
            break
        if file_name_from_output:
            file_lines_in_output.append(line.rstrip('\n'))
    assert expected_lines == file_lines_in_output, 'Returned lines are different from expected. \n' \
                                         'Expected << {e} >> \n\n Actual << {a} >>'.format(e=expected_lines, a=file_lines_in_output)


@then('Output contains last "{n}" lines from "{file}" file and no file names')
def step_impl(context, n, file):
    with open(os.path.join(TMP_DIR, 'stdout.ouput'), 'r') as f:
        output = f.readlines()
    expected_lines = get_last_lines(os.path.join(TMP_DIR, file), int(n))
    assert file not in '\n'.join(output), 'File name in output when quiet mode is true.'
    i = 0
    for line in output:
        if line.rstrip('\n') == expected_lines[i]:
            i += 1
        if i == len(expected_lines) - 1:
            break
    assert i == len(expected_lines)-1, 'Returned lines are different from expected. \n' \
                                         'Expected << {e} >> \n\n Actual << {a} >>'.format(e=expected_lines, a=output)


@when('Tail "{n}" lines for files "{files}" with quiet mode')
def step_impl(context, files, n):
    multi_line_tail_test(files, n=int(n), q=True)

from behave import *
from random import choice
from pytail.tests.features.environment import TMP_DIR
import string
import os
import contextlib
from io import StringIO
from pytail.tail import StdoutTail
from pytail.tail import TailScriptException


def tail_test(context, expected_count, n=None):
    expected_count = int(expected_count)
    temp_stdout = StringIO()
    with contextlib.redirect_stdout(temp_stdout):
        StdoutTail([context.path], n=n).run()
    output = [line for line in temp_stdout.getvalue().strip().split('\n') if line]
    output_lines_count = len(output)
    assert output_lines_count == expected_count, 'Got unexpected lines count. ' \
                                     'Expected {ec}, actual {ac}'.format(ec=expected_count, ac=output_lines_count)
    with open(context.path, 'r') as f:
        expected_lines = [line.rstrip() for line in f.readlines()[-expected_count:]] if expected_count else []
        assert output == expected_lines, 'Returned lines are different from expected. \n' \
                                         'Expected << {e} >> \n\n Actual << {a} >>'.format(e=expected_lines, a=output)


@given('Generate text file of "{n}" lines')
def step_impl(context, n):
    context.path = os.path.join(TMP_DIR, 'text_file.txt')
    n = int(n)
    with open(os.path.join(TMP_DIR, 'text_file.txt'), 'w') as f:
        for i in range(n):
            random = ''.join([choice(string.ascii_letters + string.digits + string.punctuation) for n in range(100)])
            f.write(random + '\n')


@then('Tail "{n}" lines returns "{expected_count}" lines from given file')
def step_impl(context, n, expected_count):
    try:
        n = int(n)
    except ValueError:
        n = n

    tail_test(context, expected_count=expected_count, n=n)


@then('Tail returns "{expected_count}" lines from given file')
def step_impl(context, expected_count):
    tail_test(context, expected_count=expected_count, n=None)


@then('Tail "{n}" lines returns "{message}" exception message')
def step_impl(context, n, message):
    try:
        tail_test(context, expected_count=0, n=n)
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
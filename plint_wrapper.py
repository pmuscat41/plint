"""Utilities for running ``plint.py`` on a string input.

This module exposes :func:`main` which mimics ``plint.py`` but operates on a
string containing the claims.  No temporary files are created; the claims file
expected by ``plint.py`` is simulated using ``io.StringIO`` and monkeypatching
``open`` and ``os.path.isfile``.
"""

import io
import os
import runpy
import sys
from contextlib import redirect_stdout, redirect_stderr
from unittest import mock


def main(claims_text, *plint_args):
    """Run ``plint.py`` on the provided claims text and return its output."""

    plint_path = os.path.join(os.path.dirname(__file__), 'plint.py')
    fake_claims = os.path.join(os.path.dirname(plint_path), '_claims.txt')

    argv = [plint_path, fake_claims]
    if plint_args:
        argv.extend(plint_args)

    out_buf = io.StringIO()
    err_buf = io.StringIO()

    real_open = open
    real_isfile = os.path.isfile

    def patched_open(path, mode='r', *args, **kwargs):
        if os.path.abspath(path) == os.path.abspath(fake_claims):
            if 'r' in mode:
                return io.StringIO(claims_text)
            else:
                return io.StringIO()  # discard writes
        if os.path.abspath(path) == os.path.abspath(fake_claims + '.marked'):
            return io.StringIO()
        return real_open(path, mode, *args, **kwargs)

    def patched_isfile(path):
        if os.path.abspath(path) == os.path.abspath(fake_claims) or \
           os.path.abspath(path) == os.path.abspath(fake_claims + '.marked'):
            return True
        return real_isfile(path)

    with mock.patch('sys.argv', argv), \
         mock.patch('builtins.open', side_effect=patched_open), \
         mock.patch('os.path.isfile', side_effect=patched_isfile), \
         redirect_stdout(out_buf), redirect_stderr(err_buf):
        try:
            runpy.run_path(plint_path, run_name='__main__')
        except SystemExit:
            # plint.py calls sys.exit() on some errors; capture and continue
            pass

    return out_buf.getvalue() + err_buf.getvalue()


if __name__ == '__main__':
    input_text = sys.stdin.read()
    output_text = main(input_text)
    print(output_text)

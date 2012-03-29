#!/usr/bin/env python

# Based on Yipit's git pre-commit hook:
# http://tech.yipit.com/2011/11/16/183772396/
#
# Does not interact with Git repository; simply runs checks

import os
import re
import subprocess
import sys

DEFAULT_CHECKS = [
        {
            'output': 'Checking for pdbs...',
            'command': 'grep -n "import pdb" %s',
            'ignore_files': ['.*pre-commit'],
            'print_filename': True,
            },
        {
            'output': 'Checking for ipdbs...',
            'command': 'grep -n "import ipdb" %s',
            'ignore_files': ['.*pre-commit'],
            'print_filename': True,
            },
        {
            'output': 'Checking for print statements...',
            'command': 'grep -n print %s',
            'match_files': ['.*\.py$'],
            'ignore_files': ['.*migrations.*', '.*management/commands.*', '.*manage.py', '.*/scripts/.*'],
            'print_filename': True,
            },
        {
            'output': 'Checking for console.log()...',
            'command': 'grep -n console.log %s',
            'match_files': ['.*yipit/.*\.js$'],
            'print_filename': True,
            },
        {
            'output': 'Running Pyflakes...',
            'command': 'pyflakes %s',
            'match_files': ['.*\.py$'],
            'ignore_files': ['.*settings/.*', '.*manage.py', '.*migrations.*', '.*/terrain/.*'],
            'print_filename': False,
            },
        {
            'output': 'Running pep8...',
            'command': 'pep8 -r --ignore=E501,W293 %s',
            'match_files': ['.*\.py$'],
            'ignore_files': ['.*migrations.*'],
            'print_filename': False,
            },
        ]

ROOT_DIR = os.getcwd()

EXCLUDE_DIRS = [
        '.git',
        '.hg',
        '.svn',
        'data',
        ]

def matches_file(file_name, match_files):
    return any(re.compile(match_file).match(file_name) for match_file in match_files)


def check_files(files, check):
    result = 0
    print check['output']
    for file_name in files:
        if not 'match_files' in check or matches_file(file_name, check['match_files']):
            if not 'ignore_files' in check or not matches_file(file_name, check['ignore_files']):
                process = subprocess.Popen(check['command'] % file_name, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, err = process.communicate()
                if out or err:
                    if check['print_filename']:
                        prefix = '\t%s:' % file_name
                    else:
                        prefix = '\t'
                    output_lines = ['%s%s' % (prefix, line) for line in out.splitlines()]
                    print '\n'.join(output_lines)
                    if err:
                        print err
                    result = 1
    return result

def list_files(target_dir=None, exclude_dirs=None):
    if not target_dir:
        target_dir = ROOT_DIR

    target_dir = os.path.abspath(target_dir)

    if not exclude_dirs:
        exclude_dirs = EXCLUDE_DIRS

    exclude_dirs_abs = [os.path.join(target_dir, d) for d in EXCLUDE_DIRS]

    files = []
    for root, dirs, file_names in os.walk(target_dir):

        # Skip excluded directories
        skip = False
        for exclude_dir in exclude_dirs_abs:
            if root[:len(exclude_dir)] == exclude_dir:
                skip = True
                break
        if skip: continue

        for file_name in file_names:
            files.append(os.path.join(root, file_name))

    return files

def run_check(check, files=None):
    if not files:
        files = list_files()
    return check_files(files, check)

def run_checks(checks=None, files=None, target_dir=None, exclude_dirs=None):
    if not checks:
        checks = DEFAULT_CHECKS
    
    files = list_files(target_dir=target_dir, exclude_dirs=exclude_dirs)
    
    result = 0
    
    for check in checks:
        result = run_check(check, files) or result

    return result

if __name__ == '__main__':
    result = run_checks(DEFAULT_CHECKS)
    sys.exit(result)


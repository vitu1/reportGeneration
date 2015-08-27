#!/usr/bin/env python

from distutils.core import setup

# Get version number from package
exec(open('reportlib/version.py').read())

setup(
    name='reportGeneration',
    version=__version__,
    description='Generate report tables for the shotgun metagenomics pipeline.',
    author='Ceylan Tanes',
    author_email='ctanes@gmail.com',
    url='https://github.com/PennChopMicrobiomeProgram',
    packages=['reportlib'],
    scripts=['scripts/preprocess_report.py', 'scripts/ko_assignment_report.py', 'scripts/fastqc_report.py', 'scripts/build_results_table.py'],
    )

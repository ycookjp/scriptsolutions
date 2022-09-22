# -*- coding: utf-8 -*-
''''test-all script summary.

Copyright: ycookjp

This module runs unittest TestCases under this script's current directory.
Before running this script, edit test_all.yml in this script's current
directory as following.

    module_patterns:
      - '<script-name-pattern>'
      - '<script-name-pattern>'

Example:
    $ python test_all.py

Attributes:
    None

'''

from unittest import TestLoader, TestSuite
from HtmlTestRunner import HTMLTestRunner
import io
import os

import yaml

def load_config():
    '''
    
    Loads configuration file with YAMS format. 
    Configuration file should be located at same directory of this
    script, and name should be base name of this script except for
    extension is '.yml'.
    
    Returns:
        Dictionary: Returns key-value information.
    
    '''
    config_path = os.path.splitext(__file__)[0] + '.yml'
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
        return config

def run_test_all():
    '''
    
    Runs unittest's TestCases.

    '''
    # Loding config file
    config = load_config()
    # Getting test script patterns form config
    patterns = config['module_patterns']

    # Getting test suites from script patterns.
    suite = TestSuite()
    for pattern in patterns:
        suite.addTest(TestLoader().discover(os.path.dirname(__file__), pattern))

    runner = HTMLTestRunner( \
            output=os.path.dirname(__file__) + '/../target/site/test-report', \
            report_name='python-progs', add_timestamp=False, combine_reports=True)
    
    runner.run(suite)

if __name__ == '__main__':
    run_test_all()

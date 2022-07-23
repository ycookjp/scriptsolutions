# -*- config: utf-8 -*-

import unittest
import HtmlTestRunner
import logging
import os

from mypackage import failerror

class FailErrorTest(unittest.TestCase):
    
    def test_substring(self):
        self.assertEqual(failerror.substring('hello world !', 0, 2), 'he')
        self.assertEqual(failerror.substring('hello world !', 6), 'world !')
        self.assertEqual(failerror.substring(None, 0, 1), None)

if __name__ == '__main__':
    html_runner = HtmlTestRunner.HTMLTestRunner(
            output=os.path.dirname(__file__) + '/../target/site/test-report',
            add_timestamp=False)
    unittest.main(testRunner=html_runner)

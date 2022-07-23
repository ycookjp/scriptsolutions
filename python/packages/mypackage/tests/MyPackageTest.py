# -*- coding: utf-8 -*-

import unittest
import HtmlTestRunner
import logging
import os
import sys

from datetime import datetime
from mypackage import  mypackage

class MyPackageTest(unittest.TestCase):
    
    def setUp(self):
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        logging.debug('Set up test.')
    
    def test_find_repeat(self):
        # 3文字が11回出現する
        self.assertEqual(mypackage.find_repeat('abcijkxyz', 'ijk'), [3, 1],
                         msg="'ijk' must be found at index:3  of 'abcijkxyz' and 1 repeat.")
        # 3文字の中で1文字が違っていたら、その文字列は検出されない
        self.assertEqual(mypackage.find_repeat('abcijkxyz', 'ijK'), [-1, 0],
                         msg="'ijK' must be found at index:-1 of 'abcijkxyz' and 0 repeat.")
        # 3文字が連続している場合は、最初に検出した位置と、繰り返し回数：2が返される。
        self.assertEqual(mypackage.find_repeat('abcijkijkxyz', 'ijk'), [3, 2],
                         msg="'ijk' must be found at index:3  of 'abcijkijkxyz' and 3 repeat.")
        # 検出文字列が1文字で検出対象にそれが3つ連続する場合は、繰り返し回数：3が返される
        self.assertEqual(mypackage.find_repeat('abcijkxxx', 'x'), [6, 3],
                         msg="'x' must be found at index:6  of 'abcijkxxx' and 3 repeat.")
        
        # 開始位置を指定するとそれより前の文字列は検出されない
        self.assertEqual(mypackage.find_repeat('abcijkxyz', 'abc', 1), [-1, 0],
                         msg="'abc' must be found at index:-1  of 'bcijkxyz' and 0 repeat.")
        # 開始位置を指定するとそれより前の文字列は検出される
        self.assertEqual(mypackage.find_repeat('abcijkxyz', 'ijk', 3), [3, 1],
                         msg="'ijk' must be found at index:3  of 'ijkxyz' and 1 repeat.")
        
        # 終了位置を指定するとそれより後ろの文字列は検出されない
        self.assertEqual(mypackage.find_repeat('abcijkxyz', 'xyz', 0, 8), [-1, 0],
                         msg="'zyz' must be found at index:-1  of 'abcijkxy' and 0 repeat.")
        # 終了位置を指定するとそれより前の文字列は検出されない
        self.assertEqual(mypackage.find_repeat('abcijkxyz', 'ijk', 3, 7), [3, 1],
                         msg="'ijk' must be found at index:3  of 'ijk' and 1 repeat.")
    
    def test_format_date(self):

        # 月日時分が１桁の場合
        date = datetime(234, 5, 6, 7, 8, 9)
        # yyyy-MM-dd hh:mm:ss
        self.assertEqual(mypackage.format_date(date, "yyyy-MM-dd hh:mm:ss"), "0234-05-06 07:08:09")
        # yyyyMMddhhmmss
        self.assertEqual(mypackage.format_date(date, "yyyyMMddhhmmss"), "02340506070809")
        # yy-M-d h:m:s
        self.assertEqual(mypackage.format_date(date, "yy-M-d h:m:s"), "34-5-6 7:8:9")
        
        # 月日時分秒が２桁の場合
        date = datetime(2012, 10, 11, 12, 13, 14)
        # yyyy-MM-dd hh:mm:ss
        self.assertEqual(mypackage.format_date(date, "yyyy-MM-dd hh:mm:ss"), "2012-10-11 12:13:14")
        # yyyyMMddhhmmss
        self.assertEqual(mypackage.format_date(date, "yyyyMMddhhmmss"), "20121011121314")
        # yy-M-d h:m:s
        self.assertEqual(mypackage.format_date(date, "yy-M-d h:m:s"), "12-10-11 12:13:14")
        # 書式文字列に年５桁、月日時分秒に３桁を指定した場合
        # yyyyy/MMM/ddd hhh:mmm:sss
        self.assertEqual(mypackage.format_date(date, "yyyyy/MMM/ddd hhh:mmm:sss"), "02012/010/011 012:013:014")
        
        # 日本語a-zA-Z0-9YYYYDDHHSS => No match.
        self.assertEqual(mypackage.format_date(date, "日本語a-zA-Z0-9YYYYDDHHSS"), "日本語a-zA-Z0-9YYYYDDHHSS")
    
    def tearDown(self):
        logging.debug('Tear down test.')

if __name__ == '__main__':
    html_runner = HtmlTestRunner.HTMLTestRunner(
             output=os.path.dirname(__file__) + '/../target/site/test-report',
             add_timestamp=False)
    unittest.main(testRunner=html_runner)

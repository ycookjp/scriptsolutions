# -*- config: utf8 -*-
'''CsvutilTest module.

Copyright ycookjp
https://github.com/ycookjp/

'''
from pythonutils import csvutil

from io import StringIO
import logging
import sys
import unittest

root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class CsvutilTest(unittest.TestCase):
    '''csvutilモジュールのテストクラス。
    '''
    @classmethod
    def setUpClass(cls):
        pass
    
    @classmethod
    def tearDownClass(cls):
        pass
    
    def test__delete_line_break(self):
        '''_delete_line_break関数をテストする。
        '''
        logging.info('>>>>> test__delete_line_break start')

        logging.info('test01: \'abc\\r\\n\' -> \'abc\'')
        strdata: str = "abc\r\n"
        result = csvutil._delete_line_break(strdata)
        self.assertEqual('abc', result)

        logging.info('test02: \'abc\\n\' -> \'abc\'')
        strdata = 'abc\n'
        result = csvutil._delete_line_break(strdata)
        self.assertEqual('abc', result)

        logging.info('test03: \'abc\' -> \'abc\'')
        strdata = 'abc'
        result = csvutil._delete_line_break(strdata)
        self.assertEqual('abc', result)
        
        logging.info('test04: \'abc\\r\\ndef\\r\\n\' -> \'abc\\r\\ndef\'')
        strdata = 'abc\r\ndef\r\n'
        result = csvutil._delete_line_break(strdata)
        self.assertEqual('abc\r\ndef', result)
        
        logging.info('test05: \'abc\\ndef\\n\' -> \'abc\\ndef\'')
        strdata = 'abc\ndef\n'
        result = csvutil._delete_line_break(strdata)
        self.assertEqual('abc\ndef', result)
        
        logging.info('test06: \'abc\\ndef\' -> \'abc\\ndef\'')
        strdata = 'abc\ndef'
        result = csvutil._delete_line_break(strdata)
        self.assertEqual('abc\ndef', result)

        logging.info('<<<<< test__delete_line_break end')
    
    def test_get_csv_rowdata(self):
        '''get_csv_rowdata関数をテストする。
        
        1. 以下のCSVファイルを読み込む

                1,abc,def,あいう,かきく
                2,"abc","def","あいう","かきく"
                3,"abc,xyz","def
                uvw,","あいう,らりる","かきく""
                ""やゆよ,"
                4, "abc", ""def, "あいう", ""かきく
                5,"abc,xyz" ,"def
                uvw," "","あいう,らりゆ" ,"かきく""
                ""やゆよ," ""
            
            * カンマで区切らた文字がCSVの項目となること。  
                1,abc,def,あいう,かきく\\r\\n  
                => ['1', 'abc', 'def', 'あいう', 'かきく']
            * カンマで区切られた文字が「"」で始まり「"」で終わる場合は、
              CSV項目の値は文字列の前後の「"」が削除されていること。  
                2,"abc","def","あいう","かきく"\\r\\n  
                => ['2', 'abc', 'def', 'あいう', 'かきく']
            * 「"」で囲まれた文字列の中に改行、「,」が含まれる場合は、それらを
              含め「"」で囲まれた部分がCSV項目の値となること。  
                …,"def\\r\\nuvw,",…   
                => […, 'def\\r\\nuvw,', …]
            * カンマで区切られた文字列が「"」で始まり、「"」で終わる場合で、
              その文字列の中に「""」が存在する場合は、「""」は「"」として
              CSV項目に取り込まれること。  
                … ,"かきく""\\r\\n""やゆよ,"\\r\\n  
                => […, 'かきく"\\r\\n"やゆよ,']
            * カンマの後ろが「"」以外の文字があり、その後に「"」で囲まれる文字列
              があった場合は、「"」も含めてCSV項目に取り込まれること。  
                …, "あいう", ""かきく\\r\\n
                => […, ' "あいう"', ' ""かきく']
            * カンマの後ろが「"」で囲まれているが、後ろの「"」の後に「"」以外の
              文字列が存在する場合は、「"」を含めてCSV項目に取り込まれること。  
                …,らりゆ" ,…  
                => […, 'らりゆ" ', …]
            * カンマの後ろに以下の文字列が続く場合、
                * 「"」で囲まれており、その中に「""」、改行が存在する
                * その後ろが「"」、改行以外の文字である
                * さらにその後に「""」が続いて終わる
            
                文字列の前後の「"」が削除され、「""」が「"」に痴漢されたものが
                CSV項目の値となること。  
                …,"かきく""\\r\\n""やゆよ," ""\\r\\n  
                => […, 'かきく"\\r\\n"やゆよ," "']
        
        '''
        logging.info('>>>>> test_get_csv_rowdata start')

        csvdata = '1,abc,def,あいう,かきく\r\n'
        csvdata = csvdata + '2,"abc","def","あいう","かきく"\r\n'
        csvdata = csvdata + '3,"abc,xyz","def\r\nuvw,","あいう,らりる","かきく""\r\n""やゆよ,"\r\n'
        csvdata = csvdata + '4, "abc", ""def, "あいう", ""かきく\r\n'
        csvdata = csvdata + '5,"abc,xyz" ,"def\r\nuvw," "","あいう,らりゆ" ,"かきく""\r\n""やゆよ," ""\r\n'
        
        with StringIO(csvdata) as f:
            for rowdata in csvutil.read_csv(f):
                logging.info(f'fowdata: {rowdata}')
                if rowdata[0] == '1':
                    logging.info('test01: CSV line[1]')
                    self.assertEqual('abc', rowdata[1])
                    self.assertEqual('def', rowdata[2])
                    self.assertEqual('あいう', rowdata[3])
                    self.assertEqual('かきく', rowdata[4])
                if rowdata[0] == '2':
                    logging.info('test01: CSV line[2]')
                    self.assertEqual('abc', rowdata[1])
                    self.assertEqual('def', rowdata[2])
                    self.assertEqual('あいう', rowdata[3])
                    self.assertEqual('かきく', rowdata[4])
                if rowdata[0] == '3':
                    logging.info('test01: CSV line[3]')
                    self.assertEqual('abc,xyz', rowdata[1])
                    self.assertEqual('def\r\nuvw,', rowdata[2])
                    self.assertEqual('あいう,らりる', rowdata[3])
                    self.assertEqual('かきく"\r\n"やゆよ,', rowdata[4])
                if rowdata[0] == '4':
                    logging.info('test01: CSV line[4]')
                    self.assertEqual(' "abc"', rowdata[1])
                    self.assertEqual(' ""def', rowdata[2])
                    self.assertEqual(' "あいう"', rowdata[3])
                    self.assertEqual(' ""かきく', rowdata[4])
                if rowdata[0] == '5':
                    logging.info('test01: CSV line[5]')
                    self.assertEqual('"abc,xyz" ', rowdata[1])
                    self.assertEqual('def\r\nuvw," "', rowdata[2])
                    self.assertEqual('"あいう,らりゆ" ', rowdata[3])
                    self.assertEqual('かきく"\r\n"やゆよ," "', rowdata[4])

        logging.info('<<<<< test_get_csv_rowdata end')

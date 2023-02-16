'''AwsResourceOperatorFactoryTest module.

Copyright: ycookjp

'''

import unittest
import logging
import os
import shutil
import sys

from awsutils.aws_resource_operator import AwsResourceOperatorFactory

root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class AwsResourceOperatorFactoryTest(unittest.TestCase):
    '''AwsResourceOperatorFactory クラス用のテストクラス
    
    '''
    @classmethod
    def setUpClass(cls):
        '''テストクラスの set up を実行します。
        
        Args:
            cls: テストクラス
        
        '''
        logging.info('Set up test class.')

    @classmethod
    def tearDownClass(cls):
        '''テストクラスの tear down を実行します。
        
        Args:
            cls: テストクラス
        
        '''
        logging.info('Tear down test class.')
        
        workdir = os.path.join(os.path.dirname(__file__), 'work')
        for name in os.listdir(workdir):
            name_path = os.path.join(workdir, name)
            if os.path.isfile(name_path) and name != 'do_not_commit_this_directory':
                os.remove(name_path)
            elif os.path.isdir(name_path):
                shutil.rmtree(name_path)
    
    def test_create(self):
        '''createメソッドのテストを実行します。
        
        * 引数に「ec2.instance」を指定してcreateメソッドを実行する。
            * => AwsEc2InstanceOperatorクラスのインスタンスが作成されること。
        * 引数に「rds.db_cluster」を指定してcreateメソッドを実行する。
            * => AwsRdsDbClusterOperatorクラスのインスタンスが作成されること。
        * 引数に「rds.db_instance」を指定してcreateメソッドを実行する。
            * => AwsRdsDbInstanceOperatorクラスのインスタンスが作成されること。
        
        '''
        logging.info('>>>>> test_create start')
        
        region_name = 'ap-northeast-1'
        
        # 引数に「ec2.instance」を指定してcreateメソッドを実行する。
        operator = AwsResourceOperatorFactory.create('ec2.instance', region_name)
        # => AwsEc2InstanceOperatorクラスのインスタンスが作成されること。
        self.assertEqual(operator.__class__.__name__, 'AwsEc2InstanceOperator')
        
        # 引数に「rds.db_cluster」を指定してcreateメソッドを実行する。
        operator = AwsResourceOperatorFactory.create('rds.db_cluster', region_name)
        # => AwsRdsDbClusterOperatorクラスのインスタンスが作成されること。
        self.assertEqual(operator.__class__.__name__, 'AwsRdsDbClusterOperator')
        
        # 引数に「rds.db_instance」を指定してcreateメソッドを実行する。
        operator = AwsResourceOperatorFactory.create('rds.db_instance', region_name)
        # => AwsRdsDbInstanceOperatorクラスのインスタンスが作成されること。
        self.assertEqual(operator.__class__.__name__, 'AwsRdsDbInstanceOperator')
        
        logging.info('<<<<< test_create end')
    
    def test_error_create(self):
        '''不正なパラメータを指定して、createメソッドのテストを実行します。
        
        * 引数に「ec2.error」を指定してcreateメソッドを実行する。
            * => RuntimeError 例外が発生すること。
        
        '''
        logging.info('>>>>> test_error_create start')
        
        region_name = 'ap-northeast-1'
        
        # 引数に「ec2.error」を指定してcreateメソッドを実行する。
        with self.assertRaises(Exception) as cm:
            AwsResourceOperatorFactory.create('ec2.error', region_name)
        logging.info(str(cm.exception))
        # => RuntimeError 例外が発生すること。
        self._baseAssertEqual(cm.exception.__class__.__name__, 'RuntimeError')
        
        logging.info('<<<<< test_error_create end')

if __name__ == '__main__':
    unittest.main()

'''AwsEc2InstanceOperatorTest module.

Copyright: ycookjp

'''

import unittest
import logging
import os
import shutil
import sys

from awsutils.aws_resource_operator import AwsResourceOperatorFactory
import aws_test_utils
from moto import mock_ec2

root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class AwsEc2InstanceOperatorTest(unittest.TestCase):
    '''AwsEc2InstanceOperator クラス用のテストクラス
    
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

    @mock_ec2
    def test_start_stop(self):
        '''startメソッド、stopメソッドのテストを実行します。
        
        テストの内容は以下のとおりです。
        
        * 起動しているEC2インスタンスのIDを指定して、stopメソッドを実行する。
            * => 停止操作したインスタンスの数が1であること。
            * => インスタンスのステータスが「stopped」であること。
        * 停止しているEC2インスタンスのIDを指定して、startメソッドを実行する。
            * => 開始操作したインスタンスの数が1であること。
            * => インスタンスのステータスが「running」であること。
        * 
        
        '''
        logging.info('>>>>> test_start_stop start')
        
        region_name = 'ap-northeast-1'
        operator = AwsResourceOperatorFactory.create('ec2.instance', region_name)

        instances = aws_test_utils.run_instances('ami-xxxxxxxxxxxxxxxxx',
                region_name, 1)
        instance_id = instances[0]['InstanceId']

        # 起動しているEC2インスタンスのIDを指定して、stopメソッドを実行する。
        count = operator.stop(instance_id)
        status = operator.get_status(instance_id)
        # => 停止操作したインスタンスの数が1であること。
        self.assertEqual(count, 1)
        # => インスタンスのステータスが「stopped」であること。
        self.assertEqual(status, 'stopped')

        # 停止しているEC2インスタンスのIDを指定して、startメソッドを実行する。
        count = operator.start(instance_id)
        status = operator.get_status(instance_id)
        # => 開始操作したインスタンスの数が1であること。
        self.assertEqual(count, 1)
        # => インスタンスのステータスが「running」であること。
        self.assertEqual(status, 'running')
        
        logging.info('<<<<< test_start_stop end')
    
    @mock_ec2
    def test_start_stop_resources(self):
        '''startメソッド、stopメソッドのテストを実行します。
        
        テストの内容は、以下のとおりです。
        
        * 起動している２つのEC2インスタンスのIDのリストを指定して、
          stop_resourcesメソッドを実行する。
            * => 停止操作したインスタンスの数が2であること。
            * => それぞれのEC2インスタンスのステータスが「stopped」であること。
        * 停止している２つのEC2インスタンスのIDのリストを指定して、
          start_resourcesメソッドを実行する。
            * => 停止操作したインスタンスの数が2であること。
            * => 停止操作したインスタンスの数が2であること。
        
        '''
        logging.info('>>>>> test_start_stop_resources start')

        region_name = 'ap-northeast-1'
        operator = AwsResourceOperatorFactory.create('ec2.instance', region_name)

        instances = aws_test_utils.run_instances('ami-xxxxxxxxxxxxxxxxx',
                region_name, 2)
        instance_ids = []
        for instance in instances:
            instance_ids.append(instance['InstanceId'])
        
        # 起動している２つのEC2インスタンスのIDのリストを指定して、
        # stop_resourcesメソッドを実行する。
        count = operator.stop_resources(instance_ids)
        # => 停止操作したインスタンスの数が2であること。
        self.assertEqual(count, 2)
        # => それぞれのEC2インスタンスのステータスが「stopped」であること。
        for instance_id in instance_ids:
            status = operator.get_status(instance_id)
            self.assertEqual(status, 'stopped')
        
        # 停止している２つのEC2インスタンスのIDのリストを指定して、
        # start_resourcesメソッドを実行する。
        count = operator.start_resources(instance_ids)
        # => 停止操作したインスタンスの数が2であること。
        self.assertEquals(count, 2)
        # =>それぞれのEC2インスタンスのステータスが「running」であること。
        for instance_id in instance_ids:
            status = operator.get_status(instance_id)
            self.assertEqual(status, 'running')
        
        logging.info('<<<<< test_start_stop_resources end')
    
    @mock_ec2
    def test_error_start_stop(self):
        '''存在しないEC2インスタンスのIDを指定して、start、stopメソッドの
            テストを実行します。
            
        テストの内容は、以下のとおりです。
            
        * 存在しないEC2インスタンスのIDを指定して、stopメソッドを実行する。
            * => 例外が発生すること。
        * 存在しないEC2インスタンスのIDを指定して、startメソッドを実行する。
            * => 例外が発生すること。
        
        '''
        logging.info('>>>>> test_error_start_stop start')
        
        region_name = 'ap-northeast-1'
        operator = AwsResourceOperatorFactory.create('ec2.instance', region_name)
        instance_id = 'i-xxxxxxxxxxxxxxxxx'
        
        # 存在しないEC2インスタンスのIDを指定して、stopメソッドを実行する。
        with self.assertRaises(Exception) as cm:
            operator.stop(instance_id)
        # => 例外が発生すること。
        logging.info(str(cm.exception))
        
        # 存在しないEC2インスタンスのIDを指定して、startメソッドを実行する。
        with self.assertRaises(Exception) as cm:
            operator.start(instance_id)
        # => 例外が発生すること。
        logging.info(str(cm.exception))
        
        logging.info('<<<<< test_error_start_stop end')
    
    @mock_ec2
    def test_error_start_stop_resources(self):
        '''存在しないEC2インスタンスのIDを含むインスタンスIDの配列を指定して、
            start_resources、stop_resourcesメソッドのテストを実行します。
        
        テストの内容は、以下のとおりです。
        
        * 存在しないEC2インスタンス１つと、実行中のEC2インスタンス１つの
          インスタンスIDを指定して、stop_resourcesメソッドを実行する。
            * => 実行中だったEC2インスタンスのステータスが「stopped」となること。
            * => 例外が発生すること。
        * 存在しないEC2インスタンス１つと、停止中のEC2インスタンス１つの
          インスタンスIDを指定して、start_resourcesメソッドを実行する。
            * => 停止中だったEC2インスタンスのステータスが「running」となること；
            * => 例外が発生すること。
        
        '''
        logging.info('>>>>> test_error_start_stop_resources start')
        
        region_name = 'ap-northeast-1'
        operator = AwsResourceOperatorFactory.create('ec2.instance', region_name)

        instances = aws_test_utils.run_instances('ami-xxxxxxxxxxxxxxxxx',
                region_name, 1)
        running_ids = []
        for instance in instances:
            running_ids.append(instance['InstanceId'])
        instance_ids = ['i-xxxxxxxxxxxxxxxxx']
        instance_ids.extend(running_ids)
        
        # 存在しないEC2インスタンス１つと、実行中のEC2インスタンス１つの
        # インスタンスIDを指定して、stop_resourcesメソッドを実行する。
        with self.assertRaises(Exception) as cm:
            operator.stop_resources(instance_ids)
        # => 例外が発生すること。
        logging.info(str(cm.exception))
        # => 実行中だったEC2インスタンスのステータスが「stopped」となること。
        for instance_id in running_ids:
            status = operator.get_status(instance_id)
            self.assertEquals(status, 'stopped')
        
        # 存在しないEC2インスタンス１つと、停止中のEC2インスタンス１つの
        # インスタンスIDを指定して、start_resourcesメソッドを実行する。
        with self.assertRaises(Exception) as cm:
            operator.start_resources(instance_ids)
        # => 例外が発生すること。
        logging.info(str(cm.exception))
        # => 停止中だったEC2インスタンスのステータスが「running」となること；
        for instance_id in running_ids:
            status = operator.get_status(instance_id)
            self.assertEquals(status, 'running')
        
        logging.info('<<<<< test_error_start_stop_resources end')

if __name__ == '__main__':
    unittest.main()

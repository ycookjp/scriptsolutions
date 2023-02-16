# -*- config: utf-8 -*-
'''AwsRdsInstanceOperatorTest module.

Copyright: ycookjp

Note:
    RDSのAWS clientのモックは、RDSのインスタンス１つしかサポートしないため、
    テストでは有効なインスタンスが常に１つであるようにシナリオを構成している。

'''

import unittest
import logging
import os
import shutil
import sys

from awsutils.aws_resource_operator import AwsResourceOperatorFactory
import aws_test_utils
from moto import mock_rds

root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class AwsRdsInstanceOperatorTest(unittest.TestCase):
    '''AwsRdsInstanceOperator クラス用のテストクラス
    
    '''
    @classmethod
    def setUpClass(cls):
        '''テストクラスの set up を実行します。
        
        Args:
            cls: テストクラスのインスタンス
        
        '''
        logging.info('Set up test class.')

    @classmethod
    def tearDownClass(cls):
        '''テストクラスの tear down を実行します。
        
        Args:
            cls: テストクラスのインスタンス
        
        '''
        logging.info('Tear down test class.')
        
        workdir = os.path.join(os.path.dirname(__file__), 'work')
        for name in os.listdir(workdir):
            name_path = os.path.join(workdir, name)
            if os.path.isfile(name_path) and name != 'do_not_commit_this_directory':
                os.remove(name_path)
            elif os.path.isdir(name_path):
                shutil.rmtree(name_path)
    
    @mock_rds
    def test_start_stop(self):
        '''startメソッド、stopメソッドのテストを実行します。
        
        テストの内容は、以下のとおりです。
        
        * 実行中のRDS DB instanceのIDを指定して、stopメソッドを実行する。
            * => 停止操作したRDS DB instanceの個数が1であること。
            * => RDS DB instanceのステータスが「stopping」または「stopped」と
              なること。
        * 停止中のRDS DB instanceのIDを指定して、stopメソッドを開始する。
            * => 停止操作したRDS DB instanceの個数が0であること。
            * => RDS DB instanceのステータスが「stopping」または「stopped」と
              なること。
        * 停止中のRDS DB instanceのIDを指定して、startメソッドを開始する。
            * => 開始操作したRDS DB instanceの個数が1であること。
            * => RDS DB instanceのステータスが「available」であること。
        * 実行中のRDS DB instanceのIDを指定して、startメソッドを開始する。
            * => 開始操作したRDS DB instanceの個数が0であること。
            * => RDS DB instanceステータスが「available」であること。
        
        '''
        logging.info('>>>>> test_start_stop start')
        
        region_name = 'ap-northeast-1'
        # AwsRdsDbInstanceOperator クラスのインスタンスを作成する
        operator = AwsResourceOperatorFactory.create('rds.db_instance', region_name)
        
        # RDSのDB instanceを作成する
        db_instance_id = 'rds_instance_test01'
        resource_type = 'db.t2.micro'
        engine_name = 'postgres'
        username = 'postgres'
        password = 'password@123'
        logging.info(f'Creating RDS DB Instance: {db_instance_id} ...')
        aws_test_utils.create_db_instance(db_instance_id, resource_type,
                engine_name, username, password, region_name)
        status = operator.get_status(db_instance_id)
        logging.info(f'RDS DB Instance: {db_instance_id} {status}')
        
        # 実行中のRDS DB instanceのIDを指定して、stopメソッドを実行する。
        logging.info(f'Stopping RDS DB Instance: {db_instance_id} ...')
        count = operator.stop(db_instance_id)
        # => 停止操作したRDS DB instanceの個数が1であること。
        self.assertEqual(count, 1)
        status = operator.get_status(db_instance_id)
        logging.info(f'RDS DB Instance: {db_instance_id} {status}')
        statuses = [status]
        # => RDS DB instanceのステータスが「stopping」または「stopped」と
        # なること。
        self.assertTrue(statuses.count('stopping') + statuses.count('stopped') > 0)
        
        # 停止中のRDS DB instanceのIDを指定して、stopメソッドを開始する。
        logging.info(f'Stopping RDS DB Instance: {db_instance_id} ...')
        count = operator.stop(db_instance_id)
        # => 停止操作したRDS DB instanceの個数が0であること。
        self.assertEqual(count, 0)
        status = operator.get_status(db_instance_id)
        logging.info(f'RDS DB Instance: {db_instance_id} {status}')
        statuses = [status]
        # => RDS DB instanceのステータスが「stopping」または「stopped」と
        # なること。
        self.assertTrue(statuses.count('stopping') + statuses.count('stopped') > 0)
         
        # 停止中のRDS DB instanceのIDを指定して、startメソッドを開始する。
        logging.info(f'Starting RDS DB Instance: {db_instance_id} ...')
        count = operator.start(db_instance_id)
        # => 開始操作したRDS DB instanceの個数が1であること。
        self.assertEqual(count, 1)
        status = operator.get_status(db_instance_id)
        logging.info(f'RDS DB Instance: {db_instance_id} {status}')
        # => RDS DB instanceのステータスが「available」であること。
        self.assertEqual(status, 'available')
        
        # 実行中のRDS DB instanceのIDを指定して、startメソッドを開始する。
        logging.info(f'Starting RDS DB Instance: {db_instance_id} ...')
        count = operator.start(db_instance_id)
        # => 開始操作したRDS DB instanceの個数が0であること。
        self.assertEqual(count, 0)
        status = operator.get_status(db_instance_id)
        logging.info(f'RDS DB Instance: {db_instance_id} {status}')
        # => RDS DB instanceのステータスが「available」であること。
        self.assertEqual(status, 'available')
        
        logging.info('<<<<< test_start_stop end')
    
    @mock_rds
    def test_start_stop_resources(self):
        '''start_resourcesメソッド、stop_resourcesメソッドのテストを実行します。
        
        テストの内容は、以下のとおりです。
        
        * 実行中のRDS DB instance１つのIDを指定して、stop_resourcesメソッドを
          実行する。
            * => 停止操作したRDS DB cluserの個数は1であること。
            * => RDS DB instanceのステータスが「stopping」または「stopped」で
              あること。
        * 停止中のRDS DB instance１つのIDを指定して、stop_resourcesメソッドを
          実行する。
            * => 停止操作したRDS DB cluserの個数は0であること。
            * => RDS DB instanceのステータスが「stopping」または「stopped」で
              あること。
        * 停止中のRDS DB instance１つのIDを指定して、start_resourcesメソッドを
          実行する。
            * => 開始操作したRDS DB instanceの個数が１であること。
            * => RDS DB instanceのステータスがavailableであること。
        * 実行中のRDS DB instance１つのIDを指定して、start_resourcesメソッドを
          実行する。
            * => 開始操作したRDS DB instanceの個数が０であること。
            * => RDS DB instanceのステータスがavailableであること。
        
        '''
        logging.info('>>>>> test_start_stop_resources start')
        
        region_name = 'ap-northeast-1'
        # AwsRdsDbInstanceOperator クラスのインスタンスを作成する
        operator = AwsResourceOperatorFactory.create('rds.db_instance', region_name)
        
        # RDSのDB instanceを作成する
        db_instance_id = 'rds_instance_test01'
        resource_type = 'db.t2.micro'
        engine_name = 'postgres'
        username = 'postgres'
        password = 'password@123'
        logging.info(f'Creating RDS DB Instance: {db_instance_id} ...')
        aws_test_utils.create_db_instance(db_instance_id, resource_type,
                engine_name, username, password, region_name)
        status = operator.get_status(db_instance_id)
        logging.info(f'RDS DB Instance: {db_instance_id} {status}')
        
        # 実行中のRDS DB instance１つのIDを指定して、stop_resourcesメソッドを
        # 実行する。
        logging.info(f'Stopping RDS DB Instance: {db_instance_id} ...')
        count = operator.stop_resources([db_instance_id])
        # => 停止操作したRDS DB cluserの個数は1であること。
        self.assertEqual(count, 1)
        status = operator.get_status(db_instance_id)
        logging.info(f'RDS DB Instance: {db_instance_id} {status}')
        statuses = [status]
        # => RDS DB instanceのステータスが「stopping」または「stopped」で
        # あること。
        self.assertTrue(statuses.count('stopping') + statuses.count('stopped') > 0)
        
        # 停止中のRDS DB instance１つのIDを指定して、stop_resourcesメソッドを
        # 実行する。
        logging.info(f'Stopping RDS DB Instance: {db_instance_id} ...')
        count = operator.stop_resources([db_instance_id])
        # => 停止操作したRDS DB cluserの個数は0であること。
        self.assertEqual(count, 0)
        status = operator.get_status(db_instance_id)
        logging.info(f'RDS DB Instance: {db_instance_id} {status}')
        statuses = [status]
        # => RDS DB instanceのステータスが「stopping」または「stopped」で
        # あること。
        self.assertTrue(statuses.count('stopping') + statuses.count('stopped') > 0)
        
        # 停止中のRDS DB instance１つのIDを指定して、start_resourcesメソッドを
        # 実行する。
        logging.info(f'Starting RDS DB Instance: {db_instance_id} ...')
        count = operator.start_resources([db_instance_id])
        # => 開始操作したRDS DB instanceの個数が１であること。
        self._baseAssertEqual(count, 1)
        status = operator.get_status(db_instance_id)
        logging.info(f'RDS DB Instance: {db_instance_id} {status}')
        # => RDS DB instanceのステータスがavailableであること。
        self.assertEqual(status, 'available')
        
        # 実行中のRDS DB instance１つのIDを指定して、start_resourcesメソッドを
        # 実行する。
        logging.info(f'Starting RDS DB Instance: {db_instance_id} ...')
        count = operator.start_resources([db_instance_id])
        # => 開始操作したRDS DB instanceの個数が０であること。
        self._baseAssertEqual(count, 0)
        status = operator.get_status(db_instance_id)
        logging.info(f'RDS DB Instance: {db_instance_id} {status}')
        # => RDS DB instanceのステータスがavailableであること。
        self.assertEqual(status, 'available')
        
        logging.info('<<<<< test_start_stop_resources end')
    
    @mock_rds
    def test_error_start_stop(self):
        '''存在しないRDS DB instanceのIDを指定して、startメソッド、stopメソッドのテストを実行します。
        
        テスト内容は、以下のとおりです。
        
        * 存在しないのRDS DB instanceのIDを指定して、stopメソッドを実行する。
            * => 例外が発生すること。
        * 存在しないのRDS DB instanceのIDを指定して、startメソッドを開始する。
            * => 例外が発生すること。
        
        '''
        logging.info('>>>>> test_error_start_stop start')
        
        region_name = 'ap-northeast-1'
        # AwsRdsDbInstanceOperator クラスのインスタンスを作成する
        operator = AwsResourceOperatorFactory.create('rds.db_instance', region_name)
        
        # 存在しないRDSのDB instance ID
        db_instance_id = 'rds_instance_error'
        
        # 存在しないのRDS DB instanceのIDを指定して、stopメソッドを実行する。
        logging.info(f'Stopping RDS DB Instance: {db_instance_id} ...')
        with self.assertRaises(Exception) as cm:
            operator.stop(db_instance_id)
        # => 例外が発生すること。
        logging.info(str(cm.exception))
        
        # 存在しないのRDS DB instanceのIDを指定して、startメソッドを開始する。
        logging.info(f'Starting RDS DB Instance: {db_instance_id} ...')
        with self.assertRaises(Exception) as cm:
            operator.start(db_instance_id)
        # => 例外が発生すること。
        logging.info(str(cm.exception))
        
        logging.info('<<<<< test_error_start_stop end')
    
    @mock_rds
    def test_error_start_stop_resources(self):
        '''存在しないRDS DB InstanceのIDを含むRDS DB instanceの配列を指定してstart_resourcesメソッド、stop_resourcesメソッドのテストを実行します。
        
        テストの内容は、以下のとおりです。

        * 存在しないRDS DB cliuster１つと実行中のRDS DB instance１つのIDを指定
          して、stop_resourcesメソッド実行する。
            * => 例外が発生すること。
            * => 存在するRDS DB instanceのステータスが「stopping」または「stopped」
              であること。
        * 存在しないRDS DB cliuster１つと停止中のRDS DB instance１つのIDを指定
          して、stop_resourcesメソッドを実行する。
            * => 例外が発生すること。
            * => 存在するRDS DB instanceのステータスが「stopping」または「stopped」
              であること。
        * 存在しないRDS DB cliuster１つと停止中のRDS DB instance１つのIDを指定
          して、start_resourcesメソッドを実行する。
            * => 例外が発生すること。
            * => 存在するRDS DB instanceのステータスがavailableであること。
        * 存在しないRDS DB cliuster１つと実行中のRDS DB instance１つのIDを指定
          して、start_resourcesメソッドを実行する。
            * => 例外が発生すること。
            * => RDS DB instanceのステータスがavailableであること。
        
        '''
        logging.info('>>>>> test_error_start_stop_resources start')
        
        region_name = 'ap-northeast-1'
        # AwsRdsDbInstanceOperator クラスのインスタンスを作成する
        operator = AwsResourceOperatorFactory.create('rds.db_instance', region_name)
        
        # RDSのDB instanceを作成する
        db_instance_id_ok = 'rds_instance_test01'
        resource_type = 'db.t2.micro'
        engine_name = 'postgres'
        username = 'postgres'
        password = 'password@123'
        logging.info(f'Creating RDS DB Instance: {db_instance_id_ok} ...')
        aws_test_utils.create_db_instance(db_instance_id_ok, resource_type,
                engine_name, username, password, region_name)
        
        # 存在しない RDSのDB instance ID
        db_instance_id_ng = 'rds_instance_error'
        
        # 存在しないRDS DB cliuster１つと実行中のRDS DB instance１つのIDを指定
        # して、stop_resourcesメソッド実行する。
        logging.info(f'Stopping RDS DB Instance: {[db_instance_id_ng, db_instance_id_ok]} ...')
        with self.assertRaises(Exception) as cm:
            operator.stop_resources([db_instance_id_ng, db_instance_id_ok])
        # => 例外が発生すること。
        logging.info(str(cm.exception))
        status = operator.get_status(db_instance_id_ok)
        logging.info(f'RDS DB Instance: {db_instance_id_ok} {status}')
        statuses = [status]
        # => 存在するRDS DB instanceのステータスが「stopping」または「stopped」
        # であること。
        self.assertTrue(statuses.count('stopping') + statuses.count('stopped') > 0)
        
        # 存在しないRDS DB cliuster１つと停止中のRDS DB instance１つのIDを指定
        # して、stop_resourcesメソッドを実行する。
        logging.info(f'Stopping RDS DB Instance: {[db_instance_id_ng, db_instance_id_ok]} ...')
        with self.assertRaises(Exception) as cm:
            operator.stop_resources([db_instance_id_ng, db_instance_id_ok])
        # => 例外が発生すること。
        logging.info(str(cm.exception))
        status = operator.get_status(db_instance_id_ok)
        logging.info(f'RDS DB Instance: {db_instance_id_ok} {status}')
        statuses = [status]
        # => 存在するRDS DB instanceのステータスが「stopping」または「stopped」
        # であること。
        self.assertTrue(statuses.count('stopping') + statuses.count('stopped') > 0)
        
        # 存在しないRDS DB cliuster１つと停止中のRDS DB instance１つのIDを指定
        # して、start_resourcesメソッドを実行する。
        logging.info(f'Starting RDS DB Instance: {[db_instance_id_ng, db_instance_id_ok]} ...')
        with self.assertRaises(Exception) as cm:
            operator.start_resources([db_instance_id_ng, db_instance_id_ok])
        # => 例外が発生すること。
        logging.info(str(cm.exception))
        status = operator.get_status(db_instance_id_ok)
        logging.info(f'RDS DB Instance: {db_instance_id_ok} {status}')
        # => 存在するRDS DB instanceのステータスがavailableであること。
        self.assertEqual(status, 'available')
        
        # 存在しないRDS DB cliuster１つと実行中のRDS DB instance１つのIDを指定
        # して、start_resourcesメソッドを実行する。
        logging.info(f'Starting RDS DB Instance: {[db_instance_id_ng, db_instance_id_ok]} ...')
        with self.assertRaises(Exception) as cm:
            operator.start_resources([db_instance_id_ng, db_instance_id_ok])
        # => 例外が発生すること。
        logging.info(str(cm.exception))
        status = operator.get_status(db_instance_id_ok)
        logging.info(f'RDS DB Instance: {db_instance_id_ok} {status}')
        # => RDS DB instanceのステータスがavailableであること。
        self.assertEqual(status, 'available')
        
        logging.info('<<<<< test_error_start_stop_resources end')

if __name__ == '__main__':
    unittest.main()

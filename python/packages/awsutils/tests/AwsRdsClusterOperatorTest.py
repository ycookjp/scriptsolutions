# -*- config: utf-8 -*-
'''AwsRdsClusterOperatorTest module.

Copyright: ycookjp

Note:
    RDSのAWS clientのモックは、RDSのインスタンス１つしかサポートしないため、
    テストでは有効なインスタンスが常に１つであるようにシナリオを構成している。

'''

import unittest
import HtmlTestRunner
import json
import logging
import os
import shutil
import sys
import traceback

from awsutils import aws_resource_start_stop
from awsutils.aws_resource_operator import AwsResourceOperatorFactory
import aws_test_utils
import boto3
from moto import mock_rds
from unittest.case import TestCase
import time
import yaml

root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class AwsRdsClusterOperatorTest(unittest.TestCase):
    '''AwsRdsClusterOperator クラス用のテストクラス
    
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
        
        * 実行中のRDS DB clusterのIDを指定して、stopメソッドを実行する。
            * => 停止操作したRDS DB clusterの個数が1であること。
            * => RDS DB clusterのステータスが「stopping」または「stopped」と
              なること。
        * 停止中のRDS DB clusterのIDを指定して、stopメソッドを開始する。
            * => 停止操作したRDS DB clusterの個数が0であること。
            * => RDS DB clusterのステータスが「stopping」または「stopped」と
              なること。
        * 停止中のRDS DB clusterのIDを指定して、startメソッドを開始する。
            * => 開始操作したRDS DB clusterの個数が1であること。
            * => RDS DB clusterのステータスが「available」であること。
        * 実行中のRDS DB clusterのIDを指定して、startメソッドを開始する。
            * => 開始操作したRDS DB clusterの個数が0であること。
            * => RDS DB clusterステータスが「available」であること。
        
        '''
        logging.info('>>>>> test_start_stop start')
        
        region_name = 'ap-northeast-1'
        # AwsRdsDbClusterOperator クラスのインスタンスを作成する
        operator = AwsResourceOperatorFactory.create('rds.db_cluster', region_name)
        
        # RDSのDB clusterを作成する
        db_cluster_id = 'rds_cluster_test01'
        engine_name = 'postgres'
        username = 'postgres'
        password = 'password@123'
        logging.info(f'Creating RDS DB Cluster: {db_cluster_id} ...')
        aws_test_utils.create_db_cluster(db_cluster_id, engine_name,
                                username, password, region_name)
        status = operator.get_status(db_cluster_id)
        logging.info(f'RDS DB Cluster: {db_cluster_id} {status}')
        
        # 実行中のRDS DB clusterのIDを指定して、stopメソッドを実行する。
        logging.info(f'Stopping RDS DB Cluster: {db_cluster_id} ...')
        count = operator.stop(db_cluster_id)
        # => 停止操作したRDS DB clusterの個数が1であること。
        self.assertEqual(count, 1)
        status = operator.get_status(db_cluster_id)
        logging.info(f'RDS DB Cluster: {db_cluster_id} {status}')
        statuses = [status]
        # => RDS DB clusterのステータスが「stopping」または「stopped」と
        # なること。
        self.assertTrue(statuses.count('stopping') + statuses.count('stopped') > 0)
        
        # 停止中のRDS DB clusterのIDを指定して、stopメソッドを開始する。
        logging.info(f'Stopping RDS DB Cluster: {db_cluster_id} ...')
        count = operator.stop(db_cluster_id)
        # => 停止操作したRDS DB clusterの個数が0であること。
        self.assertEqual(count, 0)
        status = operator.get_status(db_cluster_id)
        logging.info(f'RDS DB Cluster: {db_cluster_id} {status}')
        statuses = [status]
        # => RDS DB clusterのステータスが「stopping」または「stopped」と
        # なること。
        self.assertTrue(statuses.count('stopping') + statuses.count('stopped') > 0)
         
        # 停止中のRDS DB clusterのIDを指定して、startメソッドを開始する。
        logging.info(f'Starting RDS DB Cluster: {db_cluster_id} ...')
        count = operator.start(db_cluster_id)
        # => 開始操作したRDS DB clusterの個数が1であること。
        self.assertEqual(count, 1)
        status = operator.get_status(db_cluster_id)
        logging.info(f'RDS DB Cluster: {db_cluster_id} {status}')
        # => RDS DB clusterのステータスが「available」であること。
        self.assertEqual(status, 'available')
        
        # 実行中のRDS DB clusterのIDを指定して、startメソッドを開始する。
        logging.info(f'Starting RDS DB Cluster: {db_cluster_id} ...')
        count = operator.start(db_cluster_id)
        # => 開始操作したRDS DB clusterの個数が0であること。
        self.assertEqual(count, 0)
        status = operator.get_status(db_cluster_id)
        logging.info(f'RDS DB Cluster: {db_cluster_id} {status}')
        # => RDS DB clusterのステータスが「available」であること。
        self.assertEqual(status, 'available')
        
        logging.info('<<<<< test_start_stop end')
    
    @mock_rds
    def test_start_stop_resources(self):
        '''start_resourcesメソッド、stop_resourcesメソッドのテストを実行します。
        
        テストの内容は、以下のとおりです。
        
        * 実行中のRDS DB cluster１つのIDを指定して、stop_resourcesメソッドを
          実行する。
            * => 停止操作したRDS DB cluserの個数は1であること。
            * => RDS DB instanceのステータスが「stopping」または「stopped」で
              あること。
        * 停止中のRDS DB cluster１つのIDを指定して、stop_resourcesメソッドを
          実行する。
            * => 停止操作したRDS DB cluserの個数は0であること。
            * => RDS DB instanceのステータスが「stopping」または「stopped」で
              あること。
        * 停止中のRDS DB cluster１つのIDを指定して、start_resourcesメソッドを
          実行する。
            * => 開始操作したRDS DB clusterの個数が１であること。
            * => RDS DB clusterのステータスがavailableであること。
        * 実行中のRDS DB cluster１つのIDを指定して、start_resourcesメソッドを
          実行する。
            * => 開始操作したRDS DB clusterの個数が０であること。
            * => RDS DB clusterのステータスがavailableであること。
        
        '''
        logging.info('>>>>> test_start_stop_resources start')
        
        region_name = 'ap-northeast-1'
        # AwsRdsDbClusterOperator クラスのインスタンスを作成する
        operator = AwsResourceOperatorFactory.create('rds.db_cluster', region_name)
        
        # RDSのDB clusterを作成する
        db_cluster_id = 'rds_cluster_test01'
        engine_name = 'postgres'
        username = 'postgres'
        password = 'password@123'
        logging.info(f'Creating RDS DB Cluster: {db_cluster_id} ...')
        aws_test_utils.create_db_cluster(db_cluster_id, engine_name, username,
                password, region_name)
        status = operator.get_status(db_cluster_id)
        logging.info(f'RDS DB Cluster: {db_cluster_id} {status}')
        
        # 実行中のRDS DB cluster１つのIDを指定して、stop_resourcesメソッドを
        # 実行する。
        logging.info(f'Stopping RDS DB Cluster: {db_cluster_id} ...')
        count = operator.stop_resources([db_cluster_id])
        # => 停止操作したRDS DB cluserの個数は1であること。
        self.assertEqual(count, 1)
        status = operator.get_status(db_cluster_id)
        logging.info(f'RDS DB Cluster: {db_cluster_id} {status}')
        statuses = [status]
        # => RDS DB instanceのステータスが「stopping」または「stopped」で
        # あること。
        self.assertTrue(statuses.count('stopping') + statuses.count('stopped') > 0)
        
        # 停止中のRDS DB cluster１つのIDを指定して、stop_resourcesメソッドを
        # 実行する。
        logging.info(f'Stopping RDS DB Cluster: {db_cluster_id} ...')
        count = operator.stop_resources([db_cluster_id])
        # => 停止操作したRDS DB cluserの個数は0であること。
        self.assertEqual(count, 0)
        status = operator.get_status(db_cluster_id)
        logging.info(f'RDS DB Cluster: {db_cluster_id} {status}')
        statuses = [status]
        # => RDS DB instanceのステータスが「stopping」または「stopped」で
        # あること。
        self.assertTrue(statuses.count('stopping') + statuses.count('stopped') > 0)
        
        # 停止中のRDS DB cluster１つのIDを指定して、start_resourcesメソッドを
        # 実行する。
        logging.info(f'Starting RDS DB Cluster: {db_cluster_id} ...')
        count = operator.start_resources([db_cluster_id])
        # => 開始操作したRDS DB clusterの個数が１であること。
        self._baseAssertEqual(count, 1)
        status = operator.get_status(db_cluster_id)
        logging.info(f'RDS DB Cluster: {db_cluster_id} {status}')
        # => RDS DB clusterのステータスがavailableであること。
        self.assertEqual(status, 'available')
        
        # 実行中のRDS DB cluster１つのIDを指定して、start_resourcesメソッドを
        # 実行する。
        logging.info(f'Starting RDS DB Cluster: {db_cluster_id} ...')
        count = operator.start_resources([db_cluster_id])
        # => 開始操作したRDS DB clusterの個数が０であること。
        self._baseAssertEqual(count, 0)
        status = operator.get_status(db_cluster_id)
        logging.info(f'RDS DB Cluster: {db_cluster_id} {status}')
        # => RDS DB clusterのステータスがavailableであること。
        self.assertEqual(status, 'available')
        
        logging.info('<<<<< test_start_stop_resources end')
    
    @mock_rds
    def test_error_start_stop(self):
        '''存在しないRDS DB clusterのIDを指定して、startメソッド、stopメソッドのテストを実行します。
        
        テスト内容は、以下のとおりです。
        
        * 存在しないのRDS DB clusterのIDを指定して、stopメソッドを実行する。
            * => 例外が発生すること。
        * 存在しないのRDS DB clusterのIDを指定して、startメソッドを開始する。
            * => 例外が発生すること。
        
        '''
        logging.info('>>>>> test_error_start_stop start')
        
        region_name = 'ap-northeast-1'
        # AwsRdsDbClusterOperator クラスのインスタンスを作成する
        operator = AwsResourceOperatorFactory.create('rds.db_cluster', region_name)
        
        # 存在しないRDSのDB cluster ID
        db_cluster_id = 'rds_cluster_error'
        
        # 存在しないのRDS DB clusterのIDを指定して、stopメソッドを実行する。
        logging.info(f'Stopping RDS DB Cluster: {db_cluster_id} ...')
        with self.assertRaises(Exception) as cm:
            operator.stop(db_cluster_id)
        # => 例外が発生すること。
        logging.info(str(cm.exception))
        
        # 存在しないのRDS DB clusterのIDを指定して、startメソッドを開始する。
        logging.info(f'Starting RDS DB Cluster: {db_cluster_id} ...')
        with self.assertRaises(Exception) as cm:
            operator.start(db_cluster_id)
        # => 例外が発生すること。
        logging.info(str(cm.exception))
        
        logging.info('<<<<< test_error_start_stop end')
    
    @mock_rds
    def test_error_start_stop_resources(self):
        '''存在しないRDS DB ClusterのIDを含むRDS DB clusterの配列を指定してstart_resourcesメソッド、stop_resourcesメソッドのテストを実行します。
        
        テストの内容は、以下のとおりです。

        * 存在しないRDS DB cliuster１つと実行中のRDS DB cluster１つのIDを指定
          して、stop_resourcesメソッド実行する。
            * => 例外が発生すること。
            * => 存在するRDS DB instanceのステータスが「stopping」または「stopped」
              であること。
        * 存在しないRDS DB cliuster１つと停止中のRDS DB cluster１つのIDを指定
          して、stop_resourcesメソッドを実行する。
            * => 例外が発生すること。
            * => 存在するRDS DB instanceのステータスが「stopping」または「stopped」
              であること。
        * 存在しないRDS DB cliuster１つと停止中のRDS DB cluster１つのIDを指定
          して、start_resourcesメソッドを実行する。
            * => 例外が発生すること。
            * => 存在するRDS DB instanceのステータスがavailableであること。
        * 存在しないRDS DB cliuster１つと実行中のRDS DB cluster１つのIDを指定
          して、start_resourcesメソッドを実行する。
            * => 例外が発生すること。
            * => RDS DB clusterのステータスがavailableであること。
        
        '''
        logging.info('>>>>> test_error_start_stop_resources start')
        
        region_name = 'ap-northeast-1'
        # AwsRdsDbClusterOperator クラスのインスタンスを作成する
        operator = AwsResourceOperatorFactory.create('rds.db_cluster', region_name)
        
        # RDSのDB clusterを作成する
        db_cluster_id_ok = 'rds_cluster_test01'
        engine_name = 'postgres'
        username = 'postgres'
        password = 'password@123'
        logging.info(f'Creating RDS DB Cluster: {db_cluster_id_ok} ...')
        aws_test_utils.create_db_cluster(db_cluster_id_ok, engine_name, username,
                password, region_name)
        
        # 存在しない RDSのDB cluster ID
        db_cluster_id_ng = 'rds_cluster_error'
        
        # 存在しないRDS DB cliuster１つと実行中のRDS DB cluster１つのIDを指定
        # して、stop_resourcesメソッド実行する。
        logging.info(f'Stopping RDS DB Cluster: {[db_cluster_id_ng, db_cluster_id_ok]} ...')
        with self.assertRaises(Exception) as cm:
            operator.stop_resources([db_cluster_id_ng, db_cluster_id_ok])
        # => 例外が発生すること。
        logging.info(str(cm.exception))
        status = operator.get_status(db_cluster_id_ok)
        logging.info(f'RDS DB Cluster: {db_cluster_id_ok} {status}')
        statuses = [status]
        # => 存在するRDS DB instanceのステータスが「stopping」または「stopped」
        # であること。
        self.assertTrue(statuses.count('stopping') + statuses.count('stopped') > 0)
        
        # 存在しないRDS DB cliuster１つと停止中のRDS DB cluster１つのIDを指定
        # して、stop_resourcesメソッドを実行する。
        logging.info(f'Stopping RDS DB Cluster: {[db_cluster_id_ng, db_cluster_id_ok]} ...')
        with self.assertRaises(Exception) as cm:
            operator.stop_resources([db_cluster_id_ng, db_cluster_id_ok])
        # => 例外が発生すること。
        logging.info(str(cm.exception))
        status = operator.get_status(db_cluster_id_ok)
        logging.info(f'RDS DB Cluster: {db_cluster_id_ok} {status}')
        statuses = [status]
        # => 存在するRDS DB instanceのステータスが「stopping」または「stopped」
        # であること。
        self.assertTrue(statuses.count('stopping') + statuses.count('stopped') > 0)
        
        # 存在しないRDS DB cliuster１つと停止中のRDS DB cluster１つのIDを指定
        # して、start_resourcesメソッドを実行する。
        logging.info(f'Starting RDS DB Cluster: {[db_cluster_id_ng, db_cluster_id_ok]} ...')
        with self.assertRaises(Exception) as cm:
            operator.start_resources([db_cluster_id_ng, db_cluster_id_ok])
        # => 例外が発生すること。
        logging.info(str(cm.exception))
        status = operator.get_status(db_cluster_id_ok)
        logging.info(f'RDS DB Cluster: {db_cluster_id_ok} {status}')
        # => 存在するRDS DB instanceのステータスがavailableであること。
        self.assertEqual(status, 'available')
        
        # 存在しないRDS DB cliuster１つと実行中のRDS DB cluster１つのIDを指定
        # して、start_resourcesメソッドを実行する。
        logging.info(f'Starting RDS DB Cluster: {[db_cluster_id_ng, db_cluster_id_ok]} ...')
        with self.assertRaises(Exception) as cm:
            operator.start_resources([db_cluster_id_ng, db_cluster_id_ok])
        # => 例外が発生すること。
        logging.info(str(cm.exception))
        status = operator.get_status(db_cluster_id_ok)
        logging.info(f'RDS DB Cluster: {db_cluster_id_ok} {status}')
        # => RDS DB clusterのステータスがavailableであること。
        self.assertEqual(status, 'available')
        
        logging.info('<<<<< test_error_start_stop_resources end')

if __name__ == '__main__':
    html_runner = HtmlTestRunner.HTMLTestRunner(
            output=os.path.dirname(__file__) + '/../target/site/test-report',
            add_timestamp=False)
    unittest.main(testRunner=html_runner)

# -*- config: utf-8 -*-
'''AwsRdsClusterOperatorTest module.

Copyright: ycookjp

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
    '''
    
    AwsRdsClusterOperator クラス用のテストクラス
    
    '''
    @classmethod
    def setUpClass(cls):
        '''
        
        テストクラスの set up を実行します。
        
        Args:
            cls: テストクラスのインスタンス
        
        '''
        logging.info('Set up test class.')

    @classmethod
    def tearDownClass(cls):
        '''
        
        テストクラスの tear down を実行します。
        
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
    def _create_db_cluster(self, db_cluster_id, engine_name, username, password,
                           region_name):
        rds = boto3.client('rds', region_name=region_name)
        db_cluster = rds.create_db_cluster(DBClusterIdentifier=db_cluster_id,
                Engine=engine_name, MasterUsername=username, MasterUserPassword=password)
        return db_cluster
    
    @mock_rds
    def test_start_stop(self):
        logging.info('>>>>> test_start_stop start')
        
        region_name = 'ap-northeast-1'
        # AwsRdsDbClusterOperator クラスのインスタンスを作成する
        operator = AwsResourceOperatorFactory.create('rds.db_cluster', region_name)
        
        # RDSのDB clusterを作成する
        db_cluster_id = 'rds_cluster_test01'
        engine_name = 'postgres'
        username = 'postgres'
        password = 'password@123'
        logging.info(f'Creating RDS DB Cluster {db_cluster_id} ...')
        self._create_db_cluster(db_cluster_id, engine_name,
                                username, password, region_name)
        status = operator.get_status(db_cluster_id)
        logging.info(f'RDS DB Cluster: {db_cluster_id} {status}')
        
        # RDS DB clusterを停止する
        logging.info(f'Stopping RDS DB Cluster {db_cluster_id} ...')
        operator.stop(db_cluster_id)
        status = operator.get_status(db_cluster_id)
        logging.info(f'RDS DB Cluster: {db_cluster_id} {status}')
        statuses = [status]
        self.assertTrue(statuses.count('stopping') + statuses.count('stopped') > 0)
        
        # RDS DB clusterを開始する
        logging.info(f'Starting RDS DB Cluster {db_cluster_id} ...')
        operator.start(db_cluster_id)
        status = operator.get_status(db_cluster_id)
        logging.info(f'RDS DB Cluster: {db_cluster_id} {status}')
        self.assertEqual(status, 'available')
        
        logging.info('<<<<< test_start_stop end')
    
    @mock_rds
    def test_start_stop_resources(self):
        logging.info('>>>>> test_start_stop_resources start')
        
        region_name = 'ap-northeast-1'
        # AwsRdsDbClusterOperator クラスのインスタンスを作成する
        operator = AwsResourceOperatorFactory.create('rds.db_cluster', region_name)
        
        # RDSのDB clusterを作成する
        db_cluster_id = 'rds_cluster_test01'
        engine_name = 'postgres'
        username = 'postgres'
        password = 'password@123'
        logging.info(f'Creating RDS DB Cluster {db_cluster_id} ...')
        self._create_db_cluster(db_cluster_id, engine_name, username, password,
                                region_name)
        status = operator.get_status(db_cluster_id)
        logging.info(f'RDS DB Cluster: {db_cluster_id} {status}')
        
        # RDS DB clusterを停止する
        logging.info(f'Stopping RDS DB Cluster {db_cluster_id} ...')
        operator.stop_resources([db_cluster_id])
        status = operator.get_status(db_cluster_id)
        logging.info(f'RDS DB Cluster: {db_cluster_id} {status}')
        statuses = [status]
        self.assertTrue(statuses.count('stopping') + statuses.count('stopped') > 0)
        
        # RDS DB clusterを開始する
        logging.info(f'Starting RDS DB Cluster {db_cluster_id} ...')
        operator.start_resources([db_cluster_id])
        status = operator.get_status(db_cluster_id)
        logging.info(f'RDS DB Cluster: {db_cluster_id} {status}')
        self.assertEqual(status, 'available')
        
        logging.info('<<<<< test_start_stop_resources end')

    @mock_rds
    def test_start_stop_resource_with_config(self):
        logging.info('>>>>> test_start_stop_resource_with_config start')
        
        # RDSのDB clusterを作成する
        yaml_config = aws_test_utils.load_yaml(__file__)
        region_name = yaml_config['region_name']
        access_key = yaml_config['access_key_id']
        secret_key = yaml_config['secret_access_key']
        configkey = 'db_cluster_resources'
        operator = AwsResourceOperatorFactory.create(
                yaml_config[configkey][0]['type'], region_name)
        
        db_cluster_ids = yaml_config[configkey][0]['ids']
        for db_cluster_id in db_cluster_ids:
            engine_name = 'postgres'
            username = 'postgres'
            password = 'password@123'
            logging.info(f'Creating RDS DB Cluster {db_cluster_id} ...')
            self._create_db_cluster(db_cluster_id, engine_name,
                                    username, password, region_name)
            status = operator.get_status(db_cluster_id)
            logging.info(f'RDS DB Cluster: {db_cluster_id} {status}')

        # RDSのDB clusterを停止する
        event = {"action": "stop", "configKey": configkey}
        aws_resource_start_stop.start_stop_aws_resources(event, None, True, __file__)
        # DB clusterのステータスが stopping であること
        for db_cluster_id in db_cluster_ids:
            self.assertEqual(operator.get_status(db_cluster_id), 'stopped')
        
        logging.info('<<<<< test_start_stop_resource_with_config end')

if __name__ == '__main__':
    html_runner = HtmlTestRunner.HTMLTestRunner(
            output=os.path.dirname(__file__) + '/../target/site/test-report',
            add_timestamp=False)
    unittest.main(testRunner=html_runner)

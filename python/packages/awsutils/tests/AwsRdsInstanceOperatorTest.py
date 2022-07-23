# -*- config: utf-8 -*-
'''AwsRdsInstanceOperatorTest module.

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

class AwsRdsInstanceOperatorTest(unittest.TestCase):
    '''
    
    AwsRdsInstanceOperator クラス用のテストクラス
    
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
    def _create_db_instance(self, db_instance_id, resource_type, engine_name,
                            username, password, region_name):
        rds = boto3.client('rds', region_name=region_name)
        db_instance = rds.create_db_instance(DBInstanceIdentifier=db_instance_id,
                DBInstanceClass=resource_type,
                Engine=engine_name, MasterUsername=username, MasterUserPassword=password)
        return db_instance
    
    @mock_rds
    def test_start_stop(self):
        logging.info('>>>>> test_start_stop start')
        
        region_name = 'ap-northeast-1'
        # AwsRdsDbCInstanceOperator クラスのインスタンスを作成する
        operator = AwsResourceOperatorFactory.create('rds.db_instance', region_name)
        
        # RDSのDB instanceを作成する
        db_instance_id = 'rds_instance_test01'
        resource_type = 'db.t2.micro'
        engine_name = 'postgres'
        username = 'postgres'
        password = 'password@123'
        self._create_db_instance(db_instance_id, resource_type, engine_name,
                                 username, password, region_name)
        status = operator.get_status(db_instance_id)
        logging.info(f'RDS DB Instance: {db_instance_id} {status}')
        
        # RDS DB instanceを停止する
        operator.stop(db_instance_id)
        status = operator.get_status(db_instance_id)
        logging.info(f'RDS DB Instance: {db_instance_id} {status}')
        statuses = [status]
        self.assertTrue(statuses.count('stopping') + statuses.count('stopped') > 0)
        
        # RDS DB instanceを開始する
        operator.start(db_instance_id)
        status = operator.get_status(db_instance_id)
        logging.info(f'RDS DB Instance: {db_instance_id} {status}')
        self.assertEqual(status, 'available')
        
        logging.info('<<<<< test_start_stop end')
    
    @mock_rds    
    def test_start_stop_resources(self):
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
        self._create_db_instance(db_instance_id, resource_type, engine_name,
                                 username, password, region_name)
        status = operator.get_status(db_instance_id)
        logging.info(f'RDS DB Instance: {db_instance_id} {status}')
        
        # RDS DB instanceを停止する
        operator.stop_resources([db_instance_id])
        status = operator.get_status(db_instance_id)
        logging.info(f'RDS DB Instance: {db_instance_id} {status}')
        statuses = [status]
        self.assertTrue(statuses.count('stopping') + statuses.count('stopped') > 0)
        
        # RDS DB instanceを開始する
        operator.start_resources([db_instance_id])
        status = operator.get_status(db_instance_id)
        logging.info(f'RDS DB Instance: {db_instance_id} {status}')
        self.assertEqual(status, 'available')
        
        logging.info('<<<<< test_start_stop_resources end')

    @mock_rds
    def test_start_stop_resource_with_config(self):
        logging.info('>>>>> test_start_stop_resource_with_config start')
        
        # RDSのDB instanceを作成する
        yaml_config = aws_test_utils.load_yaml(__file__)
        region_name = yaml_config['region_name']
        access_key = yaml_config['access_key_id']
        secret_key = yaml_config['secret_access_key']
        configkey = 'db_instance_resources'
        operator = AwsResourceOperatorFactory.create(yaml_config[configkey][0]['type'], region_name)
        
        db_instance_ids = yaml_config[configkey][0]['ids']
        for db_instance_id in db_instance_ids:
            resource_type = 'db.t2.micro'
            engine_name = 'postgres'
            username = 'postgres'
            password = 'password@123'
            self._create_db_instance(db_instance_id, resource_type, engine_name,
                                     username, password, region_name)
            status = operator.get_status(db_instance_id)
            logging.info(f'RDS DB Instance: {db_instance_id} {status}')

        # RDSのDB instanceを停止する
        event = {"action": "stop", "configKey": configkey}
        aws_resource_start_stop.start_stop_aws_resources(event, None, True, __file__)
        # DB instanceのステータスが stopping であること
        for db_instance_id in db_instance_ids:
            self.assertEqual(operator.get_status(db_instance_id), 'stopped')
        
        logging.info('<<<<< test_start_stop_resource_with_config end')

if __name__ == '__main__':
    html_runner = HtmlTestRunner.HTMLTestRunner(
            output=os.path.dirname(__file__) + '/../target/site/test-report',
            add_timestamp=False)
    unittest.main(testRunner=html_runner)

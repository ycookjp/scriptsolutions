# -*- config: utf-8 -*-
'''AwsEc2StartStopTest module.

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
import aws_test_utils
import boto3
from moto import mock_ec2
from moto import mock_rds
from unittest.case import TestCase
import time
import yaml
from awsutils.aws_resource_operator import AwsResourceOperatorFactory

root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class MyContext():
    '''テスト用の context オブジェクト
    
    '''
    function_name = None

class AwsEc2InstanceOperatorTest(unittest.TestCase):
    '''aws_resource_start_stop モジュール用のテストクラス
    
    '''
    # event から情報を取得するかどうかの定数
    _use_event = True
    
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
    
    def _set_use_event(self, use_event):
        '''
        aws_resource_start_stop モジュールの start_stop_aws_resources 関数実行に
        情報を event から取得するかどうかの設定をします。
        
        Args:
            use_event (boolean): インスタンスの銃砲取得元が event の場合は
                    True、contextの場合は False を指定します
        '''
        self._use_event = use_event
    
    def _dump_config_workfile(self, config: dict, replace_map: dict,
                              workfile_path: str):
        '''yaml形式の設定ファイルのインスタンスIDを置き換えて、作業ファイルに保存します。
        
        Args:
            config (dict): yaml形式の設定ファイルの内容を格納したdictionary
            replace_map (dict): 置換対象のインスタンスIDと置換後のインスタンスID
                の情報を設定したdictionary。dictionaryのキーと値は以下のように
                設定します。
                * キー: configKey
                * 値: 以下のキーと値を持つDictionary
                    * キー: <type>:<置換対象のインスタンスID> の形式の文字列
                    * 値: <置換後のインスタンスID>
            workfile_path (str): 作業ファイルのパス
        
        '''
        # configの内容をスキャンする
        for configkey in list(replace_map):
            replace_info = replace_map.get(configkey)
            resource_groups = config.get(configkey)
            for resource_group in resource_groups:
                resource_type = resource_group.get('type')
                replaced_ids = []
                for id in resource_group.get('ids'):
                    replaced_id = replace_info.get(f'{resource_type}:{id}')
                    if replaced_id != None:
                        replaced_ids.append(replaced_id)
                    else:
                        replaced_ids.append(id)
                resource_group['ids'] = replaced_ids
        
        aws_test_utils.dump_yaml(config, workfile_path)
    
    def setUp(self):
        '''テスト関数の set up を実行します。
        
        '''
        logging.info('Set up test.')
    
    def tearDown(self):
        '''テストクラスの tear down を実行します。
        
        '''
        logging.info('Tear down test.')
    
    def test_load_config(self):
        '''_load_config 関数のテストを実行します。
        
        * 設定ファイルのキーを指定して読み込んだ AwsResourceStartStopConfig
          オブジェクトの内容が設定ファイルの内容と一致すること
        
        * 設定ファイルのキー配列を指定して読み込んだ AwsResourceStartStopConfig
          オブジェクトの内容が設定ファイルの内容と一致すること
        
        '''
        logging.info('>>>>> test_load_config start')
        
        # 設定ファイルのキーを指定して読み込んだ AwsResourceStartStopConfig
        # オブジェクトの内容が設定ファイルの内容と一致すること
        config = aws_resource_start_stop._load_config(__file__, 'test02_ng')
        self.assertEqual(config.region_name, 'ap-northeast-1')
        # 設定ファイルのキー配列を指定して読み込んだ AwsResourceStartStopConfig
        # オブジェクトの内容が設定ファイルの内容と一致すること
        resource_types = config.resource_groups
        ## ec2.instance
        self.assertEqual(resource_types[0].get('type'), 'ec2.instance')
        self.assertEqual(resource_types[0].get('ids'), ['i-ngngngngngngngng_', 'i-xxxxxxxxxxxxxxxxx'])
        ## rds.db_cluster
        self.assertEqual(resource_types[1].get('type'), 'rds.db_cluster')
        self.assertEqual(resource_types[1].get('ids'), ['myrds_clusterng', 'myrds_cluster01'])
        ## rds.db_instance
        self.assertEqual(resource_types[2].get('type'), 'rds.db_instance')
        self.assertEqual(resource_types[2].get('ids'), ['myrds_instanceng', 'myrds_instance01'])
        
        logging.info('<<<<< test_load_config end')
    
    def test_error_load_config(self):
        '''_load_config 関数のエラーが発生する場合のテストを実行します。
        
        * 設定ファイルに存在しないキー名を指定するとエラーとなること
        
        '''
        logging.info('>>>>> test_error_load_config start')
        
        # 設定ファイルに存在しないキー名を指定するとエラーとなること
        with self.assertRaises(Exception):
            config = aws_resource_start_stop._load_config(__file__, 'key_not_exists')
        
        logging.info('<<<<< test_error_load_config end')
    
    def test_get_action_from_context(self):
        '''_get_action_from_context 関数をテストします。
        
        * contextオブジェクトのfunction_nameプロパティに'ec2_start_test01_ok'
          を指定すると、'start'が返される
        
        * contextオブジェクトのfunction_nameプロパティに
          'ec2_stop_resources_test_ok' を指定すると、'stop'が返される
        
        '''
        logging.info('>>>>> test_get_action_from_context start')
        
        context = MyContext()
        
        # Lambda関数名に'start'を指定
        context.function_name = 'ec2_start_test01_ok'
        action_name = aws_resource_start_stop._get_action_from_context(context)
        self.assertEqual(action_name, 'start')
        
        # Lambda関数名にstopを指定
        context.function_name = 'ec2_stop_resources_test_ok'
        action_name = aws_resource_start_stop._get_action_from_context(context)
        self.assertEqual(action_name, 'stop')
        
        logging.info('<<<<< test_get_action_from_context end')
    
    def test_get_action_from_event(self):
        '''_get_action_from_event 関数をテストします。
        
        * event dictionary のキー：action の値 に 'start' を指定すると、
          'start'が返される
        
        * event dictionary のキー：action の値に 'stop' を指定すると、
          'stop'が返される
        
        '''
        logging.info('>>>>> test_get_action_from_event start')
        
        # event dictionary のキー：action の値に'start'を指定
        event = {"action": "start", "configKey": "test01_ok"}
        action_name = aws_resource_start_stop._get_action_from_event(event)
        self.assertEqual(action_name, 'start')
        
        # event dictionary のキー：action の値に'stop'を指定
        event = {"action": "stop", "configKey": "resources_test_ok"}
        action_name = aws_resource_start_stop._get_action_from_event(event)
        self.assertEqual(action_name, 'stop')
        
        logging.info('<<<<< test_get_action_from_event end')

    def test_get_configkey_from_context(self):
        '''_get_configkey_from_context 関数をテストします。
        
        * contextオブジェクトのfunction_nameプロパティに
          'ec2_start_resources01' を指定すると、'resources01'が返される
        
        * contextオブジェクトのfunction_nameプロパティに'ec2_start_test01_ok'
          を指定すると、'test01_ok'が返される
  
        '''
        logging.info('>>>>> test_get_configkey_from_context start')
        
        context = MyContext()
        
        # Lambda関数名のキー名に「resources01」を指定
        context.function_name = 'ec2_start_resources01'
        configkey = aws_resource_start_stop._get_configkey_from_context(context)
        self.assertEqual(configkey, 'resources01')
        
        # Lambda関数名のキー名に「test01_ok」を指定
        context.function_name = 'ec2_start_test01_ok'
        configkey = aws_resource_start_stop._get_configkey_from_context(context)
        self.assertEqual(configkey, 'test01_ok')
        
        logging.info('<<<<< test_get_configkey_from_context end')

    def test_get_configkey_from_event(self):
        '''_get_configkey_from_event 関数をテストします。
        
        * event dictionary の キー：configKey の値に 'resources01' を
          設定すると、'resources01'が返される
        
        * event dictionary の キー：configKey の値に 'test01_ok' を
          指定すると、'test01_ok'が返される
  
        '''
        logging.info('>>>>> test_get_configkey_from_event start')
        
        # event dictionary のキー：configKey の値に「resources01」を指定
        event = {"action": "sstart", "configKey": "resources01"}
        configkey = aws_resource_start_stop._get_configkey_from_event(event)
        self.assertEqual(configkey, 'resources01')
        
        # event dictionary のキー：configKey の値に「test01_ok」を指定
        event = {"action": "sstart", "configKey": "test01_ok"}
        configkey = aws_resource_start_stop._get_configkey_from_event(event)
        self.assertEqual(configkey, 'test01_ok')
        
        logging.info('<<<<< test_get_configkey_from_event end')
    
    @mock_ec2
    @mock_rds
    def test01_ok_event_start_stop_aws_resources(self):
        '''configKeyにtest01_okを設定して、start_stop_aws_resources関数のテストを実行します。
        
        テストの内容は、以下のとおりです。
        
        * EC2インスタンスとDBCクラスターが実行中の状態で、イベントにtest01_okの
          停止を指定して、start_stop_aws_resources関数を実行する。
            * => EC2インスタンスが停止していること。
            * => RDS DB Clusterが停止していること。
        * EC2インスタンスとDBCクラスターが停止中の状態で、イベントにtest01_okの
          開始を指定して、start_stop_aws_resources関数を実行する。
            * => EC2インスタンスが開始していること。
            * => RDS DB Clusterが開始していること。
        
        '''
        logging.info('>>>>> test01_ok_event_start_stop_aws_resources start')
        
        ##### テストの準備 #####
        configkey = 'test01_ok'
        # テスト用の設定ファイルを読み込む
        config_root = aws_test_utils.load_yaml(__file__)
        region_name = config_root['region_name']
        access_key = config_root['access_key_id']
        secret_key = config_root['secret_access_key']
        config = config_root[configkey]
        
        # インスタンスのステータス確認用にAWSResourceOperatorのインスタンスを取得する。
        ec2_operator = AwsResourceOperatorFactory.create('ec2.instance', region_name)
        dbc_operator = AwsResourceOperatorFactory.create('rds.db_cluster', region_name)
        dbi_operator = AwsResourceOperatorFactory.create('rds.db_instance', region_name)
        
        # ec2インスタンスを１つ開始する。
        ami_id = 'ami-test01ok'
        ec2_instances = aws_test_utils.run_instances(ami_id, region_name, 1)
        ec2_instance_01 = ec2_instances[0]['InstanceId']
        logging.info(f'EC2: {ec2_instance_01}, status: {ec2_operator.get_status(ec2_instance_01)}')
        
        # RDS DBクラスタを１つ開始する。
        engine_name = 'postgres'
        username = 'postgres'
        password = 'password@123'
        db_cluster_id = config[1]['ids'][0]
        aws_test_utils.create_db_cluster(db_cluster_id, engine_name, username,
                password, region_name)
        logging.info(f'DB Cluster: {db_cluster_id}, status: {dbc_operator.get_status(db_cluster_id)}')
        
        # インスタンスIDを置換して作業ディレクトリに保存する。
        mapping_info = dict()
        mapping_info['ec2.instance:i-xxxxxxxxxxxxxxxxx'] = ec2_instance_01
        temp_file = os.path.join(os.path.dirname(__file__), 'work',
                                 os.path.basename(__file__))
        self._dump_config_workfile(config_root, {configkey: mapping_info}, temp_file)
        
        ##### テスト開始 #####
        # EC2インスタンスとDBCクラスターが実行中の状態で、イベントにtest01_okの
        # 停止を指定して、start_stop_aws_resources関数を実行する。
        event = {"action": "stop", "configKey": configkey}
        context = MyContext()
        # start_stop_aws_resources関数を実行する。
        aws_resource_start_stop.start_stop_aws_resources(event, context, script_path=temp_file)
        # => EC2インスタンスが停止していること
        status = ec2_operator.get_status(ec2_instance_01)
        self._baseAssertEqual(status, 'stopped')
        # => RDS DB Clusterが停止していること。
        status = dbc_operator.get_status(db_cluster_id)
        self._baseAssertEqual(status, 'stopped')
        
        # EC2インスタンスとDBCクラスターが停止中の状態で、イベントにtest01_okの
        # 開始を指定して、start_stop_aws_resources関数を実行する。
        event = {"action": "start", "configKey": configkey}
        context = MyContext()
        # start_stop_aws_resources関数を実行する。
        aws_resource_start_stop.start_stop_aws_resources(event, context, script_path=temp_file)
        # => EC2インスタンスが開始していること。
        status = ec2_operator.get_status(ec2_instance_01)
        self._baseAssertEqual(status, 'running')
        # => RDS DB Clusterが開始していること。
        status = dbc_operator.get_status(db_cluster_id)
        self._baseAssertEqual(status, 'available')
        
        logging.info('<<<<< test01_ok_event_start_stop_aws_resources end')
    
    @mock_ec2
    @mock_rds
    def test01_ng_event_start_stop_aws_resources(self):
        '''configKeyにtest01_ngを設定して、start_stop_aws_resources関数のテストを実行します。
        
        テストの内容は、以下のとおりです。
        
        * 設定ファイルに、EC2インスタンスとDBクラスターが実行中のインスタンス
          IDと存在しないインスタンスIDが設定されている状態で、イベントに
          test01_ngの停止を指定して、start_stop_aws_resources関数を実行する。
            * => 例外が発生すること。
            * => EC2インスタンスが停止していること。
            * => RDS DB Clusterが停止していること。
        * 設定ファイルに、EC2インスタンスとDBクラスターが停止中のインスタンス
          IDと存在しないインスタンスIDが設定されている状態で、イベントに
          test01_ngの開始を指定して、start_stop_aws_resources関数を実行する。
            * => 例外が発生すること。
            * => EC2インスタンスが開始していること。
            * => RDS DB Clusterが開始していること。
        
        '''
        logging.info('>>>>> test01_ng_event_start_stop_aws_resources start')
        
        ##### テストの準備 #####
        configkey = 'test01_ng'
        # テスト用の設定ファイルを読み込む
        config_root = aws_test_utils.load_yaml(__file__)
        region_name = config_root['region_name']
        access_key = config_root['access_key_id']
        secret_key = config_root['secret_access_key']
        config = config_root[configkey]
        
        # インスタンスのステータス確認用にAWSResourceOperatorのインスタンスを取得する。
        ec2_operator = AwsResourceOperatorFactory.create('ec2.instance', region_name)
        dbc_operator = AwsResourceOperatorFactory.create('rds.db_cluster', region_name)
        dbi_operator = AwsResourceOperatorFactory.create('rds.db_instance', region_name)
        
        # ec2インスタンスを１つ開始する。
        ami_id = 'ami-test01ok'
        ec2_instances = aws_test_utils.run_instances(ami_id, region_name, 1)
        ec2_instance_01 = ec2_instances[0]['InstanceId']
        logging.info(f'EC2: {ec2_instance_01}, status: {ec2_operator.get_status(ec2_instance_01)}')
        
        # RDS DBクラスタを１つ開始する。
        engine_name = 'postgres'
        username = 'postgres'
        password = 'password@123'
        db_cluster_id = config[1]['ids'][1]
        aws_test_utils.create_db_cluster(db_cluster_id, engine_name, username,
                password, region_name)
        logging.info(f'DB Cluster: {db_cluster_id}, status: {dbc_operator.get_status(db_cluster_id)}')
        
        # インスタンスIDを置換して作業ディレクトリに保存する。
        mapping_info = dict()
        mapping_info['ec2.instance:i-xxxxxxxxxxxxxxxxx'] = ec2_instance_01
        temp_file = os.path.join(os.path.dirname(__file__), 'work',
                                 os.path.basename(__file__))
        self._dump_config_workfile(config_root, {configkey: mapping_info}, temp_file)
        
        ##### テスト開始 #####
        # 設定ファイルに、EC2インスタンスとDBクラスターが実行中のインスタンス
        # IDと存在しないインスタンスIDが設定されている状態で、イベントに
        # test01_ngの停止を指定して、start_stop_aws_resources関数を実行する。
        event = {"action": "stop", "configKey": configkey}
        context = MyContext()
        with self.assertRaises(Exception) as cm:
            # start_stop_aws_resources関数を実行する。
            aws_resource_start_stop.start_stop_aws_resources(event, context,
                    script_path=temp_file)
        # =>例外が発生すること
        logging.info(f'Exception: {str(cm.exception)}')
        # => EC2インスタンスが停止していること
        status = ec2_operator.get_status(ec2_instance_01)
        self._baseAssertEqual(status, 'stopped')
        # => RDS DB Clusterが停止していること。
        status = dbc_operator.get_status(db_cluster_id)
        self._baseAssertEqual(status, 'stopped')
        
        # 設定ファイルに、EC2インスタンスとDBクラスターが停止中のインスタンス
        # IDと存在しないインスタンスIDが設定されている状態で、イベントに
        # test01_ngの開始を指定して、start_stop_aws_resources関数を実行する。
        event = {"action": "start", "configKey": configkey}
        context = MyContext()
        with self.assertRaises(Exception) as e:
            # start_stop_aws_resources関数を実行する。
            aws_resource_start_stop.start_stop_aws_resources(event, context,
                    script_path=temp_file)
        # => 例外が発生すること
        logging.info(f'Exception: {str(cm.exception)}')
        # => EC2インスタンスが開始していること。
        status = ec2_operator.get_status(ec2_instance_01)
        self._baseAssertEqual(status, 'running')
        # => RDS DB Clusterが開始していること。
        status = dbc_operator.get_status(db_cluster_id)
        self._baseAssertEqual(status, 'available')
        
        logging.info('<<<<< test01_ng_event_start_stop_aws_resources end')
    
    @mock_ec2
    @mock_rds
    def test02_ok_event_start_stop_aws_resources(self):
        '''configKeyにtest02_okを設定して、start_stop_aws_resources関数のテストを実行します。
        
        テストの内容は、以下のとおりです。
        
        * EC2インスタンスとDBCインスタンスが実行中の状態で、コンテキストの
          Lambda関数名に「ec2_stop_test02_ok」を指定して、
          start_stop_aws_resources関数を実行する。
            * => EC2インスタンスが停止していること。
            * => RDS DB Clusterが停止していること。
        * EC2インスタンスとDBCインスタンスが停止中の状態で、コンテキストの
          Lambda関数名に「ec2_stop_test02_ok」を指定して、
          start_stop_aws_resources関数を実行する。
            * => EC2インスタンスが開始していること。
            * => RDS DB Clusterが開始していること。
        
        '''
        logging.info('>>>>> test02_ok_event_start_stop_aws_resources start')
        
        ##### テストの準備 #####
        configkey = 'test02_ok'
        # テスト用の設定ファイルを読み込む
        config_root = aws_test_utils.load_yaml(__file__)
        region_name = config_root['region_name']
        access_key = config_root['access_key_id']
        secret_key = config_root['secret_access_key']
        config = config_root[configkey]
        
        # インスタンスのステータス確認用にAWSResourceOperatorのインスタンスを取得する。
        ec2_operator = AwsResourceOperatorFactory.create('ec2.instance', region_name)
        dbc_operator = AwsResourceOperatorFactory.create('rds.db_cluster', region_name)
        dbi_operator = AwsResourceOperatorFactory.create('rds.db_instance', region_name)
        
        # ec2インスタンスを２つ開始する。
        ami_id = 'ami-test01ok'
        ec2_instances = aws_test_utils.run_instances(ami_id, region_name, 2)
        ec2_instance_01 = ec2_instances[0]['InstanceId']
        logging.info(f'EC2: {ec2_instance_01}, status: {ec2_operator.get_status(ec2_instance_01)}')
        ec2_instance_02 = ec2_instances[1]['InstanceId']
        logging.info(f'EC2: {ec2_instance_02}, status: {ec2_operator.get_status(ec2_instance_02)}')
        
        # RDS DBインスタンスを１つ開始する。
        resource_type = 'db.t2.micro'
        engine_name = 'postgres'
        username = 'postgres'
        password = 'password@123'
        db_instance_id = config[1]['ids'][0]
        aws_test_utils.create_db_instance(db_instance_id, resource_type, engine_name,
                        username, password, region_name)
        logging.info(f'DB Instance: {db_instance_id}, status: {dbi_operator.get_status(db_instance_id)}')
        
        # インスタンスIDを置換して作業ディレクトリに保存する。
        mapping_info = dict()
        mapping_info['ec2.instance:i-xxxxxxxxxxxxxxxxx'] = ec2_instance_01
        mapping_info['ec2.instance:i-yyyyyyyyyyyyyyyyy'] = ec2_instance_02
        temp_file = os.path.join(os.path.dirname(__file__), 'work',
                                 os.path.basename(__file__))
        self._dump_config_workfile(config_root, {configkey: mapping_info}, temp_file)
        
        ##### テスト開始 #####
        # EC2インスタンスとDBCインスタンスが実行中の状態で、コンテキストの
        # Lambda関数名に「ec2_stop_test02_ok」を指定して、start_stop_aws_resources
        # 関数を実行する。
        event = dict()
        context = MyContext()
        context.function_name = f'ec2_stop_{configkey}'
        # start_stop_aws_resources関数を実行する。
        aws_resource_start_stop.start_stop_aws_resources(event, context,
                use_event=False, script_path=temp_file)
        # => EC2インスタンスが停止していること
        status = ec2_operator.get_status(ec2_instance_01)
        self._baseAssertEqual(status, 'stopped')
        status = ec2_operator.get_status(ec2_instance_02)
        self._baseAssertEqual(status, 'stopped')
        # => RDS DB Instanceが停止していること。
        status = dbi_operator.get_status(db_instance_id)
        self._baseAssertEqual(status, 'stopped')
        
        # EC2インスタンスとDBCインスタンスが停止中の状態で、コンテキストの
        # Lambda関数名に「ec2_stop_test02_ok」を指定して、
        # start_stop_aws_resources関数を実行する。
        event = dict()
        context = MyContext()
        context.function_name = f'ec2_start_{configkey}'
        # start_stop_aws_resources関数を実行する。
        aws_resource_start_stop.start_stop_aws_resources(event, context,
                use_event=False, script_path=temp_file)
        # => EC2インスタンスが開始していること。
        status = ec2_operator.get_status(ec2_instance_01)
        self._baseAssertEqual(status, 'running')
        status = ec2_operator.get_status(ec2_instance_02)
        self._baseAssertEqual(status, 'running')
        # => RDS DB Instanceが開始していること。
        status = dbi_operator.get_status(db_instance_id)
        self._baseAssertEqual(status, 'available')
        
        logging.info('<<<<< test02_ok_event_start_stop_aws_resources end')
    
    @mock_ec2
    @mock_rds
    def test02_ng_event_start_stop_aws_resources(self):
        '''configKeyにtest02_okを設定して、start_stop_aws_resources関数のテストを実行します。
        
        テストの内容は、以下のとおりです。
        
        * 設定ファイルに、EC2インスタンスとDBインスタンスが実行中のインスタンス
          IDと存在しないインスタンスIDが設定されている状態で、コンテキストの
          Lambda関数名に「ec2_stop_test02_ok」を指定して、
          start_stop_aws_resources関数を実行する。
            * => 例外が発生すること。
            * => EC2インスタンスが停止していること。
            * => RDS DB Clusterが停止していること。
        * 設定ファイルに、EC2インスタンスとDBインスタンスが停止中のインスタンス
          IDと存在しないインスタンスIDが設定されている状態で、コンテキストの
          Lambda関数名に「ec2_stop_test02_ok」を指定して、
          start_stop_aws_resources関数を実行する。
            * => 例外が発生すること。
            * => EC2インスタンスが開始していること。
            * => RDS DB Clusterが開始していること。
        
        '''
        logging.info('>>>>> test02_ng_event_start_stop_aws_resources start')
        
        ##### テストの準備 #####
        configkey = 'test02_ng'
        # テスト用の設定ファイルを読み込む
        config_root = aws_test_utils.load_yaml(__file__)
        region_name = config_root['region_name']
        access_key = config_root['access_key_id']
        secret_key = config_root['secret_access_key']
        config = config_root[configkey]
        
        # インスタンスのステータス確認用にAWSResourceOperatorのインスタンスを取得する。
        ec2_operator = AwsResourceOperatorFactory.create('ec2.instance', region_name)
        dbc_operator = AwsResourceOperatorFactory.create('rds.db_cluster', region_name)
        dbi_operator = AwsResourceOperatorFactory.create('rds.db_instance', region_name)
        
        # ec2インスタンスを１つ開始する。
        ami_id = 'ami-test01ok'
        ec2_instances = aws_test_utils.run_instances(ami_id, region_name, 2)
        ec2_instance_01 = ec2_instances[0]['InstanceId']
        logging.info(f'EC2: {ec2_instance_01}, status: {ec2_operator.get_status(ec2_instance_01)}')
        
        # RDS DBインスタンスを１つ開始する。
        resource_type = 'db.t2.micro'
        engine_name = 'postgres'
        username = 'postgres'
        password = 'password@123'
        db_instance_id = config[2]['ids'][1]
        aws_test_utils.create_db_instance(db_instance_id, resource_type, engine_name,
                        username, password, region_name)
        logging.info(f'DB Instance: {db_instance_id}, status: {dbi_operator.get_status(db_instance_id)}')
        
        # インスタンスIDを置換して作業ディレクトリに保存する。
        mapping_info = dict()
        mapping_info['ec2.instance:i-xxxxxxxxxxxxxxxxx'] = ec2_instance_01
        temp_file = os.path.join(os.path.dirname(__file__), 'work',
                                 os.path.basename(__file__))
        self._dump_config_workfile(config_root, {configkey: mapping_info}, temp_file)
        
        ##### テスト開始 #####
        # 設定ファイルに、EC2インスタンスとDBインスタンスが実行中のインスタンス
        # IDと存在しないインスタンスIDが設定されている状態で、コンテキストの
        # Lambda関数名に「ec2_stop_test02_ng」を指定して、
        # start_stop_aws_resources関数を実行する。
        event = dict()
        context = MyContext()
        context.function_name = f'ec2_stop_{configkey}'
        with self.assertRaises(Exception) as cm:
            # start_stop_aws_resources関数を実行する。
            aws_resource_start_stop.start_stop_aws_resources(event, context,
                    use_event=False, script_path=temp_file)
        # => 例外が発生すること。
        logging.info(f'Exception: {str(cm.exception)}')
        # => EC2インスタンスが停止していること
        status = ec2_operator.get_status(ec2_instance_01)
        self._baseAssertEqual(status, 'stopped')
        # => RDS DB Instanceが停止していること。
        status = dbi_operator.get_status(db_instance_id)
        self._baseAssertEqual(status, 'stopped')
        
        # 設定ファイルに、EC2インスタンスとDBインスタンスが停止中のインスタンス
        # IDと存在しないインスタンスIDが設定されている状態で、コンテキストの
        # Lambda関数名に「ec2_start_test02_ng」を指定して、
        # start_stop_aws_resources関数を実行する。
        event = dict()
        context = MyContext()
        context.function_name = f'ec2_start_{configkey}'
        with self.assertRaises(Exception) as cm:
            # start_stop_aws_resources関数を実行する。
            aws_resource_start_stop.start_stop_aws_resources(event, context,
                use_event=False, script_path=temp_file)
        # => 例外が発生すること。
        logging.info(f'Exception: {str(cm.exception)}')
        # => EC2インスタンスが開始していること。
        status = ec2_operator.get_status(ec2_instance_01)
        self._baseAssertEqual(status, 'running')
        # => RDS DB Instanceが開始していること。
        status = dbi_operator.get_status(db_instance_id)
        self._baseAssertEqual(status, 'available')
        
        logging.info('<<<<< test02_ng_event_start_stop_aws_resources end')
    
    @mock_ec2
    @mock_rds
    def test_event_list_start_stop_aws_resources(self):
        '''start_stop_aws_resources関数にconfigKeyのリストを渡して関数を実行します。
        
        start_stop_aws_resources関数を以下の用にして実行し、２つのconfigKeyに
        設定されたEC2、DBインスタンスが停止、開始できることを確認します。
        
        * 以下の構成の設定ファイルを使用する
        * test01_okのEC2、test02_okのDBインスタンスを起動状態にする
        * configKeyのリスト [test01_ok、test02_ok] をstart_stop_aws_resources
          関数に渡して関数を実行する 
        
                test01_ok:
                  - type: ec2.instance
                    ids:
                      - i-xxxxxxxxxxxxxxxxx
                  - type: rds.db_cluster
                    ids:
                      - myrds_cluster01
                test02_ok:
                  - type: ec2.instance
                    ids:
                      - i-xxxxxxxxxxxxxxxxx
                      - i-yyyyyyyyyyyyyyyyy
                  - type: rds.db_instance
                    ids:
                      - myrds_instance01

            * => DB Clusterの停止失敗の例外が発生すること。
            * => EC2インスタンスが１台停止していること
            * => RDS DB Instanceが停止していること。
        * EC2インスタンスとDBインスタンスが停止している状態で、configKeyのリスト
          [test01_ok、test02_ok] をstart_stop_aws_resources関数に渡して
          インスタンスを開始する。
            * => EC2インスタンスの開始失敗の例外が発生すること。
            * => EC2インスタンスの開始失敗の例外が発生すること。
            * => RDS DB Instanceが開始していること。
        
        '''
        logging.info('>>>>> test_event_list_start_stop_aws_resources start')
        
        ##### テストの準備 #####
        configkey01 = 'test01_ok'
        configkey02 = 'test02_ok'
        # テスト用の設定ファイルを読み込む
        config_root = aws_test_utils.load_yaml(__file__)
        region_name = config_root['region_name']
        access_key = config_root['access_key_id']
        secret_key = config_root['secret_access_key']
        
        # インスタンスのステータス確認用にAWSResourceOperatorのインスタンスを取得する。
        ec2_operator = AwsResourceOperatorFactory.create('ec2.instance', region_name)
        dbc_operator = AwsResourceOperatorFactory.create('rds.db_cluster', region_name)
        dbi_operator = AwsResourceOperatorFactory.create('rds.db_instance', region_name)
        
        # ec2インスタンスを２つ開始する。
        ami_id = 'ami-test01ok'
        ec2_instances = aws_test_utils.run_instances(ami_id, region_name, 2)
        ec2_instance_01 = ec2_instances[0]['InstanceId']
        logging.info(f'EC2: {ec2_instance_01}, status: {ec2_operator.get_status(ec2_instance_01)}')
        
        # RDS DBインスタンスを１つ開始する。
        resource_type = 'db.t2.micro'
        engine_name = 'postgres'
        username = 'postgres'
        password = 'password@123'
        db_instance_id = config_root[configkey02][1]['ids'][0]
        aws_test_utils.create_db_instance(db_instance_id, resource_type, engine_name,
                        username, password, region_name)
        logging.info(f'DB Instance: {db_instance_id}, status: {dbi_operator.get_status(db_instance_id)}')
        
        # test01_okのインスタンスIDを置換して作業ディレクトリに保存する。
        mapping_info01 = dict()
        mapping_info01['ec2.instance:i-xxxxxxxxxxxxxxxxx'] = ec2_instance_01
        temp_file = os.path.join(os.path.dirname(__file__), 'work',
                                 os.path.basename(__file__))
        self._dump_config_workfile(config_root, {configkey01: mapping_info01},
                temp_file)
        
        ##### テスト開始 #####
        # EC2インスタンスとDBインスタンスが起動している状態で、configKeyのリスト
        # [test01_ok、test02_ok] をstart_stop_aws_resources関数に渡して
        # インスタンスを停止する。
        event = {'action': 'stop', 'configKey': [configkey01, configkey02]}
        context = MyContext()
        with self.assertRaises(Exception) as cm:
            # start_stop_aws_resources関数を実行する。
            aws_resource_start_stop.start_stop_aws_resources(event, context,
                    script_path=temp_file)
        # => EC2の停止失敗の例外が発生すること。
        logging.info(f'Exception: {str(cm.exception)}')
        # => EC2インスタンスが１台停止していること
        status = ec2_operator.get_status(ec2_instance_01)
        self._baseAssertEqual(status, 'stopped')
        # => RDS DB Instanceが停止していること。
        status = dbi_operator.get_status(db_instance_id)
        self._baseAssertEqual(status, 'stopped')
        
        # EC2インスタンスとDBインスタンスが停止している状態で、configKeyのリスト
        # [test01_ok、test02_ok] をstart_stop_aws_resources関数に渡して
        # インスタンスを開始する。
        event = {'action': 'start', 'configKey': [configkey01, configkey02]}
        context = MyContext()
        with self.assertRaises(Exception) as cm:
            # start_stop_aws_resources関数を実行する。
            aws_resource_start_stop.start_stop_aws_resources(event, context,
                    script_path=temp_file)
        # => EC2インスタンスの開始失敗の例外が発生すること。
        logging.info(f'Exception: {str(cm.exception)}')
        # => EC2インスタンスが１台開始していること
        status = ec2_operator.get_status(ec2_instance_01)
        self._baseAssertEqual(status, 'running')
        # => RDS DB Instanceが開始していること。
        status = dbi_operator.get_status(db_instance_id)
        self._baseAssertEqual(status, 'available')
        
        logging.info('<<<<< test_event_list_start_stop_aws_resources end')

if __name__ == '__main__':
    html_runner = HtmlTestRunner.HTMLTestRunner(
            output=os.path.dirname(__file__) + '/../target/site/test-report',
            add_timestamp=False)
    unittest.main(testRunner=html_runner)
# -*- config: utf-8 -*-
'''AwsEc2StartStopTest module.

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
import aws_test_utils
import boto3
from moto import mock_ec2
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
    '''
    
    テスト用の context オブジェクト
    
    '''
    function_name = None

class AwsEc2InstanceOperatorTest(unittest.TestCase):
    '''
    
    aws_resource_start_stop モジュール用のテストクラス
    
    '''
    # event から情報を取得するかどうかの定数
    _use_event = True
    
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
    
    def _set_use_event(self, use_event):
        '''
        aws_resource_start_stop モジュールの start_stop_aws_resources 関数実行に
        情報を event から取得するかどうかの設定をします。
        
        Args:
            use_event (boolean): インスタンスの銃砲取得元が event の場合は
                    True、contextの場合は False を指定します
        '''
        self._use_event = use_event
    
    @mock_ec2
    def _run_instances(self, ami_id, region_name, count=1):
        '''
        
        EC2インスタンスを起動します。
        
        Args:
            ami_id (str): AMI ID を指定します
            regopm_name (str): リージョン名を指定します
            count (:obj:`int`, optional): 作成するEC2の個数を指定します
        
        Retunrs:
            Instanceオブジェクトの配列を返します
        
        '''
        ec2 = boto3.client('ec2', region_name=region_name)
        ec2.run_instances(ImageId=ami_id, MinCount=count, MaxCount=count)
        instances = ec2.describe_instances()['Reservations'][0]['Instances']
        
        return instances

    def _get_instance(self, instance_id, instances):
        '''
        
        インスタンスIDを指定して、インスタンスを取得します。
        
        Args:
            instance_id (str): インスタンスIDを指定します
            instances: EC2インスタンスオブジェクトの配列を指定します
        
        Returns:
            Instanceオブジェクトを返します。
        
        '''
        instance = None
        
        for instance in instances:
            if instance['InstanceId'] == instance_id:
                break
        
        return instance
    
    def setUp(self):
        '''
        
        テスト関数の set up を実行します。
        
        '''
        logging.info('Set up test.')
    
    def tearDown(self):
        '''
        
        テストクラスの tear down を実行します。
        
        '''
        logging.info('Tear down test.')
    
    def test_load_config(self):
        '''
        
        _load_config 関数のテストを実行します。
        
        * 設定ファイルのキーを指定して読み込んだ AwsResourceStartStopConfig
          オブジェクトの内容が設定ファイルの内容と一致すること
        
        * 設定ファイルのキー配列を指定して読み込んだ AwsResourceStartStopConfig
          オブジェクトの内容が設定ファイルの内容と一致すること
        
        '''
        logging.info('>>>>> test_load_config start')
        
        # 設定ファイルのキーを指定して読み込んだ AwsResourceStartStopConfig
        # オブジェクトの内容が設定ファイルの内容と一致すること
        config = aws_resource_start_stop._load_config(__file__, 'resources02_test_ng')
        self.assertEqual(config.region_name, 'ap-northeast-1')
        # 設定ファイルのキー配列を指定して読み込んだ AwsResourceStartStopConfig
        # オブジェクトの内容が設定ファイルの内容と一致すること
        resource_types = config.resource_groups
        ## ec2.instance
        self.assertEqual(resource_types[0].get('type'), 'ec2.instance')
        self.assertEqual(resource_types[0].get('ids'), ['i-yyyyyyyyyyyyyyyyy', 'i-zzzzzzzzzzzzzzzzz'])
        ## rds.db_cluster
        self.assertEqual(resource_types[1].get('type'), 'rds.db_cluster')
        self.assertEqual(resource_types[1].get('ids'), ['myrds_clusterxx', 'myrds_clusteryy'])
        ## rds.db_instance
        self.assertEqual(resource_types[2].get('type'), 'rds.db_instance')
        self.assertEqual(resource_types[2].get('ids'), ['myrds_instancexx', 'myrds_instanceyy'])
        
        logging.info('<<<<< test_load_config end')
    
    def test_error_load_config(self):
        '''
        
        _load_config 関数のエラーが発生する場合のテストを実行します。
        
        * 設定ファイルに存在しないキー名を指定するとエラーとなること
        
        '''
        logging.info('>>>>> test_error_load_config start')
        
        # 設定ファイルに存在しないキー名を指定するとエラーとなること
        with self.assertRaises(Exception):
            config = aws_resource_start_stop._load_config(__file__, 'key_not_exists')
        
        logging.info('<<<<< test_error_load_config end')
    
    def test_get_action_from_context(self):
        '''
        
        _get_action_from_context 関数をテストします。
        
        * contextオブジェクトのfunction_nameプロパティに
          'ec2_start_resources01_test_ok' を指定すると、'start'が返される
        
        * contextオブジェクトのfunction_nameプロパティに
          'ec2_stop_resources_test_ok' を指定すると、'stop'が返される
        
        '''
        logging.info('>>>>> test_get_action_from_context start')
        
        context = MyContext()
        
        # Lambda関数名に'start'を指定
        context.function_name = 'ec2_start_resources01_test_ok'
        action_name = aws_resource_start_stop._get_action_from_context(context)
        self.assertEqual(action_name, 'start')
        
        # Lambda関数名にstopを指定
        context.function_name = 'ec2_stop_resources_test_ok'
        action_name = aws_resource_start_stop._get_action_from_context(context)
        self.assertEqual(action_name, 'stop')
        
        logging.info('<<<<< test_get_action_from_context end')
    
    def test_get_action_from_event(self):
        '''
        
        _get_action_from_event 関数をテストします。
        
        * event dictionary のキー：action の値 に 'start' を指定すると、
          'start'が返される
        
        * event dictionary のキー：action の値に 'stop' を指定すると、
          'stop'が返される
        
        '''
        logging.info('>>>>> test_get_action_from_event start')
        
        # event dictionary のキー：action の値に'start'を指定
        event = {"action": "start", "configKey": "resources01_test_ok"}
        action_name = aws_resource_start_stop._get_action_from_event(event)
        self.assertEqual(action_name, 'start')
        
        # event dictionary のキー：action の値に'stop'を指定
        event = {"action": "stop", "configKey": "resources_test_ok"}
        action_name = aws_resource_start_stop._get_action_from_event(event)
        self.assertEqual(action_name, 'stop')
        
        logging.info('<<<<< test_get_action_from_event end')

    def test_get_configkey_from_context(self):
        '''

        _get_configkey_from_context 関数をテストします。
        
        * contextオブジェクトのfunction_nameプロパティに
          'ec2_start_resources01' を指定すると、'resources01'が返される
        
        * contextオブジェクトのfunction_nameプロパティに
          'ec2_start_resources_test_ok' を指定すると、'resources_test_ok'が
          返される
  
        '''
        logging.info('>>>>> test_get_configkey_from_context start')
        
        context = MyContext()
        
        # Lambda関数名のキー名に「resources01」を指定
        context.function_name = 'ec2_start_resources01'
        configkey = aws_resource_start_stop._get_configkey_from_context(context)
        self.assertEqual(configkey, 'resources01')
        
        # Lambda関数名のキー名に「resources01_test_ok」を指定
        context.function_name = 'ec2_start_resources01_test_ok'
        configkey = aws_resource_start_stop._get_configkey_from_context(context)
        self.assertEqual(configkey, 'resources01_test_ok')
        
        logging.info('<<<<< test_get_configkey_from_context end')

    def test_get_configkey_from_event(self):
        '''

        _get_configkey_from_event 関数をテストします。
        
        * event dictionary の キー：configKey の値に 'resources01' を
          設定すると、'resources01'が返される
        
        * event dictionary の キー：configKey の値に 'resources_test_ok' を
          指定すると、'resources_test_ok'が返される
  
        '''
        logging.info('>>>>> test_get_configkey_from_event start')
        
        # event dictionary のキー：configKey の値に「resources01」を指定
        event = {"action": "sstart", "configKey": "resources01"}
        configkey = aws_resource_start_stop._get_configkey_from_event(event)
        self.assertEqual(configkey, 'resources01')
        
        # event dictionary のキー：configKey の値に「resources01_test_ok」を
        # 指定
        event = {"action": "sstart", "configKey": "resources01_test_ok"}
        configkey = aws_resource_start_stop._get_configkey_from_event(event)
        self.assertEqual(configkey, 'resources01_test_ok')
        
        logging.info('<<<<< test_get_configkey_from_event end')
    
    @mock_ec2
    def _test_start_stop_aws_resources(self):
        '''
        
        start_stop_aws_resources 関数のテストを実行します。
        
        * 規定値を使用して1つのインスタンスを開始できること
        * 規定値を使用して2つのインスタンスを開始できること
        * 規定値を使用して1つのインスタンスを停止できること
        * 規定値を使用して2つのインスタンスを停止できること
        * event の configKey に 設定値のキーの配列を指定して、既定値を使用して
          関数を実行すると複数のインスタンスを開始できること
        * event の configKey に 設定値のキーの配列を指定して、既定値を使用して
          関数を実行すると複数のインスタンスを停止できること
        * アクセスキーその他を指定して1つのインスタンスを開始できること
        * アクセスキーその他を指定して2つのインスタンスを開始できること
        * アクセスキーその他を指定して1つのインスタンスを停止できること
        * アクセスキーその他を指定して2つのインスタンスを停止できること
        * event の configKey に 設定値のキーの配列を指定して、アクセスキー
          その他を使用して関数を実行すると複数のインスタンスを開始できること
        * event の configKey に 設定値のキーの配列を指定して、アクセスキー
          その他を使用して関数を実行すると複数のインスタンスを停止できること
        
        '''
        resource_type = 'ec2.instance'
        region_name = 'ap-northeast-1'
        operator = AwsResourceOperatorFactory.create(resource_type, region_name)
        
        # EC2インスタンスを作成してYAML形式の設定ファイルを更新する
        ami = 'ami-1234abcd'
        yaml_config = aws_test_utils.load_yaml(__file__)
        region_name = yaml_config['region_name']
        access_key = yaml_config['access_key_id']
        secret_key = yaml_config['secret_access_key']
        
        instances = self._run_instances(ami, region_name, 2)
        instance_id_01 = instances[0]['InstanceId']
        instance_id_02 = instances[1]['InstanceId']
        yaml_config['resources01_test_ok'].clear()
        yaml_config['resources02_test_ok'].clear()
        yaml_config['resources01_test_ok'].append({'type':'ec2.instance', 'ids':[instance_id_01]})
        yaml_config['resources02_test_ok'].append({'type':'ec2.instance', 'ids':[instance_id_01, instance_id_02]})
        temp_file = os.path.join(os.path.dirname(__file__), 'work',
                                 os.path.basename(__file__))
        aws_test_utils.dump_yaml(yaml_config, temp_file)
        
        context = MyContext()
        
        # 規定値を使用して1つのインスタンスを開始する
        event = {"action": "start", "configKey": "resources01_test_ok"}
        context.function_name = 'ec2_start_resources01_test_ok'
        if self._use_event:
            logging.info('*** start_stop_aws_resources(event=' + str(event) + ') ***')
        else:
            logging.info('*** start_stop_aws_resources(context.function_name=' + context.function_name + ') ***')
        aws_resource_start_stop.start_stop_aws_resources(event, context, self._use_event, temp_file)
        # インスタンスの状態を確認する
        config = aws_resource_start_stop._load_config(temp_file, 'resources01_test_ok')
        for instance_id in config.resource_groups[0]['ids']:
            self.assertEqual(operator.get_status(instance_id), 'running')
        
        # 規定値を使用して2つのインスタンスを開始する
        event = {"action": "start", "configKey": "resources02_test_ok"}
        context.function_name = 'ec2_start_resources02_test_ok'
        if self._use_event:
            logging.info('*** start_stop_aws_resources(event=' + str(event) + ') ***')
        else:
            logging.info('*** start_stop_aws_resources(context.function_name=' + context.function_name + ') ***')
        aws_resource_start_stop.start_stop_aws_resources(event, context, self._use_event, temp_file)
        # インスタンスの状態を確認する
        config = aws_resource_start_stop._load_config(temp_file, 'resources02_test_ok')
        for instance_id in config.resource_groups[0]['ids']:
            self.assertEqual(operator.get_status(instance_id), 'running')
        
        # 規定値を使用して1つのインスタンスを停止する
        event = {"action": "stop", "configKey": "resources01_test_ok"}
        context.function_name = 'ec2_stop_resources01_test_ok'
        if self._use_event:
            logging.info('*** start_stop_aws_resources(event=' + str(event) + ') ***')
        else:
            logging.info('*** start_stop_aws_resources(context.function_name=' + context.function_name + ') ***')
        aws_resource_start_stop.start_stop_aws_resources(event, context, self._use_event, temp_file)
        
        # 規定値を使用して2つのインスタンスを停止する
        event = {"action": "stop", "configKey": "resources02_test_ok"}
        context.function_name = 'ec2_stop_resources02_test_ok'
        if self._use_event:
            logging.info('*** start_stop_aws_resources(event=' + str(event) + ') ***')
        else:
            logging.info('*** start_stop_aws_resources(context.function_name=' + context.function_name + ') ***')
        aws_resource_start_stop.start_stop_aws_resources(event, context, self._use_event, temp_file)
        
        # event に 複数の設定ファイルのキーを指定して、規定値を使用して関数を
        # 呼び出して、複数のインスタンスを開始する
        if self._use_event:
            event = {"action": "start", "configKey": ["resources01_test_ok", "resources02_test_ok"]}
            logging.info('*** start_stop_aws_resources(event=' + str(event) + ') ***')
            aws_resource_start_stop.start_stop_aws_resources(event, context, self._use_event, temp_file)
            # インスタンスの状態を確認する
            config = aws_resource_start_stop._load_config(temp_file, ["resources01_test_ok", "resources02_test_ok"])
            for instance_id in config.resource_groups[0]['ids']:
                self.assertEqual(operator.get_status(instance_id), 'running')
        
        # event に 複数の設定ファイルのキーを指定して、規定値を使用して関数を
        # 呼び出して、複数のインスタンスを停止する
        if self._use_event:
            event = {"action": "stop", "configKey": ["resources01_test_ok", "resources02_test_ok"]}
            logging.info('*** start_stop_aws_resources(event=' + str(event) + ') ***')
            aws_resource_start_stop.start_stop_aws_resources(event, context, self._use_event, temp_file)
        
        # アクセスキーその他を指定して1つのインスタンスを開始する
        event = {"action": "start", "configKey": "resources01_test_ok"}
        context.function_name = 'ec2_start_resources01_test_ok'
        if self._use_event:
            logging.info('*** start_stop_aws_resources('+ 'event=' + str(event)
                    + ', access_key=' + access_key
                    + ', secret_key=' + secret_key
                    + ') ***')
        else:
            logging.info('*** start_stop_aws_resources(context.function_name=' + context.function_name
                    + ', access_key=' + access_key
                    + ', secret_key=' + secret_key
                    + ') ***')
        aws_resource_start_stop.start_stop_aws_resources(event, context, self._use_event,
                temp_file, access_key, secret_key)
        # インスタンスの状態を確認する
        config = aws_resource_start_stop._load_config(temp_file, 'resources01_test_ok')
        for instance_id in config.resource_groups[0]['ids']:
            self.assertEqual(operator.get_status(instance_id), 'running')
        
        # アクセスキーその他を指定して2つのインスタンスを開始する
        event = {"action": "start", "configKey": "resources02_test_ok"}
        context.function_name = 'ec2_start_resources02_test_ok'
        if self._use_event:
            logging.info('*** start_stop_aws_resources('+ 'event=' + str(event)
                    + ', access_key=' + access_key
                    + ', secret_key=' + secret_key
                    + ') ***')
        else:
            logging.info('*** start_stop_aws_resources(context.function_name=' + context.function_name
                    + ', access_key=' + access_key
                    + ', secret_key=' + secret_key
                    + ') ***')
        aws_resource_start_stop.start_stop_aws_resources(event, context, self._use_event,
                temp_file, access_key, secret_key)
        # インスタンスの状態を確認する
        config = aws_resource_start_stop._load_config(temp_file, 'resources02_test_ok')
        for instance_id in config.resource_groups[0]['ids']:
             self.assertEqual(operator.get_status(instance_id), 'running')
       
        # アクセスキーその他を指定して1つのインスタンスを停止する
        event = {"action": "stop", "configKey": "resources01_test_ok"}
        context.function_name = 'ec2_stop_resources01_test_ok'
        if self._use_event:
            logging.info('*** start_stop_aws_resources('+ 'event=' + str(event)
                    + ', access_key=' + access_key
                    + ', secret_key=' + secret_key
                    + ') ***')
        else:
            logging.info('*** start_stop_aws_resources(context.function_name=' + context.function_name
                    + ', access_key=' + access_key
                    + ', secret_key=' + secret_key
                    + ') ***')
        aws_resource_start_stop.start_stop_aws_resources(event, context, self._use_event,
                temp_file, access_key, secret_key)
        
        # アクセスキーその他を指定して2つのインスタンスを停止する
        event = {"action": "stop", "configKey": "resources01_test_ok"}
        context.function_name = 'ec2_stop_resources01_test_ok'
        if self._use_event:
            logging.info('*** start_stop_aws_resources('+ 'event=' + str(event)
                    + ', access_key=' + access_key
                    + ', secret_key=' + secret_key
                    + ') ***')
        else:
            logging.info('*** start_stop_aws_resources(context.function_name=' + context.function_name
                    + ', access_key=' + access_key
                    + ', secret_key=' + secret_key
                    + ') ***')
        aws_resource_start_stop.start_stop_aws_resources(event, context, self._use_event,
                temp_file, access_key, secret_key)
        
        # event に 複数の設定ファイルのキーを指定して、アクセスキーその他を
        # 使用して関数を呼び出して、複数のインスタンスを開始する
        if self._use_event:
            event = {"action": "start", "configKey": ["resources01_test_ok", "resources02_test_ok"]}
            logging.info('*** start_stop_aws_resources(event=' + str(event)
                + ', access_key=' + access_key
                + ', secret_key=' + secret_key
                + ') ***')
            aws_resource_start_stop.start_stop_aws_resources(event, context, self._use_event, temp_file)
            # インスタンスの状態を確認する
            config = aws_resource_start_stop._load_config(temp_file, ["resources01_test_ok", "resources02_test_ok"])
            for instance_id in config.resource_groups[0]['ids']:
                self.assertEqual(operator.get_status(instance_id), 'running')
       
        # event に 複数の設定ファイルのキーを指定して、アクセスキーその他を
        # 使用して関数を呼び出して、複数のインスタンスを停止する
        if self._use_event:
            event = {"action": "stop", "configKey": ["resources01_test_ok", "resources02_test_ok"]}
            logging.info('*** start_stop_aws_resources(event=' + str(event)
                + ', access_key=' + access_key
                + ', secret_key=' + secret_key
                + ') ***')
            aws_resource_start_stop.start_stop_aws_resources(event, context, self._use_event, temp_file)
    
    def test_start_stop_ec2_instance_use_event(self):
        '''
        
        Lambda 関数の event から開始、停止するインスタンスの情報を取得して、
        start_stop_aws_resources 関数のテストを実行する関数を呼び出します。
        
        '''
        logging.info('>>>>> test_start_stop_aws_resources_use_event start')
        
        self._set_use_event(True)
        self._test_start_stop_aws_resources()

        logging.info('<<<<< test_start_stop_aws_resources_use_event end')
    
    def test_start_stop_ec2_instance_use_context(self):
        '''
        
        Lambda 関数の context から開始、停止するインスタンスの情報を取得して、
        start_stop_aws_resources 関数のテストを実行する関数を呼び出します。
        
        '''
        logging.info('>>>>> test_start_stop_aws_resources_use_context start')
        
        self._set_use_event(False)
        self._test_start_stop_aws_resources()

        logging.info('<<<<< test_start_stop_aws_resources_use_context end')
    
    @mock_ec2
    def _test_error_start_stop_aws_resources(self):
        '''
        
        start_stop_aws_resources 関数のエラーが発生する場合のテストを実行
        します。
        
        * Lambda関数名のコマンド、キー名が'_'で区切られていない場合はエラーが
          発生すること
        * Lambda関数名のコマンドがstart、stop以外である場合はエラーが発生する
          こと
        * Lambda関数名のキー名が設定ファイルに存在しない場合はエラーが発生する
          こと
        * 設定ファイルに存在しないインスタンスIDが設定されている場合はエラーが
          発生すること
        * 設定ファイルにEC2インスタンスとは別のリージョンを指定した場合は
          エラーが発生すること
        
        '''
        # テスト用のスクリプトと設定ファイルのパス
        script_temp_path = os.path.splitext(__file__)[0] + '_temp.py'
        config_temp_path = os.path.splitext(__file__)[0] + '_temp.yml'
        
        # EC2インスタンスを作成してテスト用のYAML形式の設定ファイルに反映する
        ami = 'ami-1234abcd'
        yaml_config = aws_test_utils.load_yaml(__file__)
        region_name = yaml_config['region_name']
        access_key = yaml_config['access_key_id']
        secret_key = yaml_config['secret_access_key']
        
        instances = self._run_instances(ami, region_name, 2)
        instance_id_01 = instances[0]['InstanceId']
        instance_id_02 = instances[1]['InstanceId']
        yaml_config['resources01_test_ok'] = [instance_id_01]
        yaml_config['resources02_test_ok'] = [instance_id_01, instance_id_02]
        temp_file = os.path.join(os.path.dirname(__file__), 'work',
                                 os.path.basename(__file__))
        aws_test_utils.dump_yaml(yaml_config, temp_file)
        
        context = MyContext()

        # 例外処理を実装して関数を呼び出す。
        event = {"action": "test", "configKey": "ok"}
        context.function_name = 'ec2startresources01_test_ok'
        try:
            aws_resource_start_stop.start_stop_aws_resources(event, context, self._use_event, temp_file)
        except Exception as e:
            logging.error(str(e.__class__) + ': ' +  str(e))
            traceback.print_stack(file=sys.stdout)
 
        
        # evemt dictionary の action、configKey の値が間違っている       
        # Lambda関数名のコマンド、キー名が'_'で区切られていない
        # => 例外が発生する
        event = {"action": "test", "configKey": "ok"}
        context.function_name = 'ec2startresources01_test_ok'
        if (self._use_event):
            logging.info('event: ' + str(event))
        else:
            logging.info('function name: ' + context.function_name)
        with self.assertRaises(Exception):
            aws_resource_start_stop.start_stop_aws_resources(event, context, self._use_event, temp_file)
        
        # event dictionary の leu の値が がstart、stop以外である
        # Lambda関数名のコマンドがstart、stop以外である
        # => 例外が発生する
        event = {"action": "foo", "configKey": "resources01_test_ok"}
        context.function_name = 'ec2_foo_resources01_test_ok'
        if (self._use_event):
            logging.info('event: ' + str(event))
        else:
            logging.info('function name: ' + context.function_name)
        with self.assertRaises(Exception):
            aws_resource_start_stop.start_stop_aws_resources(event, context, self._use_event, temp_file)
        
        # event dictionary の configKey の値が設定ファイルに存在しないものである
        # Lambda関数名のキー名が設定ファイルに存在しないものである
        # => 例外が発生する
        event = {"action": "start", "configKey": "resources_not_exists"}
        context.function_name = 'ec2_start_resources_not_exists'
        if (self._use_event):
            logging.info('event: ' + str(event))
        else:
            logging.info('function name: ' + context.function_name)
        with self.assertRaises(Exception):
            aws_resource_start_stop.start_stop_aws_resources(event, context, self._use_event, temp_file)
        
        # 設定ファイルに存在しないインスタンスIDが設定されている
        # => 例外が発生する
        event = {"action": "start", "configKey": "resources02_test_ng"}
        context.function_name = 'ec2_start_resources02_test_ng'
        if (self._use_event):
            logging.info('event: ' + str(event))
        else:
            logging.info('function name: ' + context.function_name)
        with self.assertRaises(Exception):
            aws_resource_start_stop.start_stop_aws_resources(event, context, self._use_event, temp_file)
        
        # 設定ファイルにEC2インスタンスとは別のリージョンを指定した
        # => 例外が発生する
        event = {"action": "start", "configKey": "resources01_test_ok"}
        context.function_name = 'ec2_start_resources01_test_ok'
        yaml_config = aws_test_utils.load_yaml(temp_file)
        yaml_config['region_name'] = 'us-east-1'
        aws_test_utils.dump_yaml(yaml_config, script_temp_path)
        if (self._use_event):
            logging.info('event: ' + str(event))
        else:
            logging.info('function name: ' + context.function_name)
        with self.assertRaises(Exception):
            aws_resource_start_stop.start_stop_aws_resources(event, context, self._use_event,
                script_temp_path)
        os.remove(config_temp_path)
    
    def test_error_start_stop_aws_resources_use_event(self):
        '''
        
        Lambda 関数の event から開始、停止するインスタンスの情報を取得して、
        start_stop_aws_resources 関数のエラー発生テストを実行する関数を
        呼び出します。
        
        '''
        logging.info('>>>>> test_error_start_stop_aws_resources_use_event start')
        
        self._set_use_event(True)
        self._test_error_start_stop_aws_resources()
        
        logging.info('<<<<< test_error_start_stop_aws_resources_use_event end')
    
    def test_error_start_stop_aws_resources_use_context(self):
        '''
        
        Lambda 関数の context から開始、停止するインスタンスの情報を取得して、
        start_stop_aws_resources 関数のエラー発生テストを実行する関数を
        呼び出します。
        
        '''
        logging.info('>>>>> test_error_start_stop_aws_resources_use_context start')
        
        self._set_use_event(False)
        self._test_error_start_stop_aws_resources()
        
        logging.info('<<<<< test_error_start_stop_aws_resources_use_context end')

if __name__ == '__main__':
    html_runner = HtmlTestRunner.HTMLTestRunner(
            output=os.path.dirname(__file__) + '/../target/site/test-report',
            add_timestamp=False)
    unittest.main(testRunner=html_runner)
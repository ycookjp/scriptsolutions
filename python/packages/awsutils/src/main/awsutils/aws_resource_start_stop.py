# -*- coding: utf-8 -*-
'''aws_resource_start_stop module.

Copyright ycookjp
https://github.com/ycookjp/

'''

import logging
import os
import yaml

from .aws_resource_operator import AwsResourceOperatorFactory

class AwsResourceStartStopConfig():
    region_name = ''
    '''
    Region name
    '''
    resource_groups = []
    '''
    Array of EC2 instance id
    '''
    access_key_id = None
    '''
    IAM user's access key id
    '''
    secret_access_key = None
    '''
    IAM user's secret access key
    '''

def _load_config(script_path: str, configkey: str):
    '''
    
    Loads configuration file with YAMS format. 
    Configuration file should be located at same directory of specified
    script path, and name should be base name of this script except for
    extension is '.yml'.
    
    Args:
        script_path (str): script path
        configkey (str): configuration key name or list of that
    
    Returns:
        AwsResourceStartStopConfig: Returns configuration object.
    
    '''
    config_path = os.path.splitext(script_path)[0] + '.yml'
    with open(config_path, 'r', encoding='utf-8') as file:
        yaml_conf = yaml.load(file, Loader=yaml.SafeLoader)
        
        config = AwsResourceStartStopConfig()
        config.region_name = yaml_conf['region_name']
        config.access_key_id = yaml_conf.get('access_key_id')
        config.secret_access_key = yaml_conf.get('secret_access_key')

        if isinstance(configkey, list):
            config.resource_groups = []
            config_dict = {}
            for key in configkey:
                for resource_group in yaml_conf[key]:
                    type_name = resource_group.get('type')
                    instance_ids = resource_group.get('ids')
                    dict_instance_ids = config_dict.get(type_name)
                    if dict_instance_ids == None:
                        config_dict[type_name] = instance_ids
                    else:
                        for instance_id in instance_ids:
                            if dict_instance_ids.count(instance_id) == 0:
                                dict_instance_ids.append(instance_id)
            for key in list(config_dict):
                config.resource_groups.append({'type': key, 'ids': config_dict.get(key)})
        elif isinstance(configkey, str):
            config.resource_groups = yaml_conf[configkey]

        return config

def _get_action_from_context(context):
    '''
    
    Lambda関数contextオブジェクトからLambda関数の名前を取得し、それを"_"で
    区切って分割して2番目の文字列を取得してEC2の開始、取得を区別する文字列
    (start/stop)を取得します。
    
    Args:
        context: Lambda関数のcontextオブジェクト
    
    Returns:
        str: EC2の開始、取得を区別する文字列(start/stop)を取得します。
                Lambda関数の名前によっては別の文字列が返されることがあります。
    
    '''
    funcname = context.function_name
    info = funcname.split('_', maxsplit=2)
    action_name = info[1]
    
    return action_name

def _get_configkey_from_context(context):
    '''
    
    Lambda関数contextオブジェクトからLambda関数の名前を取得し、それを"_"で
    区切って分割して3番目の文字列を取得して設定ファイルのキー名を取得します。
    
    Args:
        context: Lambda関数のcontextオブジェクト
    
    Returns:
        str: 設定ファイルのキー名を返します。
    
    '''
    funcname = context.function_name
    info = funcname.split('_', maxsplit=2)
    configkey = info[2]
    
    return configkey

def _get_action_from_event(event):
    action_name = event['action'];
    
    return action_name

def _get_configkey_from_event(event):
    configkey = event['configKey']
    
    return configkey

def start_stop_aws_resources(event, context, use_event=True, script_path=__file__,
        access_key_id=None, secret_access_key=None):
    '''

    event または context から action ("start" または "stop") と configKey
    (インスタンスIDの配列を取得するための設定ファイルのキー、またはキーの配列)
    を取得して、インスタンスの開始／停止をします。
    
    use_event 引数が True の場合は、event から action と configKey を取得
    します。use_event 引数が False の場合は、context から Lambda 関数の名前を
    取得し、そこから action と configKey を取得します。このときは、Lambda関数の
    名前は、「ec2_<action>_<configKey>」の形式である必要があります。
    
    引数 access_key_id を指定しない（Noneを指定した）場合は、設定ファイルの
    「access_key_id」に設定された値をIAMユーザーのアクセスキーに使用します。
    同様に引数 secret_access_key を指定しない（Noneを指定した）場合は、設定ファイルの
    「secret_access_key」に指定された値をIAMユーザーのシークレットキーに庄します。
    
    Args:
        event: Lambda関数のeventオブジェクトを指定します。
        context: Lambda関数のcontextオブジェクトを指定します。
        use_event (boolean, optional): event から情報を取得する場合は
                True、context から情報を取得する場合は False を指定する
        script_path (str, optional): スクリプトのパス
        access_key_id (str, optional): IAMユーザーのアクセスキー
        secret_access_key (str, optional): IAMユーザーのシークレットキー
        client (object, optional): low-lebel client
    
    '''

    try:
        if use_event:
            action_name = _get_action_from_event(event)
            configkey = _get_configkey_from_event(event)
        else:
            action_name = _get_action_from_context(context)
            configkey = _get_configkey_from_context(context)
        
        config = _load_config(script_path, configkey)
        
        if access_key_id == None:
            access_key_id = config.access_key_id
        if secret_access_key == None:
            secret_access_key = config.secret_access_key
        
        for resource_group in config.resource_groups:
            operator = AwsResourceOperatorFactory.create(
                    resource_group['type'], config.region_name,
                    access_key_id, secret_access_key)
            resource_type_name = resource_group['type']
            instance_ids = resource_group['ids']
            if action_name == 'start':
                operator.start_resources(instance_ids)
                for instance_id in instance_ids:
                    logging.info(f'{resource_type_name}: \'{instance_id}\' started.')
            elif action_name == 'stop':
                operator.stop_resources(instance_ids)
                for instance_id in instance_ids:
                    logging.info(f'{resource_type_name}: \'{instance_id}\' stopped.')
            else:
                raise Exception('Lambda function name error')
    except Exception:
        raise

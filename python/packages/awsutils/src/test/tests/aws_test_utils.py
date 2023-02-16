# -*- encoding: utf-8 -*-
'''aws_test_utils module.

Copyright: ycookjp

'''

import os
import yaml
import boto3
from moto import mock_ec2
from moto import mock_rds

def load_yaml(script_path):
    '''Loads YAML configuration file.
    
    Configuration file should be located at same directory of this
    script, and name should be base name of this script except for
    extension is '.yml'.
    
    Args:
        script_path (str): script path which using config file.
    
    Returns:
        Dictionary: Returns key-value information.
    
    '''
    config_path = os.path.splitext(script_path)[0] + '.yml'
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.load(file, Loader=yaml.SafeLoader)
        return config

def dump_yaml(config, script_path):
    '''Saves YAML configuration file.
    
    Configuration file should be located at same directory of this
    script, and name should be base name of this script except for
    extension is '.yml'.
    
    Args:
        config (dict): configuration data.
        script_path (str): script path which using config file.
    
    '''
    config_path = os.path.splitext(script_path)[0] + '.yml'
    with open(config_path, 'w', encoding='utf-8') as file:
        yaml.dump(config, file, default_flow_style=False)

def list_files_in_dir(dir_path: str):
    '''Crate file lists which exists under the directory.
    
    Args:
        dir_path (str): directory path.
    Returns:
        str: Returns list of relative file path from specified directory.
    
    '''
    absdir = os.path.abspath(dir_path)
    file_list = []
    
    for dpath, dnames, fnames in os.walk(absdir):
        fnames.sort()
        
        for fname in fnames:
            file_path = dpath.replace(absdir, '') + os.sep + fname
            if file_path[0] == os.sep:
                file_path = file_path[1:]
            file_list.append(file_path)
    
    return file_list

def list_s3keys_in_bucket(s3objects):
    '''S3のバケットに格納されているオブジェクトの Key のリストを取得する。
    
    Args:
        s3objects (obj): バケット名を指定して、s3 clientの list_objects 関数を
        呼び出いた戻り値を指定する。
    Returns:
        S3オブジェクトの Key のリストを返す。
    
    '''
    s3key_list = []
    contents = s3objects['Contents']
    
    for content in contents:
        s3key_list.append(content['Key'])
    
    return s3key_list
 
@mock_ec2
def run_instances(ami_id, region_name, count=1):
    '''EC2インスタンスを起動します。
    
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
    
@mock_rds
def create_db_cluster(db_cluster_id, engine_name, username, password,
                       region_name):
    '''RDS DB クラスターのインスタンスを起動します。
    
    Args:
        db_cluster_id (str): DBクラスター ID
        engine_name (str): データベース エンジンの名前
        username (str): データベース ユーザー名
        password (str): データベース ユーザーのパスワード
        region_name (str): リージョン名
    
    Returns:
        RDS DB クラスターのインスタンスを返します。
    
    '''
    rds = boto3.client('rds', region_name=region_name)
    db_cluster = rds.create_db_cluster(DBClusterIdentifier=db_cluster_id,
            Engine=engine_name, MasterUsername=username, MasterUserPassword=password)
    return db_cluster
    
@mock_rds
def create_db_instance(db_instance_id, resource_type, engine_name,
                        username, password, region_name):
    '''RDS DB インスタンスを起動します。
    
    Args:
        db_instance_id (str): DBインスタンス ID
        resource_type (str): DBインスタンスのリソース タイプ。db.t2.micro など。
        engine_name (str): データベース エンジンの名前
        username (str): データベース ユーザー名
        password (str): データベース ユーザーのパスワード
        region_name (str): リージョン名
    
    Returns:
        RDS DB インスタンスを返します。
    
    '''
    rds = boto3.client('rds', region_name=region_name)
    db_instance = rds.create_db_instance(DBInstanceIdentifier=db_instance_id,
            DBInstanceClass=resource_type,
            Engine=engine_name, MasterUsername=username, MasterUserPassword=password)
    return db_instance

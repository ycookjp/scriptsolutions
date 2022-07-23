# -*- coding: utf-8 -*-
'''aws_test_utils module.

Copyright: ycookjp

'''

import os
import yaml

def load_yaml(script_path):
    '''
    
    Loads YAML configuration file.
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
    '''
    
    Saves YAML configuration file.
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
    '''
    
    Crate file lists which exists under the directory.
    
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
    '''
    
    S3のバケットに格納されているオブジェクトの Key のリストを取得する。
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


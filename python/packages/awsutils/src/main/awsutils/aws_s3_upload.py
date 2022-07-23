# -*- config: utf-8 -*-
'''aws_s3_upload module.

Copyright ycookjp
https://github.com/ycookjp/

'''

import boto3
import logging
import os
import shutil
import sys
import yaml

class AWSS3MoveConfig():
    region_name = ''
    '''
    リージョン名
    '''
    access_key_id = None
    '''
    IAMユーザーのアクセスキー
    '''
    secret_access_key = None
    '''
    IAMユーザーのシークレットアクセスキー
    '''

def _load_config(script_path: str):
    '''
    
    Loads configuration file with YAMS format. 
    Configuration file should be located at same directory of specified
    script path, and name should be base name of this script except for
    extension is '.yml'.
    
    Args:
        script_path (str): script path
    
    Returns:
        AWSS3MoveConfig: Returns configuration object.
    
    '''
    config_path = os.path.splitext(script_path)[0] + '.yml'
    with open(config_path, 'r', encoding='utf-8') as file:
        yaml_conf = yaml.load(file, Loader=yaml.SafeLoader)
        config = AWSS3MoveConfig()
        config.region_name = yaml_conf['region_name']
        config.access_key_id = yaml_conf.get('access_key_id')
        config.secret_access_key = yaml_conf.get('secret_access_key')
        
        return config

def _operation_log(file_path: str, s3bucket_name: str, s3key: str,
                   remove_src: bool):
    '''
    
    ファイルのアップロード／移動のログを出力します。
    
    Arts:
        file_path (str): アップロード／移動したファイルのパス
        s3bucket_name (str): アップロード／移動先のS3バケット名
        s3key (str): アップロード／移動先のキー（パス月乃ファイル名）
        remove_src (bool): ファイルを移動した場合はTrue
    
    '''
    action = 'uploaded'
    if remove_src:
        action = 'moved'
    
    logging.info(f"{action} {file_path} to s3://{s3bucket_name}/{s3key}")

def _remove_files(file_path: str):
    '''
    
    指定されたファイル、または指定されたディレクトリ配下のファイル・ディレクトリ
    を削除します。
    
    Args:
        file_path (str): 削除対象のファイルまたはディレクトリのパス
    
    '''
    if os.path.isfile(file_path):
        os.remove(file_path)
    elif os.path.isdir(file_path):
        for name in os.listdir(file_path):
            name_path = os.path.join(file_path, name)
            if os.path.isfile(name_path):
                os.remove(name_path)
            elif os.path.isdir(name_path):
                shutil.rmtree(name_path)

def _get_s3_key(s3_folder_path: str, top_dir: str, file_path: str):
    '''
    
    S3バケットのフォルダ名と、アップロード対象ファイルの最上位パスからの
    相対パスを使用して、S3のキーを取得します。
    
    Args:
        s3_folder_path (str): S3バケットのフォルダの名前。サブフォルダの階層を
            持つ場合は、フォルダを'/'で区切って指定する。
        top_dir (str): アップロード対象のファイルが格納されているディレクトリの
            最上位ディレクトリ。
        file_path (str): アップロード対象のファイルのパス。
    Returns:
        str: s3パケットのフォルダ名の後ろに、アップロード対象ファイルの
        最上位ディレクトリからの相対パスを'/'で連結した文字列を返します。
    
    '''
    s3key = file_path
    
    if top_dir != None and len(top_dir) > 0 and file_path.index(top_dir) == 0:
        s3key = s3key[len(top_dir):len(s3key)]
    
    if s3key[0] == os.sep:
        s3key = s3key[1:len(s3key)]
    
    if os.sep != '/':
        s3key = s3key.replace(os.sep, '/')
    
    if s3_folder_path != None and len(s3_folder_path) > 0:
        s3key = s3_folder_path + '/' + s3key
    
    return s3key

def upload_file(file_or_dir_path: str, s3bucket_name: str, s3folder_path: str=None,
                remove_src:bool=False, script_path:str=__file__,
                access_key_id:str=None, secret_access_key:str=None):
    '''
    
    指定されたファイル、または指定されたディレクトリを再帰的に探して取得した
    ファイルを指定されたS3バケットのs3フォルダの下にアップロードします。
    この関数は、引数で指定されたスクリプトパスと同じディレクトリに存在する
    設定ファイル（スクリプトファイルと同じディレクトリに配置された、
    スクリプト名の拡張子が'.yml'であるファイル）から、以下の情報を取得して
    AWSのS3サービスに接続します。
    
    * region_name - リージョン名
    * access_key_id - (オプション) IAMユーザーのアクセスキー。引数にアクセスキーが
        指定されなかった場合は、設定ファイルから取得したものを使用する。
    * secret_access_key - (オプション) IAMユーザーのシークレットキー。引数に
        シークレットキーが指定されなかった場合は、設定ファイルから取得した
        ものを使用する。
    
    Args:
        file_or_dir_path (str): アップロード対象のファイルのパス、または
            ファイルを配置したディレクトリを指定します。
        s3bucket_name (str): アップロード先のS3バケット名を指定します。
        s3folder_path (str, optional): アップロード先のS3フォルダ名を
            指定します。S3フォルダがサブフォルダの場合は、フォルダの間を'/'で
            区切ります。この引数を省略するとフォルダ名を付けずにアップロード
            します。
        remove_src (bool, optional): ファイルをアップロード後に
            元のファイルを削除する場合はTrue、削除しない場合はFalseを指定
            します。Trueを指定した場合は、アップロード対象がファイルの場合は
            そのファイルを、ディレクトリの場合は、そのディレクトリ配下の
            ファイル・ディレクトリを削除します。
        script_path (str, optional): スクリプトのパス
        access_key_id (str, optional): IAMユーザーのアクセスキー
        secret_access_key (str, optional): IAMユーザーのシークレットキー
    
    Raises:
        Exception: file_or_dir_path で指定したパスがファイルでも
            ディレクトリでも無い場合
    
    '''
    config = _load_config(script_path)
    if access_key_id == None:
        access_key_id = config.access_key_id
    if secret_access_key == None:
        secret_access_key = config.secret_access_key
    
    s3_client = boto3.client('s3', aws_access_key_id=access_key_id,
                      aws_secret_access_key=secret_access_key)
    
    if os.path.isfile(file_or_dir_path):
        file_path = file_or_dir_path
        s3key = _get_s3_key(s3folder_path, os.path.dirname(file_path), file_path)
        s3_client.upload_file(file_path, s3bucket_name, s3key)
        _operation_log(file_path, s3bucket_name, s3key, remove_src)
    elif os.path.isdir(file_or_dir_path):
        topdir = os.path.abspath(file_or_dir_path)
        for dirpath, dirnames, filenames in os.walk(topdir):
            filenames.sort()
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                s3key = _get_s3_key(s3folder_path, topdir, file_path)
                s3_client.upload_file(file_path, s3bucket_name, s3key)
                _operation_log(file_path, s3bucket_name, s3key, remove_src)
    else:
        raise Exception('Not found source file or directory')
    
    if remove_src:
        _remove_files(file_or_dir_path)

def main(args):
    file_or_dir_path = args[1]
    s3bucket_name = args[2]
    s3folder_path = args[3]
    remove_src = False
    if len(args) > 4:
        val = args[4].lower()
        remove_src = val == 'true'
    
    upload_file(file_or_dir_path, s3bucket_name, s3folder_path, remove_src)

if __name__ == '__main__':
    main(sys.argv)

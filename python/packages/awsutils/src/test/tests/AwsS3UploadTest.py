# -*- utf-8 -*-
'''AwsS3UploadTest module.

Copyright: ycookjp

'''

import unittest
import logging
import os
import shutil
import sys

from awsutils import aws_s3_upload
import aws_test_utils
import boto3
from moto import mock_aws

root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class AwsS3MoveTest(unittest.TestCase):
    '''
    
    aws_s3_upload モジュールのテストをする。
    
    '''
    
    _os_sep = None
    '''
    ファイル区切り文字。
    '''
    
    @classmethod
    def setUpClass(cls):
        '''
        
        テストクラス起動時の初期化をする。
        
        '''
        logging.info('Set up test class.')
        
        cls._os_sep = os.sep
    
    @classmethod
    def tearDownClass(cls):
        '''
        
        テストクラス終了時の後始末をする。
        このスクリプトと同じディレクトリの下にある work ディレクトリの
        ファイル及びディレクトリ（do_not_commit_this_directory を除く）を
        削除する。
        
        '''
        logging.info('Tear down class.')
        
        os.sep = cls._os_sep
        
        workdir = os.path.join(os.path.dirname(__file__), 'work')
        for name in os.listdir(workdir):
            name_path = os.path.join(workdir, name)
            if os.path.isfile(name_path) and name != 'do_not_commit_this_directory':
                os.remove(name_path)
            elif os.path.isdir(name_path):
                shutil.rmtree(name_path)

    def setUp(self):
        '''
        
        テストメソッド起動時に実行される初期化処理。
        
        '''
        logging.info('Set up test.')
        
        os.sep = self._os_sep
    
    def tearDown(self):
        '''
        
        テストメソッド終了時に実行される終了処理。
        
        '''
        logging.info('Tear down test.')
    
    def _delete_all_objects(self, bucket_name: str):
        '''
        
        指定したS3バケット内のオブジェクトを全て削除する。
        
        Args:
            bucket_name (str): S3バケット名
        
        '''
        s3_resource = boto3.resource('s3')
        bucket = s3_resource.Bucket(bucket_name)
        # suggested by Jordon Philips 
        bucket.objects.all().delete()
    
    def test_load_config(self):
        '''
        
        _load_config 関数のテストをする。
        設定ファイル（このスクリプトファイルの名前の拡張子を「.yml」に変えた
        ファイル）に設定された以下の項目が正しく読み込まれるとを確認する。
        
        * region_name
        * access_key_id
        * secret_access_key
        
        '''
        logging.info('>>>>> test_load_config start')
        
        config = aws_s3_upload._load_config(__file__)
        
        # 読み込だ設定項目 region_name の確認
        self.assertEqual(config.region_name, 'ap-northeast-1')
        
        # 読み込んだテスト項目 access_key_id の確認
        self.assertEqual(config.access_key_id, 'my_access_key')
        
        # 読み込んだ設定項目 secret_access_key の確認
        self.assertEqual(config.secret_access_key, 'my_secret_key')

        logging.info('<<<<< test_load_config end')
    
    def test_get_s3_key(self):
        '''
        
        _get_s3_key 関数をテストする。
        
        * アップロード元ディレクトリのサブディレクトリに配置された各ファイルに
          ついて、関数の戻り値がs3パケットのフォルダ名とアップロード対象ファイル
          のアップロード先ディレクトリからの相対パスを'/'で連結したものと一致
          することを確認する。テストは、以下のパターンについて実施する。
        
          * アップロード元ディレクトリ名がディレクトリ区切り文字で終わらない場合
        
          * アップロード元ディレクトリ名がディレクトリ区切り文字で終る場合
        
        '''
        logging.info('>>>>> test_get_s3_key start')
        
        
        # アップロード元ディレクトリのサブディレクトリに配置された各ファイルに
        # ついて、関数の戻り値が第1引数で指定した文字列の後ろにアップロード先
        # ディレクトリからの相対パス（ディレクトリの区切りは'/'）を連結した
        # ものになることを確認する。
        logging.info('[test-01]')
        top_dir = os.path.join(os.path.dirname(__file__), 'test_files',
                              'AwsS3MoveTest')
        s3_folder_path = 'parent/child'
        for dirpath, dirnames, filenames in os.walk(top_dir):
            filenames.sort()
            for filename in filenames:
                s3key = aws_s3_upload._get_s3_key(s3_folder_path, top_dir,
                        os.path.join(dirpath, filename))
                relative_path = dirpath[len(top_dir):] + os.sep + filename
                if relative_path[0] == os.sep:
                    relative_path = relative_path[1:]
                expected = s3_folder_path + '/' + relative_path.replace(os.sep, '/')
                logging.info('s3key = ' + s3key)
                self.assertEqual(s3key, expected)

        # アップロード元ディレクトリ(最期がディレクトリ区切り文字の場合)を
        # テストする。
        logging.info('[test-02]')
        top_dir = top_dir + os.sep
        for dirpath, dirnames, filenames in os.walk(top_dir):
            filenames.sort()
            for filename in filenames:
                s3key = aws_s3_upload._get_s3_key(s3_folder_path, top_dir,
                        os.path.join(dirpath, filename))
                relative_path = dirpath[len(top_dir):] + os.sep + filename
                if relative_path[0] == os.sep:
                    relative_path = relative_path[1:]
                expected = s3_folder_path + '/' + relative_path.replace(os.sep, '/')
                logging.info('s3key = ' + s3key)
                self.assertEqual(s3key, expected)
        
        logging.info('<<<<< test_get_s3_key end')
    
    def test_get_s3_key_linux(self):
        '''
        
        ファイル区切り文字が'/'の場合の _get_s3_key 関数のテストを実施する。
        
        * アップロード元ディレクトリ名がファイル区切り文字で終わらない場合、
          正しい s3 キーを返すこと。
        * アップロード元ディレクトリ名がファイル区切り文字で終わる場合、
          正しい s3 キーを返すこと。
        
        '''
        logging.info('>>>>> test_get_s3_key_linux start')
        
        os.sep = '/'
        
        # アップロード元ディレクトリ名がファイル区切り文字で終わらない場合、
        # 正しい s3 キーを返すこと。
        s3_folder_path = 'parent/child'
        top_dir = '/home/hoge/test'
        dirpath = '/home/hoge/test/subdir'
        filename = 'test01.txt'
        s3key = aws_s3_upload._get_s3_key(s3_folder_path, top_dir,
                                          dirpath + os.sep + filename)
        expected = 'parent/child/subdir/test01.txt'
        logging.info('s3key = ' + s3key)
        self.assertEqual(s3key, expected)
        
        # アップロード元ディレクトリ名がファイル区切り文字で終わる場合、
        # 正しい s3 キーを返すこと。
        s3_folder_path = 'parent/child'
        top_dir = '/home/hoge/test/'
        dirpath = '/home/hoge/test/subdir'
        filename = 'test01.txt'
        s3key = aws_s3_upload._get_s3_key(s3_folder_path, top_dir,
                                          dirpath + os.sep+ filename)
        expected = 'parent/child/subdir/test01.txt'
        logging.info('s3key = ' + s3key)
        self.assertEqual(s3key, expected)
        
        logging.info('<<<<< test_get_s3_key_linux end')
    
    def test_get_s3_key_win(self):
        '''
        
        ファイル区切り文字が'\\'の場合の _get_s3_key 関数のテストを実施する。
        
        * アップロード元ディレクトリ名がファイル区切り文字で終わらない場合、
          正しい s3 キーを返すこと。
        * アップロード元ディレクトリ名がファイル区切り文字で終わる場合、
          正しい s3 キーを返すこと。
        
        '''
        logging.info('>>>>> test_get_s3_key_win start')
        
        os.sep = '\\'
        
        # アップロード元ディレクトリ名がファイル区切り文字で終わらない場合、
        # 正しい s3 キーを返すこと。
        s3_folder_path = 'parent/child'
        top_dir = 'C:\\home\\hoge\\test'
        dirpath = 'C:\\home\\hoge\\test\\subdir'
        filename = 'test01.txt'
        s3key = aws_s3_upload._get_s3_key(s3_folder_path, top_dir,
                                          dirpath + os.sep + filename)
        expected = 'parent/child/subdir/test01.txt'
        logging.info('s3key = ' + s3key)
        self.assertEqual(s3key, expected)
        
        # アップロード元ディレクトリ名がファイル区切り文字で終わる場合、
        # 正しい s3 キーを返すこと。
        s3_folder_path = 'parent/child'
        top_dir = 'C:\\home\\hoge\\test\\'
        dirpath = 'C:\\home\\hoge\\test\\subdir'
        filename = 'test01.txt'
        s3key = aws_s3_upload._get_s3_key(s3_folder_path, top_dir,
                                          dirpath + os.sep + filename)
        expected = 'parent/child/subdir/test01.txt'
        logging.info('s3key = ' + s3key)
        self.assertEqual(s3key, expected)
        
        logging.info('<<<<< test_get_s3_key_win end')
    
    @mock_aws
    def test_upload_file(self):
        '''
        
        アップロード元ファイルの削除を指定せずに、upload_file 関数を実行する。
        
        * アップロード元ディレクトリを指定して upload_file 関数を呼び出すと、
          アップロード元ディレクトリ配下のサブディレクトリを含む全てのファイルが
          s3のバケットにアップロードされることを確認する。
            * アップロード元ディレクトリ配下のファイルが削除されていないこと
            * アップロード元ディレクトリ配下のファイル数とS3バケット内の
            オブジェクトの数が一致すること

        * ファイルを１つアップロードする
            * アップロード元ディレクトリ配下のファイルが削除されていないこと
            * S3バケットのオブジェクトが１つであること
        
        '''
        logging.info('>>>>> test_upload_file start')
        
        s3_bucket_name = 'mybucket'
        s3_folder_path = 'parent/child'
        
        # テスト用のS3バケットを作成する
        s3_client = boto3.client('s3')
        s3_client.create_bucket(Bucket=s3_bucket_name)
        
        # アップロード元ディレクトリを指定して upload_file 関数を呼び出すと、
        # アップロード元ディレクトリ配下のサブディレクトリを含む全てのファイルが
        # s3のバケットにアップロードされることを確認する。
        # ディレクトリ配下のファイルをアップロードする
        top_dir = os.path.join(os.path.dirname(__file__), 'test_files',
                              'AwsS3MoveTest')
        filelist_before = aws_test_utils.list_files_in_dir(top_dir)
        aws_s3_upload.upload_file(top_dir, s3_bucket_name, s3_folder_path)
        filelist_after = aws_test_utils.list_files_in_dir(top_dir)
        #     アップロード元ディレクトリ配下のファイルが削除されていないこと
        self.assertTrue(len(filelist_after) > 0)
        self.assertEqual(filelist_before, filelist_after)
        #     アップロード元ディレクトリ配下のファイル数とS3バケットの
        #     オブジェクトの数が一致すること
        objlist = s3_client.list_objects(Bucket=s3_bucket_name)
        s3keys = aws_test_utils.list_s3keys_in_bucket(objlist)
        logging.info('S3 Keys: ' + str(s3keys))
        filelist_before.sort()
        s3keys.sort()
        self.assertEqual(len(filelist_before), len(s3keys))
        
        # S3バケットを作り直す
        self._delete_all_objects(s3_bucket_name)
        s3_client.delete_bucket(Bucket=s3_bucket_name)
        s3_client.create_bucket(Bucket=s3_bucket_name)
        
        # ファイルを１つアップロードする
        file_path = os.path.join(top_dir, 'test_file_01.txt')
        aws_s3_upload.upload_file(file_path, s3_bucket_name)
        #     ファイルが削除されていないこと
        self.assertTrue(os.path.exists(file_path))
        #     S3バケットのオブジェクトが１つであること
        objlist = s3_client.list_objects(Bucket=s3_bucket_name)
        s3keys = aws_test_utils.list_s3keys_in_bucket(objlist)
        self.assertEqual(len(s3keys), 1)

        logging.info('<<<<< test_upload_file end')
    
    @mock_aws
    def test_move_file(self):
        '''
        
        アップロード元ファイルの削除を指定して、upload_file 関数を実行する。

        * アップロード元ディレクトリを指定して upload_file 関数を呼び出すと、
          アップロード元ディレクトリ配下のサブディレクトリを含む全てのファイルが
          s3のバケットに移動されることを確認する。
            * 移動元ディレクトリの下にファイル・ディレクトリが存在しないこと
            * 移動前のアップロード元ディレクトリ配下のファイル数とS3バケットの
            オブジェクトの数が一致すること
        
        * ファイルを１つ移動する
            * コピー元ファイルが存在しないこと
            * S3バケットのオブジェクトが１つであること
        
        '''
        logging.info('>>>>> test_move_file start')
        
        s3_bucket_name = 'mybucket'
        s3_folder_path = 'parent/child'
        
        # テスト用のS3バケットを作成する
        s3_client = boto3.client('s3')
        s3_client.create_bucket(Bucket=s3_bucket_name)
        
        # 移動用のファイルを作業ディレクトリにコピーするための準備
        copy_from = os.path.join(os.path.dirname(__file__), 'test_files',
                              'AwsS3MoveTest')
        top_dir = os.path.join(os.path.dirname(__file__), 'work',
                              'AwsS3MoveTest')
        
        # 移動元のファイルを作業ディレクトリの下にコピーする
        shutil.copytree(copy_from, top_dir, dirs_exist_ok=True)
        # アップロード元ディレクトリを指定して upload_file 関数を呼び出すと、
        # アップロード元ディレクトリ配下のサブディレクトリを含む全てのファイルが
        # s3のバケットに移動されることを確認する。
        # ディレクトリ配下のファイルを移動する
        filelist_before = aws_test_utils.list_files_in_dir(top_dir)
        aws_s3_upload.upload_file(top_dir, s3_bucket_name, s3_folder_path, True)
        #     移動元ディレクトリの下にファイル・ディレクトリが存在しないこと
        filelist_after = aws_test_utils.list_files_in_dir(top_dir)
        self.assertEqual(len(filelist_after), 0)
        #     移動前のアップロード元ディレクトリ配下のファイル数とS3バケットの
        #     オブジェクトの数が一致すること
        objlist = s3_client.list_objects(Bucket=s3_bucket_name)
        s3keys = aws_test_utils.list_s3keys_in_bucket(objlist)
        self.assertEqual(len(filelist_before), len(s3keys))
        
        # S3バケットを作り直す
        self._delete_all_objects(s3_bucket_name)
        s3_client.delete_bucket(Bucket=s3_bucket_name)
        s3_client.create_bucket(Bucket=s3_bucket_name)
        
        # 移動元のファイルを作業ディレクトリの下にコピーする
        shutil.copytree(copy_from, top_dir, dirs_exist_ok=True)
        # ファイルを１つ移動する
        file_path = os.path.join(top_dir, 'test_file_01.txt')
        aws_s3_upload.upload_file(file_path, s3_bucket_name, s3_folder_path, True)
        #     コピー元ファイルが存在しないこと
        self.assertFalse(os.path.exists(file_path))
        #     S3バケットのオブジェクトが１つであること
        objlist = s3_client.list_objects(Bucket=s3_bucket_name)
        s3keys = aws_test_utils.list_s3keys_in_bucket(objlist)
        self.assertEqual(len(s3keys), 1)
        
        logging.info('<<<<< test_move_file end')
    
    @mock_aws
    def test_main(self):
        '''
        
        aws_s3_upload.py をスクリプト実行するテストを実施する。
        
        * 4番目の引数を指定せずに main 関数を呼び出すと、アップロード元
          ディレクトリ配下のサブディレクトリを含む全てのファイルがs3の
          バケットにアップロードされることを確認する。
            * 移動元ディレクトリの下のファイル・ディレクトリが削除されないこと
            * 移動前のアップロード元ディレクトリ配下のファイル数とS3バケットの
              オブジェクトの数が一致すること
        
        * 4番目の引数に'True'を指定しえ main 関数を呼び出すと、アップロード元
          ディレクトリ配下のサブディレクトリを含む全てのファイルがs3のバケットに
          移動されることを確認する。
            * 移動元ディレクトリの下にファイル・ディレクトリが存在しないこと
            * 移動前のアップロード元ディレクトリ配下のファイル数とS3バケットの
              オブジェクトの数が一致すること
        
        '''
        logging.info('>>>>> test_main start')
        
        s3_bucket_name = 'test_buckeet'
        s3_folder_path = 'key01/key02'
        
        # テスト用のS3バケットを作成する
        s3_client = boto3.client('s3')
        s3_client.create_bucket(Bucket=s3_bucket_name)
        
        # 移動用のファイルを作業ディレクトリにコピーするための準備
        copy_from = os.path.join(os.path.dirname(__file__), 'test_files',
                              'AwsS3MoveTest')
        top_dir = os.path.join(os.path.dirname(__file__), 'work',
                              'AwsS3MoveTest')
        
        # 移動元のファイルを作業ディレクトリの下にコピーする
        shutil.copytree(copy_from, top_dir, dirs_exist_ok=True)
        
        # 4番目の引数を指定せずに main 関数を呼び出すと、アップロード元
        # ディレクトリ配下のサブディレクトリを含む全てのファイルがs3の
        # バケットにアップロードされることを確認する。
        # main 関数に渡す引数を設定する
        args = [os.path.join(os.path.dirname(__file__), '../src/main/awsutils/aws_s3_upload.py'),
                top_dir, s3_bucket_name, s3_folder_path]
        # ディレクトリ配下のファイルをS3にアップロードする
        filelist_before = aws_test_utils.list_files_in_dir(top_dir)
        aws_s3_upload.main(args)
        #     移動元ディレクトリの下のファイル・ディレクトリが削除されないこと
        filelist_after = aws_test_utils.list_files_in_dir(top_dir)
        self.assertTrue(len(filelist_before) > 0)
        self.assertEqual(len(filelist_after), len(filelist_before))
        #     移動前のアップロード元ディレクトリ配下のファイル数とS3バケットの
        #     オブジェクトの数が一致すること
        objlist = s3_client.list_objects(Bucket=s3_bucket_name)
        s3keys = aws_test_utils.list_s3keys_in_bucket(objlist)
        self.assertEqual(len(filelist_before), len(s3keys))
        
        # S3バケットを作り直す
        self._delete_all_objects(s3_bucket_name)
        s3_client.delete_bucket(Bucket=s3_bucket_name)
        s3_client.create_bucket(Bucket=s3_bucket_name)
        
        # 移動元のファイルを作業ディレクトリの下にコピーする
        shutil.copytree(copy_from, top_dir, dirs_exist_ok=True)
        # 4番目の引数に'True'を指定しえ main 関数を呼び出すと、アップロード元
        # ディレクトリ配下のサブディレクトリを含む全てのファイルがs3のバケットに
        # 移動されることを確認する。
        # main 関数に渡す引数を設定する
        args = [os.path.join(os.path.dirname(__file__), '../src/main/awsutils/aws_s3_upload.py'),
                top_dir, s3_bucket_name, s3_folder_path, 'True']
        # ディレクトリ配下のファイルをS3に移動する
        filelist_before = aws_test_utils.list_files_in_dir(top_dir)
        aws_s3_upload.main(args)
        #     移動元ディレクトリの下にファイル・ディレクトリが存在しないこと
        filelist_after = aws_test_utils.list_files_in_dir(top_dir)
        self.assertEqual(len(filelist_after), 0)
        #     移動前のアップロード元ディレクトリ配下のファイル数とS3バケットの
        #     オブジェクトの数が一致すること
        objlist = s3_client.list_objects(Bucket=s3_bucket_name)
        s3keys = aws_test_utils.list_s3keys_in_bucket(objlist)
        self.assertEqual(len(filelist_before), len(s3keys))
        
        logging.info('<<<<< test_main end')
    
    @mock_aws
    def test_move_file_err(self):
        '''
        
        アップロード元ファイルの削除を指定して、エラーが発生する状態で
        upload_file 関数を実行する。
        
        * 移動元フォルダに存在しないパスを指定してファイルを移動する
            * 例外が発生し、メッセージに「Not found」が含まれること
        
        * S3バケットを削除してテストする
            * 例外が発生し、メッセージに「Failed to upload」が含まれること
            * 移動元ディレクトリ配下のファイルが削除されていないこと
        
        * ファイルを１つ移動する
            * 例外が発生し、メッセージに「Failed to upload」が含まれること
            * コピー元ファイルが削除されていないこと
        
        '''
        logging.info('>>>>> test_move_file_err start')
        
        s3_bucket_name = 'mybucket'
        s3_folder_path = 'parent/child'
        
        # テスト用のS3バケットを作成する
        s3_client = boto3.client('s3')
        s3_client.create_bucket(Bucket=s3_bucket_name)
        
        # 移動用のファイルを作業ディレクトリにコピーするための準備
        copy_from = os.path.join(os.path.dirname(__file__), 'test_files',
                              'AwsS3MoveTest')
        top_dir = os.path.join(os.path.dirname(__file__), 'work',
                              'AwsS3MoveTest')

        # 移動元のファイルを作業ディレクトリの下にコピーする
        shutil.copytree(copy_from, top_dir, dirs_exist_ok=True)
        
        # 移動元フォルダに存在しないパスを指定してファイルを移動する
        with self.assertRaises(Exception, msg='Not found') as cm:
            aws_s3_upload.upload_file(top_dir + '_NOR_EXISTS', s3_bucket_name, s3_folder_path, True)
        #     例外が発生し、メッセージに「Not found」が含まれること
        logging.info('Raised exception: ' + str(cm.exception))
        
        # S3バケットを削除してテストする
        self._delete_all_objects(s3_bucket_name)
        s3_client.delete_bucket(Bucket=s3_bucket_name)
        # ディレクトリ配下のファイルを移動する
        filelist_before = aws_test_utils.list_files_in_dir(top_dir)
        with self.assertRaises(Exception, msg='Failed to upload') as cm:
            aws_s3_upload.upload_file(top_dir, s3_bucket_name, s3_folder_path, True)
        #     例外が発生し、メッセージに「Faild to upload」が含まれること
        logging.info('Raised exception: ' + str(cm.exception))
        filelist_after =  aws_test_utils.list_files_in_dir(top_dir)
        #     移動元ディレクトリ配下のファイルが削除されていないこと
        self.assertTrue(len(filelist_after) > 0)
        self.assertEqual(filelist_before, filelist_after)
        
        # ファイルを１つ移動する
        file_path = os.path.join(top_dir, 'test_file_01.txt')
        with self.assertRaises(Exception, msg='Failed to upload') as cm:
            aws_s3_upload.upload_file(file_path, s3_bucket_name, s3_folder_path, True)
        #     例外が発生し、メッセージに「Failed to upload」が含まれること
        logging.info('Raised exception: ' + str(cm.exception))
        #     コピー元ファイルが削除されていないこと
        self.assertTrue(os.path.exists(file_path))
        
        logging.info('<<<<< test_move_file_err stop')

if __name__ == '__main__':
    unittest.main()

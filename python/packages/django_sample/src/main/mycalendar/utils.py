import logging
import sys

def init_logging(stream:str='stdout', filename:str=None, level:str='INFO'):
    '''loggingを初期化する。
    Args:
        stream (str): ログ出力先のストリーム（'stdout' または 'stderr'）を
            指定する。stream、filename はどちらか一方を指定すること。
        filename (str): ログファイルのパスを指定する。
            stream、filename はどちらか一方を指定すること。
        level (str): ログのレベルを以下の文字列で指定する。
            - 'CRITICAL'
            - 'ERROR'
            - 'WARNING'
            - 'INFO'
            - 'DEBUG'
            - 'NOTSET'
    '''
    # stream
    param_stream = None
    if stream == 'stdout':
        param_stream = sys.stdout
    elif stream == 'stderr':
        param_stream = sys.stderr
    # filename
    param_filename:str = None
    if filename != None:
        param_filename = filename
    # level
    param_level = None
    if level == 'CRITICAL':
        param_level = logging.CRITICAL
    elif level == 'ERROR':
        param_level = logging.ERROR
    elif level == 'WARNING':
        param_level = logging.WARNING
    elif level == 'INFO':
        param_level = logging.INFO
    elif level == 'DEBUG':
        param_level = logging.DEBUG
    elif level == 'NOTSET':
        param_level = logging.NOTSET

    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)

    if param_filename:
        logging.basicConfig(filename=param_filename, level=param_level)
    else:
        logging.basicConfig(stream=param_stream, level=param_level)

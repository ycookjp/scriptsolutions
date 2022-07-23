# -*- coding: utf-8 -*-

def substring(target: str, beginIndex: int, endIndex: int = None):
    '''
    
    開始、終了インデックスを指定して部分文字列を取得します。
    
    Args:
        target (str): 入力文字列
        beginIndex (int): 部分文字列の開始インデックスを指定します。
            部分文字列はこのインデックスから開始します。
        endIndex (int) 部分文字列の終了インデックスを指定します。部分文字列は
            このインデックスの１つ前の文字で終了します。このパラメータを省略した
            場合は、部分文字列は開始インデックスから文字列の最後までになります。
    
    Returns:
        str: 取得した部分文字列を返します。
    
    '''
    ret:str = ''
    if endIndex == None:
        endIndex = len(target)
    
    i = 0
    while i <= endIndex:
        ret = ret + target[i]
        i += 1
    
    return ret

# -*- coding: utf-8 -*-

'''mypackage

Copyright ycookjp
https://github.com/ycookjp/

'''

from datetime import datetime

def find_repeat(target: str, sub: str, start: int=0, end: int=-1):
    '''
    
    部分文字列が最初に出現した位置と連続する出現回数を取得します。
    
    Args:
        target (str): 部分文字列を探す対象の文字列を指定します。
        sub (str): 出現を調べる部分文字列を指定します。
        start (int, optional): 部分文字列の出現を調べる範囲の開始
            位置のインデックスを指定します。省略した時は、文字列の最初から
            出現を調べます。
        end (int, optional): 部分文字列の出現を調べる範囲の終了位置
            （指定されたインデックスの１つ前までを調べる）を指定します。
    
    Returns:
        list: 最初の養子に部分文字列が最初に出現した位置のインデックス、
            2番目の要素に出現回数を設定した配列を返します。
    
    '''
    if end < 0:
        end = len(target)

    pos: int = target.find(sub, start, end)
    count: int = 0

    if pos >= 0:
        next_pos: int = pos
        while next_pos >= 0:
            count += 1
            next_pos: int = target.find(sub, next_pos + len(sub), end)
    
    return [pos, count]

def format_date(date: datetime, formatstr: str):
    '''
    
    書式文字列に従って datetime を文字列に変換します。
    書式文字列の変換規則は以下のとおりです。
    
    * 書式文字列に'y', 'M', 'd', 'h', 'm', 's' の文字が含まれる場合、その部分を
      それぞれ date の年、月、時、分、秒に置換します。
    * 上記の文字が連続する場合は数値の桁を定義したことになります。連続する文字
      の個数よりも数値の桁が小さい場合は、数値の前に所定の桁数になるまで"0"を
      追加します。
    * 書式文字列が"7"の場合、数値（年）の桁数が書式文字列で設定された桁数より
      大きい場合は、書式文字列の桁数になるように数値の左側を切り捨てます。
    
    Args:
        date (datetime): datetimeオブジェクト
        formatstr (str): 書式文字列
    Returns:
        srr: 書式文字列に従って変換された文字列を返します。
    '''
    converted: str = ""
    start: int = 0
    end: int = len(formatstr)
    
    while start < end:
        c = formatstr[start]
        if c == "y" or c == "M" or c == "d" or c == "h" or c == "m" or c == "s":
            datechar = formatstr[start]
            found = find_repeat(formatstr, datechar, start, end)
            count = found[1] 
            
            if datechar == "y":
                val = str(date.year)
                
                if len(val) > count:
                    val = val[len(val)-count:len(val)]
            else:
                if datechar == "M":
                    val = str(date.month)
                elif datechar == "d":
                    val = str(date.day)
                elif datechar == "h":
                    val = str(date.hour)
                elif datechar == "m":
                    val = str(date.minute)
                elif datechar == "s":
                    val = str(date.second)
            
            if len(val) < count:
                val = "0" * (count - len(val)) + val
            converted = converted + val
            start = start + count
        else:
            converted = converted + formatstr[start]
            start += 1
    
    return converted

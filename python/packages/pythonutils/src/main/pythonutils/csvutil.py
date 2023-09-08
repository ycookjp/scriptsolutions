# -*- config: utf8 -*-
'''csvutil module.

Copyright ycookjp
https://github.com/ycookjp/

'''

from io import TextIOBase

def _delete_line_break(strdata: str) -> str:
    '''文字列の最後の改行コードを除去する。
    
    Arguments:
        strdata (str): 文字列

    Returns:
        引数で指定された文字列の最後に改行コードが存在した場合は、その改行
        コードを除去した文字列を返す。そうでない場合は、引数で指定された文字列を
        そのまま返す。
    
    '''
    if strdata[len(strdata)-2:len(strdata)] == '\r\n':
        strdata = strdata[:len(strdata) - 2]
    elif strdata[len(strdata)-1] == '\n':
        strdata = strdata[:len(strdata)-1]
    
    return strdata

def _trim_double_quote(strdata: str):
    '''文字列の先頭と終わりのダブルクォートを除去する。
    
    Arguments:
        strdata (str): 文字列
    
    Returns:
        引数で指定された文字列の先頭と最後の文字が共にダブルクォートの場合は
        そのダブルクォートを除去した文字列を返す。またその場合に連続した２つの
        ダブルクォートは１つのダブルクォートに置換する。

    '''
    if (len(strdata) > 1 and strdata[0] == '"'
            and strdata[len(strdata) - 1] == '"'):
        strdata = strdata[1:len(strdata)-1]
        strdata = strdata.replace('""', '"')
    
    return strdata

def read_csv(istream: TextIOBase) -> list:
    '''ストリームからCSVの１行のデータをlistで反復して返す。
    
    CSV形式の文字列からCSVの項目を要素とするlistを生成して返却する処理は
    以下のとおりである。
    
    1. 「"」が見つかったら次の「"」が見つかるまでコンマや改行を含めて読み込んだ
      文字列を現在処理中のlist項目の文字列に追加する。
    2. カンマが見つかったら、現在処理中のList項目の文字列をlistに追加して、
      次のList項目の文字列追加処理を開始する。その際追加されたlist項目の文字列の
      先頭と最後が「"」である場合は、最初と最後の「"」を除去し、連続する２つの
      「"」は１つの「"」に変換する。
    3. 改行またはストリームの終わりに達したら、現在処理中のlist項目の文字列から
      最後の改行コードを除いてlistに追加してそのlistを返す。なお、追加された
      list項目の文字列の先頭と最後が「"」の場合の扱いは、カンマが見つかった場合
      と同様である。

    Args:
        istream (TextIOBase): 入力ストリーム
    
    Examples:
        ストリームを読み込みCSVの１行のデータを配列にして返す処理の例

            from pythonutils import csvutil
            ...
            with open('/path/to/sample.csv', 'r', encoding=''utf-8) as f:
                for rowdata in csvutil.read_csv(f):
                    line = ''
                    for celldata in rowdata:
                        line = line + (',' if len(line) > 0 else '') + celldata
                    print(line)

    '''
    in_dquote: bool = False
    csvcol = ''
    rowdata = []

    while True:
        # ストリームから１行読み込む
        line: str = istream.readline()
        # ストリームの終わりに達したら処理を終了する
        if not line:
            break
        index = 0
        # １行の文字列を順に調べる
        while index < len(line):
            # ダブルクォートの中である場合
            if in_dquote:
                # 次のダブルクォートの出現位置を取得
                dqidx = line.find('"', index)
                # 次のダブルクォートが見つからない場合は改行を含む行末までの
                # 文字列をセルの文字に追加して、次の行を読み込む
                if dqidx < 0:
                    csvcol = csvcol + line[index:]
                    index = len(line)
                # 次のダブルクォートの文字が見つかったらそこまでの文字列をセルの
                # 文字に追加して、それ以降の文字を処理する
                else:
                    csvcol = csvcol + line[index:dqidx+1]
                    index = dqidx + 1
                    in_dquote = False
                continue
            # 次のダブルクォート、カンマの出現位置を取得
            dqidx = line.find('"', index)
            cmidx = line.find(',', index)
            # ダブルクォートの前にコンマが存在しない場合
            # ダブルクォートまでをセルの文字列に追加する
            if dqidx >= 0 and (cmidx < 0 or dqidx < cmidx):
                csvcol = csvcol + line[index:dqidx+1]
                in_dquote = True
                index = dqidx + 1
            # コンマの前にダブルクォートが存在しない場合
            # コンマの前までの文字列をセルの文字列に追加し、次のセルの処理を開始
            elif cmidx >= 0:
                csvcol = csvcol + line[index:cmidx]
                rowdata.append(_trim_double_quote(csvcol))
                csvcol = ''
                index = cmidx + 1
            # コンマもダブルクォートも存在しない場合
            # 行末までの文字をセルの文字列に追加し、１行分のCSVデータを返す
            else:
                csvcol = _delete_line_break(csvcol + line[index:])
                rowdata.append(_trim_double_quote(csvcol))
                yield rowdata
                csvcol = ''
                rowdata = []
                break

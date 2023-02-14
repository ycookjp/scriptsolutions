'''View module.

Copyright ycookjp

https://github.com/ycookjp/

'''
from .models import MyCalendar

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError
#from django.shortcuts import render

import calendar
import json

# Create your views here.

def _check_date(year:int, month:int, day:int=None, errmsg:str=None):
    '''年月日の範囲チェックを実行する。

    以下のチェックを実行する。
    
    * 月：1以上12以下であること
    * 日：1以上パラメータで指定した年月の最終日以下であること
    
    Args:
        year (int): 年
        month (int): 月
        day (int): 日
        errmsg (str): エラーメッセージ
    
    Raises:
        ValidationError:
          * 月が1より小さい、または12より大きい場合
          * 日が1より小さい、または月の最終日より大きい場合
    
    '''
    if not errmsg:
        errmsg = 'Input date error.'
    if month < 1 or month > 12:
        raise ValidationError(errmsg)
    elif day!=None and (day < 1 or day > calendar.monthrange(year, month)[1]):
        raise ValidationError(errmsg)

def _create_monthly(user:str, year:int, month:int):
    '''１ヶ月のカレンダー情報を登録する。
    
    指定されたユーザー、年月の１日から最終日までのカレンダー情報を登録する。
    
    Args:
        user (str): ユーザー名
        year (int): 年
        month (int): 月
    
    Returns:
        登録したレコード数
    
    '''
    # 月の最終日を取得する
    last_day:int = calendar.monthrange(year, month)[1]
    # 指定された月の１日から最終日までのカレンダー情報を登録する。
    for index in range(1, last_day+1):
        instance = MyCalendar(user=user, year=year, month=month, day=index)
        instance.save()
    
    return last_day

def get_daily(request:HttpRequest, user:str , year:int, month:int, day:int):
    '''GET get_daily/<str:user\>/<int:year\>/<int:month\>/<int:day\>/
    
    年月日を指定してカレンダー情報を取得する。
    
    * データベースから指定されたユーザー、年月日の MyCalendar オブジェクトを
      取得する。
    * データベースに指定されたユーザー、年月日の MyCalendar オブジェクトが存在
      しない場合は、ユーザーのその月の MyCalendar オブジェクトをデータベースに
      作成した上で、指定された年月日の MyCalendar オブジェクトを返す。
    
    Args:
        request (HttpRequest): リクエストオブジェクト
        user (str): ユーザー名
        year (int): 年
        month (int): 月
        day(int): 日
    
    Returns:
        JsonResponse: 指定された年月日の MyCalendar オブジェクトの内容を設定
            したJSONオブジェクトレスポンス・ボディに設定して返す。
        
                {
                  "id": ID,
                  "user": "<user_name>",
                  "year": <year>,
                  "month": <month>,
                  "day": <day>,
                  "note": "<note>"
                }
    
    Raises:
        ValidationError
        
          * URLパラメータの month の値が 1 より小さい、または 12 より大きい場合
          * URLパラメータの day の値が 1 より大きい、または month で指定された
            月の最終日より大きい場合
    
    '''
    # 日付の入力チェック
    _check_date(year, month, day)
    
    # 指定されたユーザー、年月日のMyCalendarオブジェクトを検索する
    cals = MyCalendar.objects.filter(user=user, year=year, month=month, day=day)
    
    if len(cals) > 0:
        cal = cals[0]
    else:
        # 年月日を指定してMyCalendarが取得できない場合は１ヶ月分のMyCalendar
        # オブジェクトをデータベースに登録する
        _create_monthly(user, year, month)
        # データベースから引数で指定されたユーザー、年月日のMyClass
        # オブジェクトを取得する
        cal = MyCalendar.objects.get(user=user, year=year, month=month, day=day)
    
    # モデルをDictionaryに変換する
    response_data = model_to_dict(cal)
    # JSON形式で応答を返す
    return JsonResponse(response_data)

def get_monthly(request:HttpRequest, user:str, year:int, month:int):
    '''GET get_monthly/<str:user\>/<int:year\>/<int:month\>/
    
    年月を指定してカレンダー情報を取得する。
    
    Args:
        request (HttpRequest): リクエストオブジェクト
        user (str): ユーザー名
        year (int): 年
        month (int): 月
    
    Returns:
        JsonResponse: 指定された年月のカレンダー情報の配列を設定したJSON
            オブジェクトをレスポンス・ボディに設定して返す。
        
                [
                  {
                    "id": ID,
                    "user": "<user_name>",
                    "year": <year>,
                    "month": <month>,
                    "day": <day>,
                    "note": "<note>"
                  },
                  ...
                ]
    
    Raises:
        ValidationError
        
          * URLパラメータの month の値が 1 より小さい、または 12 より大きい場合
    
    '''
    # 日付の入力チェック
    _check_date(year, month, errmsg='Input month error.')
    
    # 指定されたユーザー、年月の１日のカレンダー情報を取得する
    cals = MyCalendar.objects.filter(user=user, year=year, month=month, day=1)
    
    # 指定された月のカレンダー情報が存在しない場合は、その月のデータを登録する。
    if len(cals) == 0:
        _create_monthly(user, year, month)
    
    # 指定された年月のカレンダー情報を取得する
    cals = MyCalendar.objects.filter(user=user, year=year, month=month).order_by('day')

    # モデルをDictionaryに変換する
    response_data = []
    for cal in cals:
        response_data.append(model_to_dict(cal))
    # JSON形式で応答を返す。
    return JsonResponse(response_data, safe=False)

def save_daily(request:HttpRequest, user:str, year:int, month:int, day:int):
    '''PUT save_daily/<str:user\>/<int:year\>/<int:month\>/<int:day\>/
    
    年月日を指定してカレンダー情報を登録・更新する。
    
    * リクエスト・ボディ
    
            {
              "id": ID,
              "user": "<user_name>",
              "year": <year>,
              "month": <month>,
              "day": <day>,
              "note": "<note>"
            }
    
        * 登録（レコードのインサート）の場合は、「id」は指定しない（項目なし
          または値が空）
        * URLパラメータで指定された年月のカレンダー情報がDBに登録されていない
          場合は、その年月の１ヶ月分のカレンダー情報をDBに登録した後に、
          リクエスト・ボディに設定されたカレンダー情報をDBに更新する
    
    Args:
        request (HttpRequest): リクエストオブジェクト
        user (str): ユーザー名
        year (int): 年
        month (int): 月
        day(int): 日
    
    Raises:
        ValidationError:
        
          * URLパラメータの user、year、month、day がリクエスト・ボディの
            JSONオブジェクトのそれぞれの同名の属性と一致しないものがある場合
          * URLパラメータの month の値が 1 より小さい、または 12 より大きい場合
          * URLパラメータの day の値が 1 より大きい、または month で指定された
            月の最終日より大きい場合
    
    '''
    # 日付の入力チェック
    _check_date(year, month, day)
    
    # リクエスト・ボディをJSONオブジェクトで取得する
    json_data = json.loads(request.body)
    # 取得したJSONオブジェクトをMyCalendarクラスのインスタンスに変換する
    mycalendar:MyCalendar = MyCalendar.deserialize(json_data)
    
    # URLパラメータが登録データと一致することを確認する
    if mycalendar.user != user or mycalendar.year != year \
            or mycalendar.month != month or mycalendar.day != day:
        raise ValidationError('URL parameter(s) and request body not matched.')
    
    # URLパラメータで指定された年月の1日のカレンダー情報を取得して存在
    # しなければその月のカレンダー情報を登録する
    cals = MyCalendar.objects.filter(user=user, year=year, month=month, day=1)
    if len(cals) == 0:
        _create_monthly(user, year, month)
    
    # リクエスト・ボディにidが指定されていない場合はDBから取得する
    if mycalendar.id == None:
        cal = MyCalendar.objects.get(user=user, year=year, month=month, day=day)
        mycalendar.id = cal.id
    # リクエストされた登録データをデータベース辞登録する
    mycalendar.save()
    
    return HttpResponse()

def save_monthly(request:HttpRequest, user:str, year:int, month:int):
    '''PUT save_monthly/<str:user\>/<int:year\>/<int:month\>/
    
    年月を指定してカレンダー情報を登録・更新する。
    
    * リクエスト・ボディ
    
            [
              {
                "id": ID,
                "user": "<user_name>",
                "year": <year>,
                "month": <month>,
                "day": <day>,
                "note": "<note>"
              },
              ...
            ]
    
        * 登録（レコードのインサート）の場合は、「id」は指定しない（項目なし
          または値が空）
        * URLパラメータで指定された年月のカレンダー情報がDBに登録されていない
          場合は、その年月の１ヶ月分のカレンダー情報をDBに登録した後に、
          リクエスト・ボディに設定されたカレンダー情報をDBに更新する
    
    Args:
        request (HttpRequest): リクエストオブジェクト
        user (str): ユーザー名
        year (int): 年
        month (int): 月
    
    Raises:
        ValidationError:
        
          * URLパラメータのmonthの値が1より小さい、または12より大きい場合
          * リクエスト・ボディのディクショナリ配列の個々の要素について、
            monthの値が1より小さい、または12より大きい場合
          * リクエスト・ボディのディクショナリ配列の個々の要素について、
            dayの値が1より小さい、または月の最終日より大きい場合
    
    '''
    # 日付の入力チェック
    _check_date(year, month, errmsg='Input month error.')
    
    # リクエスト・ボディをJSONオブジェクトで取得する
    json_datas = json.loads(request.body)
    # 取得したJSONオブジェクトをMyCalendarクラスのインスタンスの配列に変換して
    # 入力チェックする
    request_data = []
    for json_data in json_datas:
        mycalendar:MyCalendar = MyCalendar.deserialize(json_data)
        # URLパラメータの user、year、month と一致していることを確認する
        if mycalendar.user != user or mycalendar.year != year or mycalendar.month != month:
            raise ValidationError('URL parameter(s) and request body not matched.')
        # 日付のの入力チェック
        _check_date(mycalendar.year, mycalendar.month, mycalendar.day)
        # 変換したMyCalendarのインスタンスを配列に追加する
        request_data.append(mycalendar)
    
    # URLパラメータで指定された年月の1日のカレンダー情報を取得して存在
    # しなければその月のカレンダー情報を登録する
    cals = MyCalendar.objects.filter(user=user, year=year, month=month, day=1)
    if len(cals) == 0:
        _create_monthly(user, year, month)
    
    # idを取得するためにURLパラメータで指定された年月のレコードを取得する
    cals = MyCalendar.objects.filter(user=user, year=year, month=month).order_by('day')
    # リクエスト・ボディのMyCalenderインスタンス配列の要素純に処理する
    for data in request_data:
        # 更新対象のデータにidが設定されていない場合は年月のレコードのidを設定する
        if data.id == None:
            data.id = cals[data.day - 1].id
        # MyCalanderインスタンスの内容をDBに更新する
        data.save()
    
    return HttpResponse()

def delete_monthly(request:HttpRequest, user:str, year:int, month:int):
    '''DELETE delete_monthly/<str:user\>/<int:year\>/<int:month\>/
    
    年月を指定してカレンダー情報を削除する。
    
    Args:
        request (HttpRequest): リクエストオブジェクト
        user (str): ユーザー名
        year (int): 年
        month (int): 月
    
    Raises:
        ValidationError:
        
          * URLパラメータのmonthの値が1より小さい、または12より大きい場合
    
    '''
    # 日付の入力チェック
    _check_date(year, month, errmsg='Input month error.')
    
    # URLパラメータで指定された年月のカレンダー情報を削除する
    MyCalendar.objects.filter(user=user, year=year, month=month).delete()
    
    return HttpResponse()

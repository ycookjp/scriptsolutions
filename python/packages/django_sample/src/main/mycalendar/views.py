from .models import MyCalendar

from django.http import HttpRequest, JsonResponse
from django.forms.models import model_to_dict
#from django.shortcuts import render

import calendar

# Create your views here.

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
    '''get_daily/<str:user\>/<int:year\>/<int:month\>/<int:day\>/
    
    年月日を指定してカレンダー情報を取得する。
    
    データベースから指定されたユーザー、年月日の MyCalendar オブジェクトを
    取得する。
    
    データベースに指定されたユーザー、年月日の MyCalendar オブジェクトが存在
    しない場合は、ユーザーのその月の MyCalendar オブジェクトをデータベースに
    作成した上で、指定された年月日の MyCalendar オブジェクトを返す。
    
    Args:
        request (HttpRequest): リクエストオブジェクト
        user (str): ユーザー名
        year (int): 年
        month (int): 月
        day(int): 日
    
    Returns:
        dict: 指定された年月日の MyCalendar オブジェクトの内容を設定した
            ディクショナリを返す。
        
            {
              response_data: {
                "user": "<user_name>",
                "year": <year>,
                "month": <month>,
                "day": <day>,
                "note": "<note>"
              }
            }
    
    '''
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
    return JsonResponse({'response_data':response_data})

def get_monthly(request:HttpRequest, user, year:int, month:int):
    '''get_monthly/<str:user\>/<int:year\>/<int:month\>/
    
    年月を指定してカレンダー情報を取得する。
    
    Args:
        request (HttpRequest): リクエストオブジェクト
        user (str): ユーザー名
        year (int): 年
        month (int): 月
    
    '''
    # 指定されたユーザー、年月の１日の関連だー情報を取得する
    cals = MyCalendar.objects.filter(user=user, year=year, month=month, day=1)
    
    # 指定された月のカレンダー情報が存在しない場合は、その月のデータを登録する。
    if len(cals) == 0:
        _create_monthly(user, year, month)
    
    # 指定された年月のカレンダー情報を取得する
    cals = MyCalendar.objects.filter(user=user, year=year, month=month)

    # モデルをDictionaryに変換する
    response_data = []
    for cal in cals:
        response_data.append(model_to_dict(cal))
    # JSON形式で応答を返す。
    return JsonResponse({'response_data':response_data})

def save_daily(request:HttpRequest, year:int, month:int, day:int):
    '''年月日を指定してカレンダー情報を登録・更新する。
    
    Args:
        request (HttpRequest): リクエストオブジェクト
        user (str): ユーザー名
        year (int): 年
        month (int): 月
        day(int): 日
    
    '''
    pass

def save_monthly(request:HttpRequest, year:int, month:int):
    '''年月を指定してカレンダー情報を登録・更新する。
    
    Args:
        request (HttpRequest): リクエストオブジェクト
        user (str): ユーザー名
        year (int): 年
        month (int): 月
    
    '''
    pass

def delete_monthly(request:HttpRequest, year:int, month:int):
    '''年月を指定してカレンダー情報を削除する。
    
    Args:
        request (HttpRequest): リクエストオブジェクト
        user (str): ユーザー名
        year (int): 年
        month (int): 月
    
    '''
    pass

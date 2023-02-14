'''Test module.

Copyright ycookjp

https://github.com/ycookjp/

'''
from .models import MyCalendar
from .utils import init_logging

from django.test import TestCase
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.core.exceptions import ValidationError
import calendar
import logging
import json

# Create your tests here.

init_logging(stream='stdout', level='DEBUG')

class MyCalendarModelTest(TestCase):
    def setUp(self):
        # user:testuserのカレンダーを削除する
        MyCalendar.objects.filter(user='testuser').delete()
    
    def tearDown(self):
        pass
    
    '''カレンダークラスのテスト。
    '''
    def test_get_daily(self):
        '''get_daily ビュー関数のテスト。
        
        1. user：testuser のデータがすべて削除された状態で、
          user:testuser、year:2020、month:1、day:2 を指定して
          /get_dayly にアクセスする。
            * 応答ステータスが正常であること
            * 2020年1月2日のカレンダーを取得するとその月のすべての日のデータが作成されること
            * 返却されたデータのuserはget_dailyで指定されたユーザーであること
            * 返却されたデータの年はget_dailyで指定された年であること
            * 返却されたデータの月はget_dailyで指定された月であること
            * 返却されたデータの日はget_dailyで指定された日であること
            * 返却されたコメントは空であること
        2. 2020年0月1日を指定して get_daily にアクセスする
            *  ValidationErrorが発生すること
        3. 2020年13月1日を指定して get_daily にアクセスする
            * ValidationErrorが発生すること
        4. user:testuser の2020年2月のカレンダー情報が作成されている状態で、
          user:testuser、year:2020、month:1、day:0 を指定して /get_dayly に
          アクセスする。
            * ValidationError 例外が発生すること
        5. user:testuser の2020年2月のカレンダー情報が作成されている状態で、
          user:testuser、year:2020、month:1、day:32 を指定して /get_dayly に
          アクセスする。
            * ValidationError 例外が発生すること
        
        '''
        cals = MyCalendar.objects.filter(user='testuser', year=2020, month=1)
        # テスト実行前は2020年1月のデータは設定されていないこと
        self.assertEqual(len(cals), 0,
                'テスト実行前は2020年1月のデータは設定されてないこと')
        
        # 1. 2020年1月のカレンダー情報が存在しない状態で、2020年1月2日を指定
        #   して /get_daily にアクセスする
        logging.info('1. 2020年1月のカレンダー情報が存在しない状態で、2020年1月2日を指定して /get_daily にアクセスする')
        response:JsonResponse = self.client.get(reverse('mycalendar:get_daily',
                kwargs={'user':'testuser', 'year':2020, 'month':1, 'day':2}))
        response_data = json.loads(response.content)
        cals = MyCalendar.objects.filter(user='testuser', year=2020, month=1)
        last_day = calendar.monthrange(2020, 1)[1]
        ## 応答ステータスが正常であること
        self.assertEqual(response.status_code, 200, '応答ステータスが正常であること')
        ## 2020年1月2日のカレンダーを取得するとその月のすべての日のデータが作成されること
        self.assertEqual(len(cals), last_day,
                '2020年1月2日のカレンダーを取得するとその月のすべての日のデータが作成されること')
        ## 返却されたデータのuserはget_dailyで指定されたユーザーであること
        self.assertEqual(response_data['user'], 'testuser',
                '返却されたデータのuserはget_dailyで指定されたユーザーであること')
        ## 返却されたデータの年はget_dailyで指定された年であること
        self.assertEqual(response_data['year'], 2020,
                '返却されたデータの年はget_dailyで指定された年であること')
        ## 返却されたデータの月はget_dailyで指定された月であること
        self.assertEqual(response_data['month'], 1,
                '返却されたデータの月はget_dailyで指定された月であること')
        ## 返却されたデータの日はget_dailyで指定された日であること
        self.assertEqual(response_data['day'], 2,
                '返却されたデータの日はget_dailyで指定された日であること')
        ## 返却されたコメントは空であること
        self.assertEqual(response_data['note'], '',
                '返却されたコメントは空であること')
        
        # 2. 2020年0月1日を指定して get_daily にアクセスする
        logging.info('2. 2020年0月1日を指定して get_daily にアクセスする')
        ## ValidationErrorが発生すること
        with self.assertRaises(ValidationError, msg='ValidationErrorが発生すること'):
            self.client.get(reverse('mycalendar:get_daily',
                    kwargs={'user':'testuser', 'year':2020, 'month':0, 'day':0}))
        
        # 3. 2020年13月1日を指定して get_monthly にアクセスする
        logging.info('3. 2020年13月1日を指定して get_monthly にアクセスする')
        ## ValidationErrorが発生すること
        with self.assertRaises(ValidationError, msg='ValidationErrorが発生すること'):
            self.client.get(reverse('mycalendar:get_daily',
                    kwargs={'user':'testuser', 'year':2020, 'month':13, 'day':1}))
        
        # 4. 2020年1月のカレンダー情報が存在する状態で2020年1月0日を指定して
        #   /get_daily にアクセスする
        logging.info('4. 2020年1月のカレンダー情報が存在する状態で2020年1月0日を指定して /get_daily にアクセスする')
        ## ValidationError 例外が発生すること
        with self.assertRaises(ValidationError, msg='ValidationError 例外が発生すること'):
            response = self.client.get(reverse('mycalendar:get_daily',
                    kwargs={'user':'testuser', 'year':2020, 'month':1, 'day':0}))
        
        # 5. 2020年1月のカレンダー情報が存在する状態で2020年1月32日を指定して
        #   /get_daily にアクセスする
        logging.info('5. 2020年1月のカレンダー情報が存在する状態で2020年1月32日を指定して /get_daily にアクセスする' )
        ## ValidationError 例外が発生すること
        with self.assertRaises(ValidationError, msg='ValidationError 例外が発生すること'):
            response = self.client.get(reverse('mycalendar:get_daily',
                    kwargs={'user':'testuser', 'year':2020, 'month':1, 'day':32}))
    
    def test_get_monthly(self):
        '''get_monthly ビュー関数のテスト。
        
        1. 2020年1月のカレンダー情報が登録されていない状態で2020年2年を
          指定して get_monthly にアクセスする
            * 取得したデータ数は月の日数と等しいこと
            * 取得した各レコードのユーザーは引数で指定されたユーザーであること
            * 取得した各レコードの年は引数で指定された月であること
            * 取得した各レコードの月は引数で指定された月であること
            * 取得した各レコードのコメントは空であること
        2. 2020年0月を指定して get_monthly にアクセスする
            * ValidationErrorが発生すること
        3. 2020年13月を指定して get_monthly にアクセスする
            * ValidationErrorが発生すること
        
        '''
        cals = MyCalendar.objects.filter(user='testuser', year=2020, month=2)
        # テスト実行前は2020年1月のカレンダー情報は登録されていないこと
        self.assertEqual(len(cals), 0,
                'テスト実行前は2020年1月のデータは設定されてないこと')
        
        # 1. 2020年1月のカレンダー情報が登録されていない状態で2020年2年を
        #   指定して get_monthly にアクセスする
        logging.info('1. 2020年1月のカレンダー情報が登録されていない状態で2020年2年を指定して get_monthly にアクセスする')
        response:JsonResponse = self.client.get(reverse('mycalendar:get_monthly',
                kwargs={'user':'testuser', 'year':2020, 'month':2}))
        response_data = json.loads(response.content)
        
        ## 取得したデータ数は月の日数と等しいこと
        last_day = calendar.monthrange(2020, 2)[1]
        self.assertEqual(len(response_data), last_day,
                '取得したデータ数は月の日数と等しいこと')
        for cal in response_data:
            ## ユーザーは引数で指定されたユーザーであること
            self.assertEqual(cal.get('user'), 'testuser',
                    'ユーザーは引数で指定されたユーザーであること')
            ## 年は引数で指定された月であること
            self.assertEqual(cal.get('year'), 2020,
                    '年は引数で指定された月であること')
            ## 月は引数で指定された月であること
            self.assertEqual(cal.get('month'), 2,
                    '月は引数で指定された月であること')
            ## コメントは空であること
            self.assertEqual(cal.get('note'), '', 'コメントは空であること')
        
        # 2. 2020年0月を指定して get_monthly にアクセスする
        logging.info('2. 2020年0月を指定して get_monthly にアクセスする')
        ## ValidationErrorが発生すること
        with self.assertRaises(ValidationError, msg='ValidationErrorが発生すること'):
            self.client.get(reverse('mycalendar:get_monthly',
                    kwargs={'user':'testuser', 'year':2020, 'month':0}))
        
        # 3. 2020年13月を指定して get_monthly にアクセスする
        logging.info('3. 2020年13月を指定して get_monthly にアクセスする')
        ## ValidationErrorが発生すること
        with self.assertRaises(ValidationError, msg='ValidationErrorが発生すること'):
            self.client.get(reverse('mycalendar:get_monthly',
                    kwargs={'user':'testuser', 'year':2020, 'month':13}))
    
    def test_save_daily(self):
        '''save_daily関数のテスト
        
        1. ユーザー：testuserの2020年2月1日のカレンダー情報を登録する
            * 応答ステータスが正常であること
            * 2020年2月のデータがデータベースに登録されていること
            * 2020年2月1日のコメントがリクエスト・ボディに指定したものと一致すること
            * URLパラメータに指定された年月日以外のデータのコメントは空白であること
        2. get_daily Web APIで2020年2月1日のカレンダー情報を取得し、コメントを
          変更して save_daily にアクセスする
            * 応答ステータスが正常であること
            * データベースに変更したコメントが反映されること
        3. ユーザー：testuserの2020年2月29日のコメントを修正する
          get_daily Web APIで2020年2月29日の関連だー情報を取得し、コメントを
          変更して save_daily にアクセスする
            * 応答ステータスが正常であること
            * データベースに変更したコメントが反映されること
        4. 2020年2月のカレンダー情報が存在する状態で2020年2月0日を指定して
          /save_daily にアクセスする
            * ValidationError 例外が発生すること
        5. 2020年2月のカレンダー情報が存在する状態で2020年2月30日を指定して
          /save_daily にアクセスする
            * ValidationError 例外が発生すること
        
        '''
        # テスト実行前は2020年1月のカレンダー情報は登録されていないこと
        cals = MyCalendar.objects.filter(user='testuser', year=2020, month=2)
        self.assertEqual(len(cals), 0,
                'テスト実行前は2020年1月のカレンダー情報は登録されていないこと')
        
        # 1. ユーザー：testuserの2020年2月1日のカレンダー情報を登録する
        logging.info('1. ユーザー：testuserの2020年2月1日のカレンダー情報を登録する')
        request_data = {'user':'testuser', 'year':2020, 'month':2, 'day':1,
                        'note':'Registed 2020-02-01 data.'}
        response:HttpResponse = self.client.put(reverse('mycalendar:save_daily',
                kwargs={'user':'testuser', 'year':2020, 'month':2, 'day':1}),
                data=json.dumps(request_data),
                content_type='application/json')
        ## 応答ステータスが正常であること
        self.assertEqual(response.status_code, 200, '応答ステータスが正常であること')
        ## 2020年2月のデータがデータベースに登録されていること
        last_day = calendar.monthrange(2020, 2)[1]
        cals = MyCalendar.objects.filter(user='testuser', year=2020, month=2).order_by('day')
        self.assertEqual(len(cals), last_day, '2020年2月のデータがデータベースに登録されていること')
        ## 2020年2月1日のコメントがリクエスト・ボディに指定したものと一致すること
        self.assertEqual(cals[0].note, 'Registed 2020-02-01 data.',
                '2020年2月1日のコメントがリクエスト・ボディに指定したものと一致すること')
        ## URLパラメータに指定された年月日以外のデータのコメントは空白であること
        for day in range(1, len(cals)):
            if day != 1:
                self.assertEqual(cals[day-1].note, '',
                        'URLパラメータに指定された年月日以外のデータのコメントは空白であること')
        
        # 2. get_daily Web APIで2020年2月1日のカレンダー情報を取得し、コメントを
        #   変更して save_daily にアクセスする
        logging.info('2. ユーザー：get_daily Web APIで2020年2月1日のカレンダー情報を取得し、コメントを変更して save_daily にアクセスする')
        response:JsonResponse = self.client.get(reverse('mycalendar:get_daily',
                kwargs={'user':'testuser', 'year':2020, 'month':2, 'day':1}))
        json_data = json.loads(response.content)
        json_data['note'] = 'Updated 2020-02-01 data.'
        response:HttpResponse = self.client.put(reverse('mycalendar:save_daily',
                kwargs={'user':'testuser', 'year':2020, 'month':2, 'day':1}),
                data=json.dumps(json_data), content_type='application/json')
        ## 応答ステータスが正常であること
        self.assertEqual(response.status_code, 200, '応答ステータスが正常であること')
        ## データベースに変更したコメントが反映されること
        cal = MyCalendar.objects.get(user='testuser', year=2020, month=2, day=1)
        self.assertEqual(cal.note, 'Updated 2020-02-01 data.',
                'データベースに変更したコメントが反映されること')
        
        # 3. ユーザー：testuserの2020年2月29日のコメントを修正する
        #   get_daily Web APIで2020年2月29日のカレンダー情報を取得し、コメントを
        #   変更して save_daily にアクセスする
        logging.info('3. ユーザー：testuserの2020年2月29日のコメントを修正する。get_daily Web APIで2020年2月29日のカレンダー情報を取得し、コメントを変更して save_daily にアクセスする')
        response:JsonResponse = self.client.get(reverse('mycalendar:get_daily',
                kwargs={'user':'testuser', 'year':2020, 'month':2, 'day':29}))
        json_data = json.loads(response.content)
        json_data['note'] = 'Updated 2020-02-29 data.'
        response:HttpResponse = self.client.put(reverse('mycalendar:save_daily',
                kwargs={'user':'testuser', 'year':2020, 'month':2, 'day':29}),
                data=json.dumps(json_data), content_type='application/json')
        ## 応答ステータスが正常であること
        self.assertEqual(response.status_code, 200, '応答ステータスが正常であること')
        ## データベースに変更したコメントが反映されること
        cal = MyCalendar.objects.get(user='testuser', year=2020, month=2, day=29)
        self.assertEqual(cal.note, 'Updated 2020-02-29 data.',
                'データベースに変更したコメントが反映されること')
        
        # 4. 2020年2月のカレンダー情報が存在する状態で2020年2月0日を指定して
        #   /save_daily にアクセスする。
        ## ValidationError 例外が発生すること
        logging.info('4. 2020年2月のカレンダー情報が存在する状態で2020年2月0日を指定して /save_daily にアクセスする。')
        with self.assertRaises(ValidationError, msg='ValidationError 例外が発生すること'):
            response = self.client.put(reverse('mycalendar:save_daily',
                    kwargs={'user':'testuser', 'year':2020, 'month':2, 'day':0}),
                    data=json.dumps({'user':'testuser','year':2020, 'month':2, 'day':0}),
                    content_type='application/json')
        
        # 5. 2020年2月のカレンダー情報が存在する状態で2020年2月30日を指定して
        #   /save_daily にアクセスする
        logging.info('5. 2020年2月のカレンダー情報が存在する状態で2020年2月30日を指定して /save_daily にアクセスする')
        ## ValidationError 例外が発生すること
        with self.assertRaises(ValidationError, msg='ValidationError 例外が発生すること'):
            response = self.client.put(reverse('mycalendar:save_daily',
                    kwargs={'user':'testuser', 'year':2020, 'month':2, 'day':30}),
                    data=json.dumps({'user':'testuser','year':2020, 'month':2, 'day':30}),
                    content_type='application/json')
        
        # 6. URLパラメータにuser:testuser、リクエスト・ボディのJSONに
        #   user:'test'を指定して save_daily にアクセスする
        logging.info('6. URLパラメータにuser:testuser、リクエスト・ボディのJSONに user:\'test\'を指定して save_daily にアクセスする')
        ## ValidationError 例外が発生すること
        with self.assertRaises(ValidationError, msg='ValidationError 例外が発生すること'):
            response = self.client.put(reverse('mycalendar:save_daily',
                    kwargs={'user':'testuser', 'year':2020, 'month':2, 'day':1}),
                    data=json.dumps({'user':'test', 'year':2020, 'month':2, 'day':1,
                            'note':'Validation Error 2020-02-01'}),
                    content_type='application/json')
    
    def test_save_monthly(self):
        '''save_monthly ビュー関数のテスト
        
        1. ユーザー：testuserの2020年2月1日、29日のカレンダー情報を登録する
            * 応答ステータスが正常であること
            * 2020年2月のデータがデータベースに登録されていること
            * 2020年2月1日、29日のコメントがリクエスト・ボディに指定したものと一致すること
            * 2020年2月1日、29日以外のデータのコメントは空白であること
        2. get_monthly Web APIで2020年2月のカレンダー情報を取得し、1日、29日の
          コメントを変更して save_monthly にアクセスする
            * 応答ステータスが正常であること
            * データベースに変更したコメントが反映されること
        3. 2020年2月のカレンダー情報が存在する状態で2020年2月1日のコメントを
          修正し、2020年2月0日を指定したカレンダー情報を最後に設定した
          レスポンス・データを設定して /save_daily にアクセスする
            * ValidationError 例外が発生すること
            * レスポンスデータに設定した2月1日のコメントはDBに登録されていない
              こと
        4. 2020年2月のカレンダー情報が存在する状態で2020年2月1日のコメントを
          修正し、2020年2月30日を指定したカレンダー情報を最後に設定した
          レスポンス・データを設定して /save_daily にアクセスする
            * ValidationError 例外が発生すること
            * レスポンスデータに設定した2月1日のコメントはDBに登録されていない
              こと
        5. 2020年2月のカレンダー情報が存在する状態で2020年2月29日のユーザーを
          'test'に修正し、/save_daily にアクセスする
            * ValidationError 例外が発生すること
        
        '''
        # テスト実行前は2020年1月のカレンダー情報は登録されていないこと
        cals = MyCalendar.objects.filter(user='testuser', year=2020, month=2)
        self.assertEqual(len(cals), 0, 'テスト実行前は2020年1月のカレンダー情報は登録されていないこと')
        
        # 1. ユーザー：testuserの2020年2月1日、29日のカレンダー情報を登録する
        logging.info('1. ユーザー：testuserの2020年2月1日、29日のカレンダー情報を登録する')
        request_data = [
            {'user':'testuser', 'year':2020, 'month':2, 'day':1, 'note':'Registed 2020-02-01 data.'},
            {'user':'testuser', 'year':2020, 'month':2, 'day':29, 'note':'Registed 2020-02-29 data.'}
        ]
        response:HttpResponse = self.client.put(reverse('mycalendar:save_monthly',
                kwargs={'user':'testuser', 'year':2020, 'month':2}),
                data=json.dumps(request_data),
                content_type='application/json')
        ## 応答ステータスが正常であること
        self.assertEqual(response.status_code, 200, '応答ステータスが正常であること')
        ## 2020年2月のデータがデータベースに登録されていること
        cals = MyCalendar.objects.filter(user='testuser', year=2020, month=2).order_by('day')
        last_day = calendar.monthrange(2020, 2)[1]
        self.assertEqual(len(cals), last_day, '2020年2月のデータがデータベースに登録されていること')
        ## 2020年2月1日、29日のコメントがリクエスト・ボディに指定したものと一致すること
        self.assertEqual(cals[0].note, 'Registed 2020-02-01 data.',
                '2020年2月1日のコメントがリクエスト・ボディに指定したものと一致すること')
        self.assertEqual(cals[28].note, 'Registed 2020-02-29 data.',
                '2020年2月29日のコメントがリクエスト・ボディに指定したものと一致すること')
        ## 2020年2月1日、29日以外のデータのコメントは空白であること
        for day in range(1, last_day):
            if day != 1 and day != 29:
                self.assertEqual(cals[day-1].note, '',
                        '2020年2月1日、29日以外のデータのコメントは空白であること')
        
        # 2. get_monthly Web APIで2020年2月のカレンダー情報を取得し、1日、29日の
        #   コメントを変更して save_daily にアクセスする
        logging.info('2. get_monthly Web APIで2020年2月のカレンダー情報を取得し、1日、29日のコメントを変更して save_daily にアクセスする')
        response:JsonResponse = self.client.get(reverse('mycalendar:get_monthly',
                kwargs={'user':'testuser','year':2020, 'month':2}))
        json_data = json.loads(response.content)
        for data in json_data:
            if data['day'] == 1:
                data['note'] = 'Updated 2020-02-01 data.'
            elif data['day'] == 29:
                data['note'] = 'Updated 2020-02-29 data.'
        response:HttpResponse = self.client.put(reverse('mycalendar:save_monthly',
                kwargs={'user':'testuser', 'year':2020, 'month':2}),
                data=json.dumps(json_data),
                content_type='application/json')
        ## 応答ステータスが正常であること
        self.assertEqual(response.status_code, 200, '応答ステータスが正常であること')
        ## データベースに変更したコメントが反映されること
        cal = MyCalendar.objects.get(user='testuser', year=2020, month=2, day=1)
        self.assertEqual(cal.note, 'Updated 2020-02-01 data.',
                'データベースに変更したコメントが反映されること')
        cal = MyCalendar.objects.get(user='testuser', year=2020, month=2, day=29)
        self.assertEqual(cal.note, 'Updated 2020-02-29 data.',
                'データベースに変更したコメントが反映されること')
        
        # 3. 2020年2月のカレンダー情報が存在する状態で2020年2月1日のコメントを
        #  修正し、2020年2月0日を指定したカレンダー情報を最後に設定した
        #  レスポンス・データを設定して /save_daily にアクセスする
        logging.info('3. 2020年2月のカレンダー情報が存在する状態で2020年2月1日のコメントを修正し、2020年2月0日を指定したカレンダー情報を最後に設定したレスポンス・データを設定して /save_daily にアクセスする')
        response:JsonResponse = self.client.get(reverse('mycalendar:get_monthly',
                kwargs={'user':'testuser', 'year':2020, 'month':2}))
        json_data = json.loads(response.content)
        self.assertEqual(json_data[0]['day'], 1, '月の最初のデータの日付は1であること')
        json_data[0]['note'] = 'XXXXXXXX'
        json_data.append({'user':'testuser', 'year':2020, 'month':2, 'day':0,
                'note':'Registed 2020-02-00 data.'})
        ## ValidationError 例外が発生すること
        with self.assertRaises(ValidationError, msg='ValidationError 例外が発生すること'):
            response:HttpResponse = self.client.put(reverse('mycalendar:save_monthly',
                    kwargs={'user':'testuser', 'year':2020, 'month':2}),
                    data=json.dumps(json_data),
                    content_type='application/json')
        ## レスポンスデータに設定した2月1日のコメントはDBに登録されていないこと
        response:JsonResponse = self.client.get(reverse('mycalendar:get_daily',
                kwargs={'user':'testuser', 'year':2020, 'month':2, 'day':1}))
        json_data = json.loads(response.content)
        self.assertNotEqual(json_data['note'], 'XXXXXXXX',
                'レスポンスデータに設定した2月1日のコメントはDBに登録されていないこと')
        
        # 4. 2020年2月のカレンダー情報が存在する状態で2020年2月1日のコメントを
        #   修正し、2020年2月30日を指定したカレンダー情報を最後に設定した
        #   レスポンス・データを設定して /save_daily にアクセスする
        logging.info('4. 2020年2月のカレンダー情報が存在する状態で2020年2月1日のコメントを修正し、2020年2月30日を指定したカレンダー情報を最後に設定したレスポンス・データを設定して /save_daily にアクセスする')
        response:JsonResponse = self.client.get(reverse('mycalendar:get_monthly',
                kwargs={'user':'testuser', 'year':2020, 'month':2}))
        json_data = json.loads(response.content)
        self.assertEqual(json_data[0]['day'], 1, '月の最初のデータの日付は1であること')
        json_data[0]['note'] = 'XXXXXXXX'
        json_data.append({'user':'testuser', 'year':2020, 'month':2, 'day':30,
                'note':'Registed 2020-02-30 data.'})
        ## ValidationError 例外が発生すること
        with self.assertRaises(ValidationError, msg='ValidationError 例外が発生すること'):
            response:HttpResponse = self.client.put(reverse('mycalendar:save_monthly',
                    kwargs={'user':'testuser', 'year':2020, 'month':2}),
                    data=json.dumps(json_data),
                    content_type='application/json')
        ## レスポンスデータに設定した2月1日のコメントはDBに登録されていないこと
        response:JsonResponse = self.client.get(reverse('mycalendar:get_daily',
                kwargs={'user':'testuser', 'year':2020, 'month':2, 'day':1}))
        json_data = json.loads(response.content)
        self.assertNotEqual(json_data['note'], 'XXXXXXXX',
                'レスポンスデータに設定した2月1日のコメントはDBに登録されていないこと')

        # 5. 2020年2月のカレンダー情報が存在する状態で2020年2月29日のユーザーを
        #   'test'に修正し、/save_daily にアクセスする
        logging.info('5. 2020年2月のカレンダー情報が存在する状態で2020年2月1日のユーザーを\'test\'に修正し、/save_daily にアクセスする')
        response:JsonResponse = self.client.get(reverse('mycalendar:get_monthly',
                kwargs={'user':'testuser', 'year':2020, 'month':2}))
        json_data = json.loads(response.content)
        self.assertEqual(json_data[28]['day'], 29, '月の29番目のデータの日付は29であること')
        json_data[28]['user'] = 'test'
        ## ValidationError 例外が発生すること
        with self.assertRaises(ValidationError, msg='ValidationError 例外が発生すること'):
            response:JsonResponse = self.client.put(reverse('mycalendar:save_monthly',
                    kwargs={'user':'testuser', 'year':2020, 'month':2}),
                    data=json.dumps(json_data),
                    content_type='application/json')
    
    def test_delete_monthly(self):
        '''delete_monthly ビュー関数のテスト。
        
        1. get_monthly/testuser/2020/1および2/ にアクセスして2020年1月と2月の
          カレンダー情報を取得してDBに2020年1月と2月のカレンダー情報を作成した
          後、delete_monthly/testuser/2020/2/ にアクセスする
            * 2020年2月のカレンダー情報が削除される（件数が0件であ）ること
            * 2020年1月のカレンダー情報は削除されない（件数が月の日数）であること
        2. delete_monthly/testuser/2020/0/ にアクセスする
            * ValidationErrorが発生すること
        3. delete_monthly/testuser/2020/13/ にアクセスする
            * ValidationErrorが発生すること
        
        '''
        # 1. get_monthly/testuser/2020/1および2/ にアクセスして2020年1月と2月の
        #   カレンダー情報を取得してDBに2020年1月と2月のカレンダー情報を作成した
        #   後、delete_monthly/testuser/2020/2/ にアクセスする
        logging.info('1. get_monthly/testuser/2020/1および2/ にアクセスして2020年1月と2月のカレンダー情報を取得してDBに2020年1月と2月のカレンダー情報を作成した後、delete_monthly/testuser/2020/2/ にアクセスする')
        response:JsonResponse = self.client.get(reverse('mycalendar:get_monthly',
                kwargs={'user':'testuser', 'year':2020, 'month':1}))
        json_data = json.loads(response.content)
        last_day = calendar.monthrange(2020, 1)[1]
        self.assertEqual(len(json_data), last_day, '2020年1月のカレンダー情報が作成されること')
        
        response:JsonResponse = self.client.get(reverse('mycalendar:get_monthly',
                kwargs={'user':'testuser', 'year':2020, 'month':2}))
        json_data = json.loads(response.content)
        last_day = calendar.monthrange(2020, 2)[1]
        self.assertEqual(len(json_data), last_day, '2020年2月のカレンダー情報が作成されること')
        
        response.HttpResponse = self.client.delete(reverse('mycalendar:delete_monthly',
                kwargs={'user':'testuser', 'year':2020, 'month':2}))
        ## 2020年2月のカレンダー情報が削除される（件数が0件である）こと
        cals = MyCalendar.objects.filter(user='testuser', year=2020, month=2)
        self.assertEqual(len(cals), 0,
                '2020年2月のカレンダー情報が削除される（件数が0件である）こと')
        ## 2020年1月のカレンダー情報は削除されない（件数が月の日数）であること
        cals = MyCalendar.objects.filter(user='testuser', year=2020, month=1)
        last_day = calendar.monthrange(2020, 1)[1]
        self.assertEqual(len(cals), last_day,
                '2020年2月のカレンダー情報が削除される（件数が0件である）こと')
        
        # 2. delete_monthly/testuser/2020/0/ にアクセスする
        logging.info('2. delete_monthly/testuser/2020/0/ にアクセスする')
        #   ValidationErrorが発生すること
        with self.assertRaises(ValidationError, msg='ValidationErrorが発生すること'):
            self.client.delete(reverse('mycalendar:delete_monthly',
                    kwargs={'user':'testuser', 'year':2020, 'month':0}))
        
        # 3. delete_monthly/testuser/2020/13/ にアクセスする
        ## ValidationErrorが発生すること
        logging.info('3. delete_monthly/testuser/2020/13/ にアクセスする')
        #   ValidationErrorが発生すること
        with self.assertRaises(ValidationError, msg='ValidationErrorが発生すること'):
            self.client.delete(reverse('mycalendar:delete_monthly',
                    kwargs={'user':'testuser', 'year':2020, 'month':13}))

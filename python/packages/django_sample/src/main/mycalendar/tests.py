from .models import MyCalendar
from .utils import init_logging

from django.test import TestCase
from django.urls import reverse
import calendar
import json
import logging
import sys

# Create your tests here.

init_logging(stream=sys.stdout, level=logging.DEBUG)

class MyCalendarModelTest(TestCase):
    def setUp(self):
        # user:testuserのカレンダーを削除する
        MyCalendar.objects.filter(user='testuser').delete()
    
    def tearDown(self):
        pass
    
    '''カレンダークラスのテスト。
    '''
    def test_get_daily(self):
        '''get_daily view関数のテスト。
        
        1. user：testuser のデータがすべて削除された状態で、
          user:testuser、year:2020、month:1、day:2 を指定して
          /get_dayly にアクセスする
        
            * 2020年1月2日のカレンダーを取得するとその月のすべての日のデータが作成されること
            * 返却されたデータのuserはget_dailyで指定されたユーザーであること
            * 返却されたデータの年はget_dailyで指定された年であること
            * 返却されたデータの月はget_dailyで指定された月であること
            * 返却されたデータの日はget_dailyで指定された日であること
            * 返却されたコメントは空であること
          
        '''
        cals = MyCalendar.objects.filter(user='testuser', year=2020, month=1)
        # テスト実行前は2020年1月のデータは設定されていないこと
        self.assertEqual(len(cals), 0,
                'テスト実行前は2020年1月のデータは設定されてないこと')
        
        response = self.client.get(reverse('mycalendar:get_daily',
                kwargs={'user':'testuser', 'year':2020, 'month':1, 'day':2}))
        response_data = json.loads(response.content)
        cals = MyCalendar.objects.filter(user='testuser', year=2020, month=1)
        max_days = calendar.monthrange(2020, 1)[1]
        # 2020年1月2日のカレンダーを取得するとその月のすべての日のデータが作成されること
        self.assertEqual(len(cals), max_days,
                '2020年1月2日のカレンダーを取得するとその月のすべての日のデータが作成されること')
        # 返却されたデータのuserはget_dailyで指定されたユーザーであること
        self.assertEqual(response_data['user'], 'testuser',
                '返却されたデータのuserはget_dailyで指定されたユーザーであること')
        # 返却されたデータの年はget_dailyで指定された年であること
        self.assertEqual(response_data['year'], 2020,
                '返却されたデータの年はget_dailyで指定された年であること')
        # 返却されたデータの月はget_dailyで指定された月であること
        self.assertEqual(response_data['month'], 1,
                '返却されたデータの月はget_dailyで指定された月であること')
        # 返却されたデータの日はget_dailyで指定された日であること
        self.assertEqual(response_data['day'], 2,
                '返却されたデータの日はget_dailyで指定された日であること')
        # 返却されたコメントは空であること
        self.assertEqual(response_data['note'], '',
                '返却されたコメントは空であること')

from django.db import models
from django.utils import timezone

_date_format = '%Y/%m/%d'

class MyCalender(models.Model):
    '''カレンダークラス
    '''
    user = models.CharField(max_length=128)
    date = models.DateField()
    note = models.TextField(max_length=512)
    unique_together = (('user', 'date'),)

    def __str__(self):
        '''レコードの文字列表現を返す。
        '''
        return f'[{self.user}]{self.date}'
    
    def deserialize(self, json_data:dict):
        '''ディクショナリ形式のJSONデータをMyCalenderモデルのインスタンスに変換する。
        Args:
            json_data (dict): ディクショナリ形式のJSONデータを指定する。
        Returns:
            MyCalender: MyCalenderのインスタンスを返却する。
        '''
        mycalender = MyCalender(
            user = json_data.get('user'),
            date = timezone.date.strptime(json_data.get('date'), _date_format) if json_data.get('date') else None,
            note = json_data.get('note')
        )
        return mycalender

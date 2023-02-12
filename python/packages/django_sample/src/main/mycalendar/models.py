from django.db import models
from django.db.models import UniqueConstraint

class MyCalendar(models.Model):
    '''カレンダークラス
    
    Attributes:
        id (int): ID
        user (str): ユーザー名
        year (int): カレンダーの年
        month (int): カレンダーの月
        day (int): カレンダーの日
        note (str): コメント
    
    '''
    id = models.IntegerField(primary_key=True)
    user = models.CharField(max_length=128)
    year = models.IntegerField()
    month = models.IntegerField()
    day = models.IntegerField()
    note = models.TextField(max_length=512)
    unique_together = (('user', 'year', 'month', 'day'),)

    class Meta:
        db_table = 'my_calendar'
        UniqueConstraint(
            name = 'unique_mycalender',
            fields=['user', 'year', 'month', 'day']
        )
        
    
    @classmethod
    def deserialize(cls, json_data: dict):
        '''ディクショナリ形式のJSONデータをMyCalendarモデルのインスタンスに変換する。
        
        Args:
            json_data (dict): ディクショナリ形式のJSONデータを指定する。
        Returns:
            MyCalendar: MyCalendarのインスタンスを返却する。
        
        '''
        mycalendar = MyCalendar(
            id = json_data.get("id"),
            user = json_data.get('user'),
            year = int(json_data.get('year')),
            month = int(json_data.get('month')),
            day = int(json_data.get('day')),
            note = json_data.get('note')
        )
        return mycalendar

    def __str__(self):
        '''レコードの文字列表現を返す。
        '''
        return f'[{self.user}]{self.year}-{self.month}-{self.day}'

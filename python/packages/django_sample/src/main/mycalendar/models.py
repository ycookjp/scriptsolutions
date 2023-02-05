from django.db import models

class MyCalendar(models.Model):
    '''カレンダークラス
    
    Attributes:
        user (str): ユーザー名
        year (int): カレンダーの年
        month (int): カレンダーの月
        day (int): カレンダーの日
        note (str): コメント
    
    '''
    user = models.CharField(max_length=128)
    year = models.IntegerField()
    month = models.IntegerField()
    day = models.IntegerField()
    note = models.TextField(max_length=512)
    unique_together = (('user', 'year', 'month', 'day'),)

    class Meta:
        db_table = 'my_calendar'

    def __str__(self):
        '''レコードの文字列表現を返す。
        '''
        return f'[{self.user}]{self.year}-{self.month}-{self.day}'
    
    def deserialize(self, json_data: dict):
        '''ディクショナリ形式のJSONデータをMyCalendarモデルのインスタンスに変換する。
        
        Args:
            json_data (dict): ディクショナリ形式のJSONデータを指定する。
        Returns:
            MyCalendar: MyCalendarのインスタンスを返却する。
        
        '''
        mycalendar = MyCalendar(
            user = json_data.get('user'),
            year = int(json_data.get('year')),
            month = int(json_data.get('month')),
            day = int(json_data.get('day')),
            note = json_data.get('note')
        )
        return mycalendar

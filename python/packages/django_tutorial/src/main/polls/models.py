# -*- config: utf8 -*-
import datetime
from django.db import models
from django.utils import timezone

# Create your models here.

class Question(models.Model):
    '''質問クラス。
    '''
    question_text: str = models.CharField(max_length=200)
    '''質問内容'''
    pub_date = models.DateTimeField('date published')
    '''質問の公開日'''

    def __str__(self):
        '''質問インスタンスの文字列表現。
        '''
        return self.question_text

    def was_published_recently(self):
        '''質問の公開日が過去１日以内かを判定する。
        
        Returns:
            boolean: 質問の公開日が過去１日いないの場合はTrue、そうでない
            場合はFalseを返す。
        
        '''
        now = timezone.now()
        return timezone.now() - datetime.timedelta(days=1) <= self.pub_date <= now

class Choice(models.Model):
    '''回答の選択肢のクラス。
    '''
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    '''選択肢に関連する質問。'''
    choice_text: str = models.CharField(max_length=200)
    '''str: 選択肢の文言。'''
    votes = models.IntegerField(default=0)
    '''int: 選択肢に対する投票数。'''

    def __str__(self):
        '''選択肢インスタンスの文字列表現。
        '''
        return self.choice_text

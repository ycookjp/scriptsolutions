from polls.models import Question
from django.utils import timezone

q = Question(question_text="What's new?", pub_date=timezone.now())
q.save()

q.choice_set.all()
q.choice_set.create(choice_text='Not much', votes=0)
q.choice_set.create(choice_text='The sky', votes=0)
q.choice_set.create(choice_text='Just hacking again', votes=0)

'''Admin site module.

Copyright ycookjp

https://github.com/ycookjp/

'''
from django.contrib import admin
from .models import MyCalendar

# Register your models here.
admin.site.register(MyCalendar)

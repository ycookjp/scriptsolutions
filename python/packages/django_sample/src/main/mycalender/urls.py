from django.urls import path
from . import views

app_name = 'mycalender'
urlpatterns = [
    path('<str:user>/<str:date>/get_daily/', views.get_daily, name='get_daily'),
    path('<str:user>/<str:month>/get_monthly', views.get_monthly, name='get_monthly'),
    path('<str:user>/<str:date>/save_daily', views.save_daily, name='save_daily'),
    path('<str:user>/<str:month>/save_monthly', views.save_monthly, ame='save_monthly'),
]

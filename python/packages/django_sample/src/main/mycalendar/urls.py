from django.urls import path
from . import views

app_name = 'mycalendar'
urlpatterns = [
    path('get_daily/<str:user>/<int:year>/<int:month>/<int:day>/', views.get_daily, name='get_daily'),
    path('get_monthly/<str:user>/<int:year>/<int:month>/', views.get_monthly, name='get_monthly'),
    path('save_daily/<str:user>/<int:year>/<int:month>/<int:day>/', views.save_daily, name='save_daily'),
    path('save_monthly/<str:user>/<int:year>/<int:month>/', views.save_monthly, name='save_monthly'),
    path('delete_monthly/<str:user>/<int:year>/<int:month>/', views.delete_monthly, name='delete_monthly'),
]

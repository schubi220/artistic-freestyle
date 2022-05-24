from django.urls import path

from . import views

app_name = 'artistic'
urlpatterns = [
    path('code', views.code, name='code'),
    path('input', views.input, name='input'),
]

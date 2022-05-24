from django.urls import path, re_path

from . import views

app_name = 'artistic'
urlpatterns = [
    path('code', views.code, name='code'),
    path('input', views.input, name='input'),
    path('free', views.free, name='free'),
    path('inputpdf', views.inputpdf, name='inputpdf'),
    path('rate', views.rate, name='rate'),
    re_path('rate/pdf/(?P<filename>(detail|result|certificate))', views.wrappdf, name='ratepdf'),
    path('display/settings', views.displaySettings, name='displaySettings'),
    path('display/beamer', views.displayBeamer, name='displayBeamer'),
    path('display/monitor', views.displayMonitor, name='displayMonitor'),
    path('display/mode', views.displayMode, name='displayMode'),
    path('display/pull', views.displayPushPull, name='displayPushPull'),
]

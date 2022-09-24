from django.urls import path, re_path

from . import views

app_name = 'artistic'
urlpatterns = [
    path('code', views.code, name='code'),
    path('input', views.input, name='input'),
    path('free', views.free, name='free'),
    path('inputpdf', views.inputpdf, name='inputpdf'),
    path('select', views.select, name='select'),
    path('rate', views.rate, name='rate'),
    re_path('rate/pdf/(?P<filename>(notice|result|certificate)).pdf', views.wrappdf, name='ratepdf'),
    path('import', views.read_csv, name='import'),
    path('choose_event', views.choose_event, name='choose_event'),
    path('display/settings', views.displaySettings, name='displaySettings'),
    path('display/beamer', views.displayBeamer, name='displayBeamer'),
    path('display/monitor', views.displayMonitor, name='displayMonitor'),
    path('display/mode', views.displayMode, name='displayMode'),
    path('display/pull', views.displayPushPull, name='displayPushPull'),
]

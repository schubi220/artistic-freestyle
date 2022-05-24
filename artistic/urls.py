from django.urls import path, re_path

from . import views

app_name = 'artistic'
urlpatterns = [
    path('code', views.code, name='code'),
    path('input', views.input, name='input'),
    path('free', views.free, name='free'),
    path('rate', views.rate, name='rate'),
    re_path('pdf/(?P<filename>(pdfdetail|pdfresult|pdfcertificate|pdfinput))', views.wrappdf, name='pdf'),
]

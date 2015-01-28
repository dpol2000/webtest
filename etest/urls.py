from django import VERSION as django_version

if django_version[1] < 4:
    from django.conf.urls.defaults import *
else:
    from django.conf.urls import patterns, include, url

from etest import views

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view()),
    url(r'^(?P<pk>\d+)', views.StudentDetailView.as_view()),
    url(r'^results/$', views.TestLogList.as_view()),
    url(r'^results/(?P<pk>\d+)', views.TestLogDetailView.as_view()),
    url(r'^tests/(?P<pk>\d+)', views.TestDetailView.as_view()),

)

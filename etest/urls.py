from django.conf.urls import patterns, url
from etest import views

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view()),
    url(r'^stats/students/(?P<pk>\d+)', views.StudentStatsView.as_view()),
    url(r'^(?P<pk>\d+)', views.StudentDetailView.as_view()),
    url(r'^results/$', views.TestLogList.as_view()),
    url(r'^results/(?P<pk>\d+)', views.TestLogDetailView.as_view()),
    url(r'^tests/(?P<pk>\d+)', views.TestDetailView.as_view()),
)

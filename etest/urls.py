from django.conf.urls import url
from etest import views, transform, vk

urlpatterns = [
    url(r'^$', views.IndexView.as_view()),
    url(r'^stats/students/(?P<pk>\d+)', views.StudentStatsView.as_view()),
    url(r'^students/(?P<pk>\d+)', views.StudentDetailView.as_view(), name='student'),
    url(r'^students/results/$', views.TestLogList.as_view()),
    url(r'^students/results/(?P<pk>\d+)', views.TestLogDetailView.as_view(), name='testlog'),
    url(r'^students/tests/(?P<pk>\d+)', views.TestDetailView.as_view(), name='test'),
    url(r'^login-test-student$', views.lts),
    url(r'^logout$', views.logout),
    url(r'^checktest_ajax$', views.check_ajax),
    url(r'^uploadcourse$', transform.upload_xml_course),
    url(r'^uploadtest$', transform.upload_xml_test),
    url(r'^get_xml$', transform.get_xml),
    url(r'^vk.*$', vk.authorize),
    url(r'^getstudentdata$', views.get_student_data),
]
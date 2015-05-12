from django import VERSION as django_version

if django_version[1] < 4:
    from django.conf.urls.defaults import patterns, include, url
else:
    from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('etest.urls')),
    url(r'^login-test-student$', 'etest.views.lts'),
    url(r'^logout$', 'etest.views.logout'),
    url(r'^checktest$', 'etest.views.check'),
    url(r'^checktest_ajax$', 'etest.views.check_ajax'),
    url(r'^students/', include('etest.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^uploadcourse$', 'etest.transform.uploadxmlcourse'),
    url(r'^uploadtest$', 'etest.transform.uploadxmltest'),
    url(r'^get_xml$', 'etest.transform.get_xml'),
    url(r'^vk.*$', 'etest.vk.authorize'),
    url(r'^getstudentdata$', 'etest.views.getstudentdata'),
)

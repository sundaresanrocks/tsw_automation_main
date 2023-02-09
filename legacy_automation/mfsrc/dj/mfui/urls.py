from django.conf.urls import patterns, include, url
from django.contrib import admin

from dj.repdec.views import RepperDecoder1

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'dj.mfui.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    # url(r'^api/repdec/resp', include(RepperDecodeResource.urls())),
    # url(r'^api/repdec/req', RepperDecodeResource.as_request(), name='api_repdec_req'),
    url(r'^repdec/', RepperDecoder1.as_view()),
)

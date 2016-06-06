
import web.zoo.urls
import web.zooapi.urls
from web.helpers.tmpl_context_function import tmpl_context_load_static


application_urls = web.zoo.urls.application_urls + web.zooapi.urls.application_urls

tmpl_context_load_static(application_urls)

# web.zoo.urls.application_urls +\


#
# urlpatterns = patterns('',
#      url(r'^api/1/', include('zooapi.urls')),
#      url(r'^', include('zoo.urls')),
# )

# urlpatterns += staticfiles_urlpatterns()
from django.conf.urls import include, url
from django.contrib import admin
import views

urlpatterns = [
    # Examples:
    url(r'^$', views.IndexView.as_view(), name='home'),
    url(r'^basics/$', views.BasicsView.as_view(), name='basics'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
]

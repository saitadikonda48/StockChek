from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import hello.views
import analyze.views

# Examples:
# url(r'^$', 'gettingstarted.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

urlpatterns = [
    url(r'^$', analyze.views.analyze_stock, name='index'),
    url(r'^db', hello.views.db, name='db'),
    url(r'^analyze', analyze.views.analyze_stock, name='analyze_stock'),
    url(r'^contact', hello.views.contact_us, name='contact_us'),
    url(r'^about', hello.views.about_us, name='about_us'),
    url(r'^hotlist', analyze.views.barchart, name='hotlist'),
    url(r'^admin/', include(admin.site.urls)),
]

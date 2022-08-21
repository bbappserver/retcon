"""retcon URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include,re_path
from rest_framework import routers
from rest_framework.authtoken import views
import retconpeople.api,sharedstrings.api,semantictags.api,retconstorage.api,retconcreatives.api


class OptionalSlashRouter(routers.DefaultRouter):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.trailing_slash = '/?'

router = OptionalSlashRouter()
router.register(r'people', retconpeople.api.PersonViewSet,basename='person')
router.register(r'usernames', retconpeople.api.UsernameViewSet)
router.register(r'usernumbers', retconpeople.api.UserNumberViewSet)
router.register(r'website', retconpeople.api.WebsiteViewSet)

router.register(r'strings', sharedstrings.api.StringsViewSet)
router.register(r'languages', sharedstrings.api.LanguageViewSet)

router.register(r'tag', semantictags.api.TagViewSet)
router.register(r'taglabel', semantictags.api.TagLabelViewSet)

router.register(r'file', retconstorage.api.NamedFileViewSet,basename='namedfile')

router.register(r'company', retconcreatives.api.CompanyViewSet)
router.register(r'episode', retconcreatives.api.EpisodeViewSet,basename='episode')
router.register(r'series', retconcreatives.api.SeriesViewSet,basename='series')

# from django.conf.urls.static import static
from django.shortcuts import redirect,render

from django.conf import settings



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', views.obtain_auth_token),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('creatives/', include('retconcreatives.urls')),
    path('files/', include('retconstorage.urls')),
    re_path(r'app/.*', lambda request: render(request, 'index.html')),
    path(r'', lambda request: render(request, 'landing.html')),
    # re_path(r'app/.+', lambda request: redirect('/app'))
]



# urlpatterns += static(r'/app/', document_root='retcon/static/main')
    # urlpatterns += static('/images/', document_root='app_root/path/to/images/')
    # urlpatterns += static('/js/', document_root='app_root/path/to/js/')
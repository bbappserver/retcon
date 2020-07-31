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
from django.urls import path,include
from rest_framework import routers
from rest_framework.authtoken import views
import retconpeople.api,sharedstrings.api,semantictags.api,retconstorage.api,retconcreatives.api

router = routers.DefaultRouter()
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


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', views.obtain_auth_token),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('creatives/', include('retconcreatives.urls')),
    path('files/', include('retconstorage.urls'))
]

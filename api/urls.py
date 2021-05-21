from django.urls import path

from api.views import create, feed, get, tweets

urlpatterns = [
    path("create/", create),
    path("get/", get),
    path("tweets/", tweets),
    path("feed/", feed),
]

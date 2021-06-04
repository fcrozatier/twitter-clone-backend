from django.urls import path

from api.views import feed, tweets

urlpatterns = [
    path("tweets/", tweets),
    path("feed/", feed),
]

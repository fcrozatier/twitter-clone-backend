from django.http.response import HttpResponse
from django.urls import path


def hello_api(request):
    return HttpResponse("hello from api!!!!!!!!!!")


urlpatterns = [
    path("hello/", hello_api),
]

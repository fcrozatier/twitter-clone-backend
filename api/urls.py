from django.http.response import HttpResponse
from django.urls import path

from api.models import User


def create(request):
    bob = User(name="bob").save()
    return HttpResponse(f"Created user {bob.name} with id {bob.id}")


def get(request):
    user = User.nodes.get(name="bob")
    return HttpResponse(f"Found user {user.name} with id {user.id}")


urlpatterns = [
    path("create/", create),
    path("get/", get),
]

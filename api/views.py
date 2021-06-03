from datetime import datetime
from random import randint

from django.http import HttpResponse

from api.models import Tweet, UserNode


def create(request):
    user = UserNode(uid=randint(10, 100)).save()
    return HttpResponse(f"Created user {user.uid} with id {user.id}")


def get(request):
    user = UserNode.nodes.get(name="bob")
    return HttpResponse(f"Found user {user.name} with id {user.id}")


def tweets(request):
    user = UserNode.nodes.get(name="bob")
    post = Tweet(content="hello i'm bob").save()
    user.tweets.connect(post)
    return HttpResponse(f"User {user.name} wrote {post.content}")


def feed(request):
    user = UserNode.nodes.get(name="bob")
    posts = user.tweets.match(date__lt=datetime.now())
    result, columns = user.cypher(
        """
        MATCH (u:User)
        WHERE u.uid=$uid
        MATCH (u)-[t:TWEETS]->(p:Post)
        RETURN t.date, p.content
        """,
        {"uid": user.uid},
    )
    return HttpResponse(f"Feed: {user.name} wrote {result[0][1]} at {result[0][0]}")

from django.http import HttpResponse

from api.models import Post, User


def create(request):
    user = User(name="bob").save()
    return HttpResponse(f"Created user {user.name} with id {user.id}")


def get(request):
    user = User.nodes.get(name="bob")
    return HttpResponse(f"Found user {user.name} with id {user.id}")


def tweets(request):
    user = User.nodes.get(name="bob")
    post = Post(content="hello i'm bob").save()
    user.tweets.connect(post)
    return HttpResponse(f"User {user.name} wrote {post.content}")


from datetime import datetime


def feed(request):
    user = User.nodes.get(name="bob")
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

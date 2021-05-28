import graphene
from graphene_django import DjangoObjectType

from api.models import Post


class PostType(graphene.ObjectType):
    content = graphene.String()
    created = graphene.DateTime()

    def resolve_content(parent, info):
        return "I'm then content"


class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hi")
    posts = graphene.List(PostType)

    def resolve_posts(self, info, **kwargs):
        return "Hello"

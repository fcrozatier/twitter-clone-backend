import graphene
from accounts.decorators import login_required
from api.models import UserNode
from api.schema.types import UserType


class Query(graphene.ObjectType):
    my_profile = graphene.Field(UserType)
    my_followers = graphene.List(UserType)
    my_subs = graphene.List(UserType)

    profile = graphene.Field(UserType)
    list_followers = graphene.List(UserType)
    list_following = graphene.List(UserType)

    @login_required
    def resolve_my_profile(root, info):
        user_uid = info.context.user.uid
        user_node = UserNode.nodes.get(uid=user_uid)
        return user_node

    @login_required
    def resolve_my_followers(root, info):
        user_uid = info.context.user.uid
        user_node = UserNode.nodes.get(uid=user_uid)
        return user_node.followers.all()

    @login_required
    def resolve_my_subs(root, info):
        user_uid = info.context.user.uid
        user_node = UserNode.nodes.get(uid=user_uid)
        return user_node.follows.all()

    def resolve_followers(root, info, **kwargs):
        pass

    def resolve_following(root, info, **kwargs):
        pass

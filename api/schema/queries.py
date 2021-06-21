import graphene
from accounts.decorators import login_required
from api.models import UserNode
from api.schema.types import UserType


# TODO create my_feed, unlike, unfollow
class Query(graphene.ObjectType):
    my_profile = graphene.Field(UserType)
    my_followers = graphene.List(UserType)
    my_subs = graphene.List(UserType)

    user_profile = graphene.Field(UserType, uid=graphene.String())
    user_followers = graphene.List(UserType)
    user_subs = graphene.List(UserType)

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

    @login_required
    def resolve_user_profile(root, info, uid):
        pass

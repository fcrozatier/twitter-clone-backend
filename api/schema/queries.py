import graphene
from accounts.decorators import login_required
from api.schema.types import LikeableType, UserType


# TODO create my_feed, tags
class Query(graphene.ObjectType):
    my_profile = graphene.Field(UserType)
    my_feed = graphene.List(LikeableType)

    user_profile = graphene.Field(UserType, uid=graphene.String())

    @login_required
    def resolve_my_profile(root, info):
        user_uid = info.context.user.uid
        user_node = UserType.get_node(user_uid)
        return user_node

    @login_required
    def resolve_my_feed(root, info):
        user_uid = info.context.user.uid
        user_node = UserType.get_node(user_uid)

    @login_required
    def resolve_user_profile(root, info, uid):
        return UserType.get_node(uid)

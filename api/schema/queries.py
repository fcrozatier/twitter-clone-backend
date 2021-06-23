import graphene
from accounts.decorators import login_required
from api.schema.types import LikeableType, UserType


# TODO create my_feed, tags
class Query(graphene.ObjectType):
    my_profile = graphene.Field(UserType)
    my_content = graphene.List(LikeableType, skip=graphene.Int(), limit=graphene.Int())
    my_feed = graphene.List(LikeableType, skip=graphene.Int(), limit=graphene.Int())

    user_profile = graphene.Field(UserType, uid=graphene.String())

    @login_required
    def resolve_my_profile(root, info):
        user_node = UserType.get_user_from_context(info)
        return user_node

    @login_required
    def resolve_my_content(root, info, **kwargs):
        user_node = UserType.get_user_from_context(info)
        return user_node.content(skip=kwargs["skip"], limit=kwargs["limit"])

    @login_required
    def resolve_my_feed(root, info, **kwargs):
        user_node = UserType.get_user_from_context(info)
        return user_node.feed(skip=kwargs["skip"], limit=kwargs["limit"])

    @login_required
    def resolve_user_profile(root, info, uid):
        return UserType.get_node(uid)

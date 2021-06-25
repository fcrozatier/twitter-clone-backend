import graphene
from accounts.decorators import login_required
from api.schema.types import LikeableType, TweetType, UserType
from neomodel import db


class Query(graphene.ObjectType):
    my_profile = graphene.Field(UserType)
    my_feed = graphene.List(
        LikeableType,
        skip=graphene.Int(),
        limit=graphene.Int(),
    )

    user_profile = graphene.Field(
        UserType,
        uid=graphene.String(required=True),
    )

    search = graphene.List(
        TweetType,
        tag=graphene.String(required=True),
        skip=graphene.Int(),
        limit=graphene.Int(),
    )

    @login_required
    def resolve_my_profile(root, info):
        user_node = UserType.get_node_from_context(info)
        return user_node

    @login_required
    def resolve_my_feed(root, info, **kwargs):
        user_node = UserType.get_node_from_context(info)
        return user_node.feed(skip=kwargs["skip"], limit=kwargs["limit"])

    @login_required
    def resolve_user_profile(root, info, uid):
        return UserType.get_node(uid)

    @login_required
    def resolve_search(root, info, tag, skip=0, limit=100, **kwargs):
        params = {"tag": tag, "skip": skip, "limit": limit}

        results, meta = db.cypher_query(
            """
            match (h:HashtagNode)<-[r:HASHTAG]-(t:TweetNode)
            where h.tag = $tag
            return t
            order by t.created desc
            skip $skip
            limit $limit
            """,
            params=params,
            resolve_objects=True,
        )

        return [item[0] for item in results]

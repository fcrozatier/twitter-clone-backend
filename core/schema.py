import accounts.schema
import api.schema
import graphene
from graphql_auth.schema import MeQuery, UserQuery


class Query(
    UserQuery,
    MeQuery,
    api.schema.Query,
    graphene.ObjectType,
):
    pass


class Mutation(
    accounts.schema.AuthMutation,
    api.schema.Mutation,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)

import accounts.schema
import api.schema.mutations
import api.schema.queries
import graphene
from graphql_auth.schema import MeQuery, UserQuery


class Query(
    UserQuery,
    MeQuery,
    api.schema.queries.Query,
    graphene.ObjectType,
):
    pass


class Mutation(
    accounts.schema.AuthMutation,
    api.schema.mutations.Mutation,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)

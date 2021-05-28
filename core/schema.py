import api.schema
import graphene


class Query(api.schema.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)

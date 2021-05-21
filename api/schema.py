from ariadne import gql, make_executable_schema

from api.queries import query

type_defs = gql(
    """
      type Query {
        hello: String!
      }
    """
)

schema = make_executable_schema(type_defs, query)

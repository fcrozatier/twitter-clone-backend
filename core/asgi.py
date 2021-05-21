import os

from api.queries import query
from api.schema import type_defs
from ariadne import make_executable_schema
from ariadne.asgi import GraphQL

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")


# application = GraphQL(schema)

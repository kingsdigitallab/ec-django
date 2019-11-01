import deeds.schema
import graphene


class Query(deeds.schema.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)

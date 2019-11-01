from deeds.models import Origin, Person
from geonames_place.models import Place
from graphene import ObjectType, relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField


class OriginNode(DjangoObjectType):
    class Meta:
        model = Origin
        filter_fields = ['person', 'place__address', 'origin_type']
        interfaces = (relay.Node, )


class PersonNode(DjangoObjectType):
    class Meta:
        model = Person
        filter_fields = ['name', 'surname']
        interfaces = (relay.Node, )


class PlaceNode(DjangoObjectType):
    class Meta:
        model = Place
        filter_fields = ['address', 'country', 'lat', 'lon']
        interfaces = (relay.Node, )


class Query(object):
    origin = relay.Node.Field(OriginNode)
    all_origins = DjangoFilterConnectionField(OriginNode)

    person = relay.Node.Field(PersonNode)
    all_persons = DjangoFilterConnectionField(PersonNode)

    place = relay.Node.Field(PlaceNode)
    all_places = DjangoFilterConnectionField(PlaceNode)

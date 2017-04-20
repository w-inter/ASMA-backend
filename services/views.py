from rest_framework import views, viewsets, permissions
from services.api.geonames import search_entity
from rest_framework import status
from rest_framework.response import Response
from .permissions import ReadOnlyPermission
from .models import Tag, Node, Way, Relation, Parameters, CorrespondenceValide, CorrespondenceEntity, Geoname, \
    FeatureCode, CorrespondenceTypes, CorrespondenceTypesClose, CorrespondenceInvalide, ParametersScorePertinence
from .serializer import TagSerializer, PointSerializer, WaySerializer, RelationSerializer, \
    CorrespondenceValideSerializer, CorrespondenceEntitySerializer, ParameterSerializer, GeonameSerializer,\
    FeatureCodeSerializer, CorrespondenceTypesSerializer, CorrespondenceTypesCloseSerializer, \
    CorrespondenceInvalideSerializer, ParametersScorePertinenceSerializer
from rest_framework.request import Request
from rest_framework.decorators import detail_route


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (ReadOnlyPermission,)


class PointViewSet(viewsets.ModelViewSet):
    queryset = Node.objects.all()
    serializer_class = PointSerializer
    permission_classes = (ReadOnlyPermission,)


class WayViewSet(viewsets.ModelViewSet):
    queryset = Way.objects.all()
    serializer_class = WaySerializer
    permission_classes = (ReadOnlyPermission,)


class RelationViewSet(viewsets.ModelViewSet):
    queryset = Relation.objects.all()
    serializer_class = RelationSerializer
    permission_classes = (ReadOnlyPermission,)


class GeonameViewSet(viewsets.ModelViewSet):
    queryset = Geoname.objects.all()
    serializer_class = GeonameSerializer
    permission_classes = (ReadOnlyPermission,)


class FeatureCodeViewSet(viewsets.ModelViewSet):
    queryset = FeatureCode.objects.all()
    serializer_class = FeatureCodeSerializer
    permission_classes = (ReadOnlyPermission, )


class ParametersViewSet(viewsets.ModelViewSet):
    queryset = Parameters.objects.all()
    serializer_class = ParameterSerializer
    permission_classes = (ReadOnlyPermission,)


class ParametersScorePertinenceViewSet(viewsets.ModelViewSet):
    queryset = ParametersScorePertinence.objects.all()
    serializer_class = ParametersScorePertinenceSerializer
    # permission_classes = (ReadOnlyPermission,)


class CorrespondenceEntityView(viewsets.ViewSet):

    def list(self, request, format=None):

        if request.GET.get('osm') and request.GET.get('gn'):
            try:
                correspondence = CorrespondenceEntity.objects.get(reference_osm=int(request.GET.get('osm')),
                                                                  reference_gn=int(request.GET.get('gn')))

                serializer = CorrespondenceEntitySerializer(correspondence, many=True)

            except CorrespondenceEntity.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.GET.get('gn'):
            try:
                correspondence = CorrespondenceEntity.objects.filter(reference_gn=int(request.GET.get('gn')))

                serializer = CorrespondenceEntitySerializer(correspondence, many=True)

            except CorrespondenceEntity.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        elif request.GET.get('osm'):
            try:
                correspondence = CorrespondenceEntity.objects.filter(reference_osm=int(request.GET.get('osm')))

                serializer = CorrespondenceEntitySerializer(correspondence, many=True)

            except CorrespondenceEntity.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)


        else:
            correspondences = CorrespondenceEntity.objects.all()
            serializer = CorrespondenceEntitySerializer(correspondences, many=True)

        return Response(serializer.data)


class GeonameSearch(views.APIView):
    def get(self, request, query, *args, **kwargs):
        list = search_entity(query)
        response = Response(list, status=status.HTTP_200_OK)

        return response


class CorrespondenceValideView(viewsets.ViewSet):

    def list(self, request, format=None):

        # http://127.0.0.1:8000/correspondence-valide/?osm=194554955&gn=822469
        if request.GET.get('osm') and request.GET.get('gn'):
            try:
                correspondence = CorrespondenceValide.objects.get(reference_osm=int(request.GET.get('osm')),
                                                              reference_gn=int(request.GET.get('gn')))
            except CorrespondenceValide.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            serializer = CorrespondenceValideSerializer(correspondence)

        else:
            #http://127.0.0.1:8000/correspondence-valide
            correspondences = CorrespondenceValide.objects.all()
            serializer = CorrespondenceValideSerializer(correspondences, many=True)

        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CorrespondenceValideSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            CorrespondenceEntity.objects.filter(reference_gn=request.data['reference_gn'],
                                                reference_osm=request.data['reference_osm']).delete()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EntityOSMDetails(viewsets.ViewSet):
    def list(self, request, id, format=None):

        serializer_context = {
            'request': Request(request),
        }

        attributes = Node.objects.filter(pk=id)
        serializer = PointSerializer(attributes, many=True, context=serializer_context)
        serializer_points = {}
        serializer_ways = {}

        type = 'NODE'
        if not attributes:
            attributes = Way.objects.filter(pk=id)
            serializer = WaySerializer(attributes, many=True, context=serializer_context)

            points = Node.objects.filter(way_reference=id)
            serializer_points = PointSerializer(points, many=True, context=serializer_context).data
            serializer_ways = {}

            type = 'WAY'

        if not attributes:
            attributes = Relation.objects.filter(pk=id)
            serializer = RelationSerializer(attributes, many=True)

            points = Node.objects.filter(relation_reference=id)
            serializer_points = PointSerializer(points, many=True, context=serializer_context).data

            ways = Way.objects.filter(relation_reference=id)
            serializer_ways = WaySerializer(ways, many=True, context=serializer_context).data

            type = 'RELATION'

        if not attributes:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer_tag = {}
        try:

            tag_list = Tag.objects.filter(reference=id)
            serializer_tag = TagSerializer(tag_list, many=True)
        except Tag.DoesNotExist:
            pass

        entity = {
            'type': type,
            'attributes': serializer.data,
            'serializer_points': serializer_points,
            'serializer_ways': serializer_ways,
            'tag_list': serializer_tag.data
        }

        return Response(entity, status=status.HTTP_200_OK)


class CorrespondenceInvalideView(viewsets.ViewSet):
    def list(self, request, format=None):

        # http://127.0.0.1:8000/correspondence-invalide/?osm=194554955&gn=822469
        if request.GET.get('osm') and request.GET.get('gn'):
            try:
                correspondence = CorrespondenceInvalide.objects.get(reference_osm=int(request.GET.get('osm')),
                                                                    reference_gn=int(request.GET.get('gn')))
            except CorrespondenceInvalide.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            serializer = CorrespondenceInvalideSerializer(correspondence)

        else:
            # http://127.0.0.1:8000/correspondence-invalide
            correspondences = CorrespondenceInvalide.objects.all()
            serializer = CorrespondenceInvalideSerializer(correspondences, many=True)

        return Response(serializer.data)

    def post(self, request, format=None):

        print(request.data)
        serializer = CorrespondenceInvalideSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            CorrespondenceEntity.objects.filter(reference_gn=request.data['reference_gn'],
                                                reference_osm=request.data['reference_osm']).delete()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CorrespondenceTypesViewSet(viewsets.ModelViewSet):
    # TODO: Help pour visualizer... blablabla

    queryset = CorrespondenceTypes.objects.all()
    serializer_class = CorrespondenceTypesSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


class CorrespondenceTypesCloseViewSet(viewsets.ModelViewSet):
    queryset = CorrespondenceTypesClose.objects.all()
    serializer_class = CorrespondenceTypesCloseSerializer
    #permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
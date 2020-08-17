from .models import Episode,Series,Company
from retconpeople.models import Person
from remotables.api import ContentResourceSerializer
from remotables.models import ContentResource
from sharedstrings.models import Strings
from rest_framework import serializers,viewsets,status,response
from rest_framework.decorators import action,renderer_classes



class CompanySerializer(serializers.HyperlinkedModelSerializer):
    
    # id= serializers.IntegerField()
    # name = serializers.CharField()

    # name = serializers.SlugRelatedField(slug_field='name',queryset=Strings.objects.all())
    name = serializers.SlugRelatedField(slug_field='name',read_only=True)
    class Meta:
        model = Company
        fields = ['id','name']
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        term=request.query_params.get('icontains',None)
        if term:
            queryset=queryset.filter(name__icontains=term)
        
        term=request.query_params.get('istartswith',None)
        if term:
            queryset=queryset.filter(name__istartswith=term)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

class CompanyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    # def list(self, request, *args,**kwargs):
    #     d=request.data
    #     if 'icontains' in d:
    #         self.queryset=queryset.filter(name__icontains=d['icontains'])
    #     return super().list(request,*args,**kwargs)

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())
    #     term=request.query_params.get('icontains',None)
    #     if term:
    #         queryset=queryset.filter(name__icontains=term)
        
    #     term=request.query_params.get('istartswith',None)
    #     if term:
    #         queryset=queryset.filter(name__istartswith=term)

    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)


    # @action(detail=False, methods=['get','post'])
    # def search(self, request, pk=None,format=None):
    #     d=request.data
    #     urls = d['urls'] if 'urls' in d else []
    #     identifiers = d['identifiers'] if 'identifiers' in d else []
    #     l=Person.search_by_identifiers(urls=urls,user_identifiers=identifiers)
    #     serializer=PersonSerializer(l,many=True)
    #     if len(l)>0:
            
    #         return Response(serializer.data,status=200)
    #     else:
    #         return Response(serializer.data,status=404)


class EpisodeSerializer(serializers.ModelSerializer):
    
    # id= serializers.IntegerField()
    # name = serializers.CharField()

    class Meta:
        model = Episode
        fields = ['id','name']
    

class EpisodeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Episode.objects.all()
    serializer_class = EpisodeSerializer

class SeriesSerializer(serializers.ModelSerializer):
    
    # id= serializers.IntegerField()
    # name = serializers.CharField()

    published_by = serializers.HyperlinkedRelatedField(required=False,
        many=True,
    queryset=Company.objects.all(),
    view_name='company-detail',
    style={'base_template': 'input.html'})

    created_by = serializers.HyperlinkedRelatedField(required=False,allow_null=True,
    queryset=Person.objects.all(),
    view_name='person-detail',
    style={'base_template': 'input.html'})

    files= serializers.SlugRelatedField(many=True,slug_field="sha256",read_only=True)

    external_representation= ContentResourceSerializer(many=True,required=False)

    def create(self, validated_data):
        urls_data = validated_data.pop('external_representation') if 'external_representation' in validated_data else []
        series = Series.objects.create(**validated_data)
        for url_data in urls_data:
            d=None
            if isinstance(url_data,str):
                d={'url':url_data}
            else:
                d=url_data
                serializer = ContentResourceSerializer(data=d)
                if serializer.is_valid():
                    d= serializer.validated_data
            res=ContentResource.objects.create(**d)
            series.external_representation.add(res)
        series.save()
        return series


    class Meta:
        model = Series
        fields = ['id','name','published_by','published_on','published_on_precision','created_by','files','external_representation']
    

class SeriesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Series.objects.all()
    serializer_class = SeriesSerializer
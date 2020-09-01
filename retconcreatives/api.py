from .models import Episode,Series,Company
from retconpeople.models import Person
from retconpeople.api import PersonSerializer
from remotables.api import ContentResourceSerializer
from remotables.models import ContentResource
from sharedstrings.models import Strings
from sharedstrings.api import StringsField
from semantictags.api import TaggableViewsetMixin,TaggableSerializerMixin
from retconstorage.models import ManagedFile
from rest_framework import serializers,viewsets,status,response
from rest_framework.decorators import action,renderer_classes
from django.db import transaction
from django.conf import Settings
from retcon.api import RetconModelViewSet



class CompanySerializer(serializers.HyperlinkedModelSerializer):
    
    # id= serializers.IntegerField()
    # name = serializers.CharField()

    # name = serializers.SlugRelatedField(slug_field='name',queryset=Strings.objects.all())
    name = StringsField()
    class Meta:
        model = Company
        fields = ['id','name','case_sensitive_name']
    
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
        return response.Response(serializer.data)
    

class CompanyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Companys to be viewed or edited.
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

class CreativeWorkSerializerMixin(TaggableSerializerMixin):
    files= serializers.SlugRelatedField(many=True,slug_field="sha256",read_only=True,style={'base_template': 'input.html'})
    
    external_representations = ContentResourceSerializer(required=False,allow_null=False,many=True,
    #view_name='company-detail',
    # queryset=ContentResource.objects.all(),
    style={'base_template': 'input.html'})


class CreativeWorkViewsetMixin(TaggableViewsetMixin):

    @action(detail=True, methods=['get','post','delete'])
    def producers(self, request, pk=None,format=None):
        master=self.get_object()
        subordinate_field_name='produced_by'
        subordinate_field_serializer = CompanySerializer
        subordinate_type = Company
        return self.generic_master_detail_list_request_handler(request, master, subordinate_field_serializer, subordinate_field_name, subordinate_type)
    

    @action(detail=True, methods=['get','post','delete'])
    def publishers(self, request, pk=None,format=None):
        master=self.get_object()
        subordinate_field_name='published_by'
        subordinate_field_serializer = CompanySerializer
        subordinate_type = Company
        return self.generic_master_detail_list_request_handler(request, master, subordinate_field_serializer, subordinate_field_name, subordinate_type)

class EpisodeSerializer(CreativeWorkSerializerMixin):
    
    # id= serializers.IntegerField()
    # name = serializers.CharField()
    # files= serializers.SlugRelatedField(many=True,slug_field="sha256",read_only=True,style={'base_template': 'input.html'})
    # # tags = serializers.PrimaryKeyRelatedField(required=False,allow_null=False,many=True,
    # # #view_name='company-detail',
    # # queryset=Tag.objects.all(),
    # # style={'base_template': 'input.html'})
    # # external_representations = serializers.PrimaryKeyRelatedField(required=False,allow_null=False,many=True,
    # # #view_name='company-detail',
    # # queryset=ContentResource.objects.all(),
    # # style={'base_template': 'input.html'})

    # external_representations = ContentResourceSerializer(required=False,allow_null=False,many=True,
    # #view_name='company-detail',
    # # queryset=ContentResource.objects.all(),
    # style={'base_template': 'input.html'})

    class Meta:
        model = Episode
        exclude = []
    

class EpisodeViewSet(CreativeWorkViewsetMixin):
    """
    API endpoint that allows Episodes to be viewed or edited.
    """
    queryset = Episode.objects.all()
    serializer_class = EpisodeSerializer

class SeriesSerializer(CreativeWorkSerializerMixin):
    
    # id= serializers.IntegerField()
    # name = serializers.CharField()

    # published_by = serializers.PrimaryKeyRelatedField(required=False,
    #     many=True, 
    #     #view_name='company-detail',
    # queryset=Company.objects.all(),
    # style={'base_template': 'input.html'})

    # created_by = serializers.PrimaryKeyRelatedField(required=False,allow_null=True,
    # #view_name='person-detail',
    # queryset=Person.objects.all(),
    # style={'base_template': 'input.html'})

    # produced_by = serializers.PrimaryKeyRelatedField(required=False,allow_null=False,many=True,
    # #view_name='company-detail',
    # queryset=Company.objects.all(),
    # style={'base_template': 'input.html'})

    # files= serializers.SlugRelatedField(many=True,slug_field="sha256",read_only=True,style={'base_template': 'input.html'})

    # external_representations= ContentResourceSerializer(many=True,required=False)

    def create(self, validated_data):
        urls_data = validated_data.pop('external_representations') if 'external_representations' in validated_data  else []
        files = validated_data.pop('files') if 'files' in validated_data and validated_data['files'] is not None else []

        #TODO,WHAT WAS IS THINKING, CREATING ON THESE FIELDS IS A TERRIBLE IDEA, only do this with owned fields
        # produced_by = validated_data.pop('produced_by') if 'produced_by' in validated_data and validated_data['produced_by'] is not None else []
        # published_by = validated_data.pop('published_by') if 'published_by' in validated_data and validated_data['published_by'] is not None else []
        # created_by = validated_data.pop('created_by') if 'created_by' in validated_data else None

        with transaction.atomic():
            series = Series.objects.create(**validated_data)
            for x in urls_data:
                d=None
                if isinstance(x,str): #TODO can't happen need custom field validation
                    d={'url':x}
                else:
                    d=x
                    serializer = ContentResourceSerializer(data=d)
                    if serializer.is_valid():
                        d= serializer.validated_data
                    else:
                        raise ValueError(serializer.error_messages)
                res,created=ContentResource.objects.get_or_create(**d)
                series.external_representations.add(res)
            try:
                for x in files:
                    b=bytes.fromhex(x)
                    o=ManagedFile.objects.get(sha256=x)
                    series.files.add(o)
            except ManagedFile.DoesNotExist as e:
                return response.Response({'status':'fail','message':'None existant file','data':x},status=status.HTTP_428_PRECONDITION_REQUIRED)
        
        #TODO Phase these out
        
        # for x in published_by:
        #     d=None
        #     serializer = CompanySerializer(data=x)
        #     if serializer.is_valid():
        #         d= serializer.validated_data
        #     res=Company.objects.create(**d)
        #     series.produced_by.add(res)
        
        # if created_by is None:
        #     series.created_by=None
        # else:
        #     serializer = PersonSerializer(data=created_by)
        #     if serializer.is_valid():
        #         d= serializer.validated_data
        #     else:
        #         raise ValueError(serializer.error_messages)
        #     res=Person.objects.create(**d)
        #     series.created_by=res
            #series.produced_by.add(x)
        # for x in created_by:
        #     serializer = PersonSerializer(data=x)
        #     if serializer.is_valid():
        #         d= serializer.validated_data
        #     res=Company.objects.create(**d)
        #     series.created_by.add(res)
        series.save()
        return series

    class Meta:
        model = Series
        exclude=[]
        #fields = ['id','name','published_by','published_on','published_on_precision','created_by','files','external_representations','parent_series','medium','produced_by']
    

class SeriesViewSet(CreativeWorkViewsetMixin):
    """
    API endpoint that allows Series to be viewed or edited.
    """
    queryset = Series.objects.all()
    serializer_class = SeriesSerializer

    


    @action(detail=True, methods=['get','post','delete'])
    def producers(self, request, pk=None,format=None):
        master=self.get_object()
        subordinate_field_name='produced_by'
        subordinate_field_serializer = CompanySerializer
        subordinate_type = Company
        return self.generic_master_detail_list_request_handler(request, master, subordinate_field_serializer, subordinate_field_name, subordinate_type)
    

    @action(detail=True, methods=['get','post','delete'])
    def publishers(self, request, pk=None,format=None):
        master=self.get_object()
        subordinate_field_name='published_by'
        subordinate_field_serializer = CompanySerializer
        subordinate_type = Company
        return self.generic_master_detail_list_request_handler(request, master, subordinate_field_serializer, subordinate_field_name, subordinate_type)

    

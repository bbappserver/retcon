from django.shortcuts import redirect,get_object_or_404
from django.db.transaction import atomic
from rest_framework import serializers, viewsets,status,decorators
from rest_framework.response import Response
from .models import Tag, TagLabel
from sharedstrings.api import StringsField
from sharedstrings.models import Strings
from sharedstrings.api import StringsSerializer
from retcon.api import RetconModelViewSet

class TagLabelSerializer(serializers.ModelSerializer):
    language = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='isocode'
    )
    #label= StringsField()
    definitions = serializers.SerializerMethodField()
    expand_implied = serializers.SerializerMethodField()
    
    def get_definitions(self,obj):
        l= Tag.objects.filter(labels=obj) | Tag.objects.filter(canonical_label=obj)
        s=set()
        for t in l:
            if t.id not in s:
                s.add(t.id)
        return list(s)
    # label = serializers.CharField()
    # label = serializers.SlugRelatedField(
    #         many=False,
    #         read_only=True,
    #         slug_field='name'
    #     )

    class Meta:
        model = TagLabel
        #depth=1
        fields = ['label','language','definitions']



class TagLabelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = TagLabel.objects.all()
    serializer_class = TagLabelSerializer

    def get_queryset(self):
        queryset = TagLabel.objects.all()
        lang = self.request.query_params.get('lang', self.request.LANGUAGE_CODE)
        if lang != "any":
            queryset=queryset.filter(language__isocode=lang)
        return queryset

    # def retrieve(self, request, pk=None):
    #     queryset = TagLabel.objects.all()
    #     lang= request.GET['locale'] if 'locale' in request.GET else request.LANGUAGE_CODE
        
    #     if not lang == "any":
    #         queryset=queryset.filter(isocode=lang)
        
    #     tag=get_object_or_404(queryset,pk=pk)
        
    #     serializer = TagLabelSerializer(tag,context={'request': request})
    #     return Response(serializer.data)
    
    # def list(self, request):
    #     queryset = TagLabel.objects.all()
    #     lang= request.GET['locale'] if 'locale' in request.GET else request.LANGUAGE_CODE
        
    #     if not lang == "any":
    #         queryset=queryset.filter(language__isocode=lang)
        
    #     serializer = TagLabelSerializer(queryset,many=True,context={'request': request})
    #     return Response(serializer.data)

    @decorators.action(methods=['post'],detail=True)
    def add_definition(self,request):
        label = self.get_object()
        Tag.get(id=request.data)
        Tag.labels.add(label)
        Tag.save()
        pass



class TagSerializer(serializers.ModelSerializer):
    #labels = TagLabelSerializer(many=True)
    labels = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='label'
    )
    canonical_label = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='label'
    )

    class Meta:
        model = Tag
        depth = 1
        fields = ['id', 'labels','canonical_label']

class TerseTagSerializer(serializers.ModelSerializer):
    canonical_label = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='label'
    )

    class Meta:
        model = Tag
        depth = 1
        fields = ['id','canonical_label']
    


class TagViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    @decorators.action(methods=['patch'],detail=True)
    def add_label(self,request):
        queryset = TagLabel.objects.all()
        try:
            lang= request.PATCH['locale'] if 'locale' in request.PATCH else request.LANGUAGE_CODE

            with atomic():
                tag= self.get_object()
                s=Strings.objects.get_or_create(name=request.PATCH.name)
                s.save()
                label=TagLabel.objects.get_or_create(language__isocode=lang,label=s)
                label.save()
            return Response("OK", status=status.HTTP_200_OK)
        except:
            return Response("An error occured", status=status.HTTP_400_BAD_REQUEST)
        

class TaggableViewsetMixin(RetconModelViewSet):
    
    @decorators.action(detail=True, methods=['get','post','delete'])
    def tags(self, request, pk=None,format=None):
        master=self.get_object()
        subordinate_field_name='tags'
        subordinate_field_serializer = TagSerializer
        subordinate_type = Tag
        return self.generic_master_detail_list_request_handler(request, master, subordinate_field_serializer, subordinate_field_name, subordinate_type)

    @decorators.action(detail=True, methods=['get','post','delete'])
    def ambiguous_tags(self, request, pk=None,format=None):
        master=self.get_object()
        subordinate_field_name='ambiguous_tags'
        subordinate_field_serializer = StringsSerializer
        subordinate_type = Strings
        return self.generic_master_detail_list_request_handler(request, master, subordinate_field_serializer, subordinate_field_name, subordinate_type)

class TaggableSerializerMixin(serializers.ModelSerializer):
    tags= serializers.PrimaryKeyRelatedField(required=False,allow_null=False,many=True,
    queryset=Tag.objects.all(),
    style={'base_template': 'input.html'})
    
    ambiguous_tags= serializers.SlugRelatedField(required=False,allow_null=False,many=True,slug_field='name',
    queryset=Strings.objects.all(),
    style={'base_template': 'input.html'})
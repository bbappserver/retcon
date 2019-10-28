from django.shortcuts import redirect,get_object_or_404
from django.db.transaction import atomic
from rest_framework import serializers, viewsets,status
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from .models import Tag, TagLabel


class TagLabelSerializer(serializers.ModelSerializer):
    language = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='isocode'
    )
    # label = serializers.CharField()
    # label = serializers.SlugRelatedField(
    #         many=False,
    #         read_only=True,
    #         slug_field='name'
    #     )

    class Meta:
        model = TagLabel
        depth=1
        fields = ['definitions','language', 'label']



class TagLabelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = TagLabel.objects.all()
    serializer_class = TagLabelSerializer

    def retrieve(self, request, pk=None):
        queryset = TagLabel.objects.all()
        lang= request.GET['locale'] if 'locale' in request.GET else request.LANGUAGE_CODE
        
        if not lang == "any":
            queryset=queryset.filter(isocode=lang)
        
        tag=get_object_or_404(queryset,pk=pk)
        
        serializer = TagLabelSerializer(tag,context={'request': request})
        return Response(serializer.data)
    
    def list(self, request):
        queryset = TagLabel.objects.all()
        lang= request.GET['locale'] if 'locale' in request.GET else request.LANGUAGE_CODE
        
        if not lang == "any":
            queryset=queryset.filter(language__isocode=lang)
        
        serializer = TagLabelSerializer(queryset,many=True,context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['patch'])
    def add_definition(self,request):
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

    @detail_route(methods=['patch'])
    def add_label(self,request):
        queryset = TagLabel.objects.all()
        try:
            lang= request.PATCH['locale'] if 'locale' in request.PATCH else request.LANGUAGE_CODE

            with atomic:
                tag= self.get_object()
                s=Strings.objects.get_or_create(name=request.PATCH.name)
                s.save()
                label=TagLabel.objects.get_or_create(language__isocode=lang,label=s)
                label.save()
            return Response("OK", status=status.HTTP_200_OK)
        except:
            return Response("An error occured", status=status.HTTP_400_BAD_REQUEST)
        


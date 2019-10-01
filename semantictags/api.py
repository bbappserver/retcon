from rest_framework import serializers,viewsets
from .models import Tag,TagLabel

class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        #fields = ['first_name', 'last_name', 'description', 'tags']

class TagViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class TagLabelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TagLabel
        label = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='name'
     )
        #fields = ['website','name']

class TagLabelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = TagLabel.objects.all()
    serializer_class = TagLabelSerializer
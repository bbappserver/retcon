from rest_framework import serializers,viewsets
from .models import Strings,Language

class StringsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Strings
        fields = ['id','name']

class StringsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Strings.objects.all()
    serializer_class = StringsSerializer

class LanguageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Language
        #fields = ['website','name']

class LanguageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer

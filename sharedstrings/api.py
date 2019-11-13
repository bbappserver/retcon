from rest_framework import serializers,viewsets,response
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

    def list(self, request):
        search=request.query_params['term']
        queryset = Strings.objects.filter(name__icontains=search)
        l=(x.name for x in queryset)
        
        #serializer = StringsSerializer(queryset, many=True)
        return response.Response(l)


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

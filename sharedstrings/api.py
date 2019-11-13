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

    def string_score(self,s,match):
        N= len(match)+1
        score=0
        for i in range(len(match)):
            if i < len(s):
                if (s[i].lower() == match[i].lower()):
                    score+=N
            N-=1
        return score


    def list(self, request):
        search=request.query_params['term']
        queryset = Strings.objects.filter(name__icontains=search).order_by('name')
        l=( (x.name,self.string_score(x.name,search)) for x in queryset)
        sorted_by_second = sorted(l, key=lambda tup: -tup[1])
        l= [x[0] for x in sorted_by_second]

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

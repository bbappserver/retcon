from rest_framework import serializers,viewsets,response
from .models import Strings,Language

class StringsSerializer(serializers.ModelSerializer):
    
    # id= serializers.IntegerField()
    # name = serializers.CharField()

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
    
    
    # def partial_update(self, request, *args, **kwargs):
    #     instance = self.queryset.get(pk=kwargs.get('pk'))
    #     serializer = self.serializer_class(instance, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return response.Response(serializer.data)


    def list(self, request):

        if len(request.query_params)==0:
            return super().list(request)
        if 'name' in request.query_params:
            #A programatic general search
            return super().list(request)
        elif 'term' in request.query_params:
            #A search for autocomplation
            search=request.query_params['term']
            queryset = Strings.objects.filter(name__icontains=search).order_by('name')
            l=( (x.name,self.string_score(x.name,search)) for x in queryset)
            sorted_by_second = sorted(l, key=lambda tup: -tup[1])
            l= [x[0] for x in sorted_by_second]
            status=200
            if len(l)==0:
                status=404
            #serializer = StringsSerializer(queryset, many=True)
            return response.Response(l,status=status)
        else:
            return super().list(request)


class StringsField(serializers.RelatedField):

    def __init__(self,*args,**kwargs):
        #kwargs['read_only']=False
        if 'queryset' not in kwargs and ('read_only' not in kwargs or kwargs['read_only'] == False):
            kwargs['queryset']= Strings.objects.all()
        
        return super().__init__(*args,**kwargs)

    def to_representation(self, value):
#        assert(isinstance(value.name,str))
        return str(value.name)
    def to_internal_value(self, data):
        if data is None: return None
        if isinstance(data,Strings):return data
        if isinstance(data,str):
            if hasattr(self,'queryset'):
                qs= self.queryset
            else:
                qs = Strings.objects.all()

            s, created = qs.get_or_create(name=data)
            return s
        else:
            raise serializers.ValidationError('Attempted to assign unconvertible type to StringsField')
        


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

    def create(self,request):
        return response.Response("Languages cannot be edited via API",status=403)
    def update(self,request):
        return response.Response("Languages cannot be edited via API",status=403)

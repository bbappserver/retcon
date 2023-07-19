from .models import NamedFile,ManagedFile
from rest_framework import serializers,viewsets,status,response
from rest_framework.decorators import action,renderer_classes
from rest_framework.response import Response
class NamedFileSerializer(serializers.ModelSerializer):
    
    # id= serializers.IntegerField()
    # name = serializers.CharField()

    class Meta:
        model = NamedFile
        fields = ['id','name','identity']
    

class NamedFileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = NamedFile.objects.all()
    serializer_class = NamedFileSerializer

    # def list(self, request, *args,**kwargs):
    #     d=request.data
    #     if 'icontains' in d:
    #         self.queryset=queryset.filter(name__icontains=d['icontains'])
    #     return super().list(request,*args,**kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        term=request.query_params.get('icontains',None)
        if term:
            queryset=queryset.filter(name__icontains=term)
        
        term=request.query_params.get('istartswith',None)
        if term:
            queryset=queryset.filter(name__istartswith=term)
        
        term=request.query_params.get('identityid',None)
       
        if term:
            try:
                term=int(term)
                queryset=queryset.filter(identity_id=term)
            except:
                return Response({'status':'error','message':'identityid must be integer'},status=status.HTTP_400_BAD_REQUEST)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


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
class HexBinField(serializers.CharField):
    """
    Color objects are serialized into 'rgb(#, #, #)' notation.
    """
    def to_representation(self, value):
        return value.hex()
    def to_internal_value(self, data):
        return bytes.fromhex(data)

class ManagedFileSerializer(serializers.ModelSerializer):
        md5=HexBinField(required=False)
        sha256=HexBinField(required=False)
        class Meta:
            model = ManagedFile
            fields = ['id','md5','sha256']
        
class ManagedFileViewset(viewsets.ModelViewSet):
        
        @action(methods=['post'],detail=False)
        def get_or_create(self,pk,request):
            raise NotImplementedError()
            out,created=ManagedFile.objects.get_or_create(**request.body)
            ManagedFileSerializer(out)
            if created:
                return response.Response(out.data,status=status.HTTP_201_CREATED)
            else:
                return response.Response(out.data,status=status.HTTP_200_OK)
            
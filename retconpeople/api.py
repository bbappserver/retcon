from rest_framework import serializers,viewsets
from .models import Person,UserName,UserNumber,Website

class PersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'description', 'tags']

class PersonViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Person.objects.all()
    serializer_class = PersonSerializer

class UsernameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserName
        fields = ['website','name']

class UsernameViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = UserName.objects.all()
    serializer_class = UsernameSerializer

class UserNumberSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserNumber
        #fields = ['website', 'number']

class UserNumberViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = UserNumber.objects.all()
    serializer_class = UserNumberSerializer

class WebsiteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Website
        #fields = ['website', 'number']

class WebsiteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer
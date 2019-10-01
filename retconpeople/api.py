from rest_framework import serializers,viewsets
from rest_framework.reverse import reverse
from rest_framework.response import Response
from .models import Person,UserName,UserNumber,Website
from sharedstrings.models import Strings
from django.shortcuts import redirect,get_object_or_404
class PersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'description','merged_into', 'tags']

class PersonViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Person.objects.all()
    serializer_class = PersonSerializer

    def retrieve(self, request, pk=None):
        queryset = Person.objects.all()
        user = get_object_or_404(queryset, id=pk)
        
        if user.merged_into is not None and not 'noredirect' in request.GET:
            user=user.merged_into
            #redirect_url=reverse('person-detail', args=[user], request=request)
            redirect_url=reverse('person-detail', args=[user.id])
            return redirect(redirect_url,permenant=True)
        serializer = PersonSerializer(user,context={'request': request})
        return Response(serializer.data)

class UsernameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserName
        fields = ['website','name','belongs_to']

class UsernameViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = UserName.objects.all()
    serializer_class = UsernameSerializer

class UserNumberSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserNumber
        fields = ['website', 'number','belongs_to']

class UserNumberViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = UserNumber.objects.all()
    serializer_class = UserNumberSerializer

class WebsiteSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.SlugRelatedField(many=False,read_only=False,slug_field='name',queryset=Strings.objects.all())
    tld = serializers.SlugRelatedField(many=False,read_only=False,slug_field='name',queryset=Strings.objects.all())

    class Meta:
        model = Website
        fields="__all__"
        # exclude=['url']


class WebsiteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer
from rest_framework import serializers,viewsets,status
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Person,UserName,UserNumber,Website
from sharedstrings.models import Strings
from semantictags.api import TagSerializer,TagLabelSerializer
from django.shortcuts import redirect,get_object_or_404
import json

class UsernameSerializer(serializers.ModelSerializer):
    website = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='domain'
    )
    name = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='name'
    )
    class Meta:
        model = UserName
        
        fields = ['website','name','belongs_to']

class LeafUsernameSerializer(UsernameSerializer):

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
    website = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='domain'
    )
    class Meta:
        model = UserNumber
        fields = ['website', 'number','belongs_to']

class LeafUserNumberSerializer(serializers.HyperlinkedModelSerializer):
    website = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='domain'
    )
    class Meta:
        model = UserNumber
        fields = ['website', 'number']

class UserNumberViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = UserNumber.objects.all()
    serializer_class = UserNumberSerializer


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    first_name = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='name',
        queryset=Strings.objects.all()
    )

    last_name = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='name',
        queryset=Strings.objects.all()
    )

    pseudonyms = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field='name',
        queryset=Strings.objects.all()
    )

    usernames=LeafUsernameSerializer(many=True)
    user_numbers=LeafUserNumberSerializer(many=True)

    tags = TagSerializer(many=True)
    class Meta:
        model = Person
        depth=1
        fields = ['first_name', 'last_name','pseudonyms', 'description','merged_into', 'tags','usernames','user_numbers']

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


class WebsiteSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.SlugRelatedField(many=False,read_only=False,slug_field='name',queryset=Strings.objects.all())
    tld = serializers.SlugRelatedField(many=False,read_only=False,slug_field='name',queryset=Strings.objects.all())

    class Meta:
        model = Website
        fields=['name','tld','domain',"description","username_pattern","user_number_pattern","parent_site","tags"]


class WebsiteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer

    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        site = self.get_object()

        if 'owners' in request.GET:
            lnames= list(map(lambda x: (x.name.name,x.belongs_to_id),site.user_names.all()))
            lnumbers=map(lambda x: x.number,site.user_numbers.all())
            lnames.extend(lnumbers)
        else:
            lnames= list(map(lambda x: x.name.name,site.user_names.all()))
            lnumbers=map(lambda x: x.number,site.user_numbers.all())
            lnames.extend(lnumbers)
        print(lnames)
        return Response(lnames)


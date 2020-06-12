from rest_framework import serializers,viewsets,status
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.decorators import action,renderer_classes
from rest_framework.renderers import JSONRenderer
from .models import Person,UserName,UserNumber,Website
from sharedstrings.api import StringsField
from semantictags.api import TagSerializer,TagLabelSerializer
from django.shortcuts import redirect,get_object_or_404
from django.db import transaction
import json

from rest_framework import renderers


class PlainTextRenderer(renderers.BaseRenderer):
    media_type = 'text/plain'
    format = 'txt'

    def render(self, data, media_type=None, renderer_context=None):
        return data.encode(self.charset)


class UsernameSerializer(serializers.ModelSerializer):
    website = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='domain',
        queryset=Website.objects.all()
    )
    name = StringsField()
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
        read_only=False,
        slug_field='domain',
        queryset=Website.objects.all()
    )
    class Meta:
        model = UserNumber
        fields = ['website', 'number','belongs_to']
    


class LeafUserNumberSerializer(serializers.HyperlinkedModelSerializer):
    website = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='domain',
        queryset=Website.objects.all()
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
    first_name = StringsField(required=False)

    last_name = StringsField(required=False)

    pseudonyms = StringsField(many=True,required=False)


    usernames=LeafUsernameSerializer(many=True,required=False)
    user_numbers=LeafUserNumberSerializer(many=True,required=False)

    tags = TagSerializer(many=True,required=False)
    class Meta:
        model = Person
        depth=1
        fields = ['id','first_name', 'last_name','pseudonyms', 'description','merged_into', 'tags','usernames','user_numbers']
    
    def create(self, validated_data):
        # profile_data = validated_data.pop('profile')
        user = Person.objects.create(**validated_data)
        # Profile.objects.create(user=user, **profile_data)
        return user
    
    

            
    # def update(self, instance, validated_data):
    #     s_usernames = validated_data.pop('usernames')
    #     s_usernumbers = validated_data.pop('user_numbers')
    #     usernames = instance.usernames
    #     usernumbers = instance.usernumbers

    #     copy_fields= list(self.fields)
    #     list.remove('usernames')
    #     list.remove('user_numbers')

    #     #copy or update
    #     for k in copy_fields:
    #         setattr(instance,k,validated_data.get(k, getattr(instance,k)))

    #     for d in s_usernames:
    #         domain=s_usernames['website']
    #         name= s_usernames['name']

    #         instance.usernames.through.get_or_create(person=instance,website__domain=domain,name=name)

    #     instance.save()

    #     return instance
    

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
    
    @action(detail=True, methods=['get','post','delete'])
    def users(self, request, pk=None,format=None):
        
        person = self.get_object()
        
        try:
            with transaction.atomic():
                if request.method == 'GET':
                    l=[]
                    l.extend(LeafUsernameSerializer(person.usernames,many=True).data)
                    l.extend(LeafUserNumberSerializer(person.user_numbers,many=True).data)
                    return Response(l)
                elif request.method == 'POST':
                    l=request.data
                    for e in l:
                        if('name' in e):
                            u = LeafUsernameSerializer(data=e)
                            if u.is_valid(): 
                                u=u.save()
                                person.usernames.add(u)
                            else:
                                raise serializers.ValidationError()
                        else:
                            u=LeafUserNumberSerializer(data=e)
                            if u.is_valid(): 
                                u=u.save()
                                person.user_numbers.add(u)
                            else:
                                raise serializers.ValidationError()
                    person.save()
                    return Response([],status=200)
                elif request.method == 'DELETE':
                    l=request.data
                    for e in l:
                        if('name' in e):
                            u = LeafUsernameSerializer(data=e)
                            if u.is_valid(): 
                                u=UserName.objects.get(**u.validated_data)
                            person.usernames.remove(u)
                            u.delete()
                        else:
                            u = LeafUserNumberSerializer(data=e)
                            if u.is_valid(): 
                                u=UserNumber.objects.get(**u.validated_data)
                            person.usernames.remove(u)
                            u.delete()
                    person.save()
                    return Response([],status=200)
        except serializers.ValidationError as e:
            return Response([],status=401)
        except Exception as e:
            return Response([],status=501)

    def create(self, request):
        d=request.data
        if 'usernames' in d or 'user_numbers' in d:
            return Response('Please user POST /people/<pk>/users to add users after creation.',status=401)
        return super().create(request)
            


class WebsiteSerializer(serializers.HyperlinkedModelSerializer):
    name = StringsField()

    #TODO derive tld automatically in model and make this readonly
    tld = StringsField()

    class Meta:
        model = Website
        fields=['id','name','tld','domain',"description","username_pattern","user_number_pattern","parent_site","tags"]


class WebsiteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer
    renderer_classes=(JSONRenderer,PlainTextRenderer)
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None,format=None):
        site = self.get_object()
        

        if 'owners' in request.GET:
            lnames= list(map(lambda x: (x.name.name,x.belongs_to_id),site.user_names.all()))
            lnumbers=map(lambda x: x.number,site.user_numbers.all())
            lnames.extend(lnumbers)
        else:
            lnames= list(map(lambda x: x.name.name,site.user_names.all()))
            lnumbers=map(lambda x: x.number,site.user_numbers.all())
            lnames.extend(lnumbers)
        
        if format == "txt" and not 'owners' in request.GET:
            lnames= "\n".join(lnames)

            return Response(lnames)
            
        return Response(lnames)


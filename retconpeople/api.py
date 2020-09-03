from rest_framework import serializers,viewsets,status
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.decorators import action,renderer_classes
from rest_framework.renderers import JSONRenderer
from .models import Person,UserName,UserNumber,Website,UrlPattern
from sharedstrings.api import StringsField
from sharedstrings.models import Strings
from semantictags.api import TagSerializer,TagLabelSerializer
from retcon.api import RetconModelViewSet
from django.shortcuts import redirect,get_object_or_404
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import json

from rest_framework import renderers


class PlainTextRenderer(renderers.BaseRenderer):
    media_type = 'text/plain'
    format = 'txt'

    def render(self, data, media_type=None, renderer_context=None):
        return data.encode(self.charset)

class UrlPatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = UrlPattern
        fields= ['pattern']

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
    distinguish_from=serializers.HyperlinkedRelatedField(many=True,required=False,view_name='person-detail',queryset=Person.objects.all())

    class Meta:
        model = Person
        depth=1
        fields = ['id','first_name', 'last_name','pseudonyms', 'description','merged_into', 'tags','usernames','user_numbers','distinguish_from','uuid']
    
    # def create(self, validated_data):
    #     # tracks_data = validated_data.pop('tracks')
    #     # urls = validated_data.pop('urls')
    #     person = Person.objects.create(**validated_data)
    #     for track_data in urls:
            
    #         Track.objects.create(album=album, **track_data)
    #     return person
    #     # profile_data = validated_data.pop('profile')
        
    #     # Profile.objects.create(user=user, **profile_data)
    #     return person
    
    

            
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
    

class PersonViewSet(RetconModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Person.objects.all()
    serializer_class = PersonSerializer

    def create(self, request):
        d=request.data
        if 'usernames' in d or 'user_numbers' in d:
            return Response('Please user POST /people/<pk>/users to add users after creation.',status=401)
        return super().create(request)

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
    
    
    @action(detail=False, methods=['get','post'])
    def search(self, request, pk=None,format=None):
        d=request.data
        urls = d['urls'] if 'urls' in d else []
        identifiers = d['identifiers'] if 'identifiers' in d else []
        l=Person.search_by_identifiers(urls=urls,user_identifiers=identifiers)
        serializer=PersonSerializer(l,many=True)
        if len(l)>0:
            
            return Response(serializer.data,status=200)
        else:
            return Response(serializer.data,status=404)

    
    @action(detail=False,methods=['post'])
    def autocreate(self, request, pk=None,format=None):
        '''Creates a person from the given information or returns conflicting ids'''
        d=request.data
        if not ('urls' in d or 'identifiers' in d):
            r= Response({'status':'fail','message':'Body must contain urls or identifiers key'},status=400)
            return r
        
        #autocorrect a single url into a list
        if 'urls' in d and not isinstance(d['urls'],list):
            d['urls']=[d['urls']]


        urls = d['urls'] if 'urls' in d else []
        identifiers = d['identifiers'] if 'identifiers' in d else []
        allow_partial= 'allowpartial' in request.query_params and request.query_params['allowpartial'] =='1'
        try:
            serializer=None
            partial=False
            created=False
            try:
                t=Person.create_from_identifiers(user_identifiers=identifiers,urls=urls,fail_on_missing_domain= not allow_partial)
                if t==False:
                    m='No websites matching that pattern'
                    r= Response({'status':'fail','message':m},status=400)
                    return r
                else:
                    created,partial,id=t
                serializer=PersonSerializer(id)
            except Person.DuplicateIdentityError as e:
                identities=e.identities
                serializer=PersonSerializer(identities,many=True)
                return Response(serializer.data,status=409)
            except ValueError as e:
                if settings.DEBUG:
                    m=str(m)
                else:
                    m='Something about that input was wrong'
                r= Response({'status':'fail','message':m},status=400)
                return r

            if partial:
                r= Response(serializer.data,status=207)
                response.data['created'] = created
                return r

            if created:
                return Response(serializer.data,status=201)
            else:
                return Response(serializer.data,status=200)

        except ObjectDoesNotExist as e:
            return Response(str(e),status=404)
        # except NotImplementedError:
        #     return Response(status=501)
        # except Exception as e:
        #     return Response(status=500)


    @action(detail=True, methods=['get','post','delete'])
    def users(self, request, pk=None,format=None):
        
        l=request.data
        if not isinstance(l,list):
            l=[l]

        #resolve domains into sites
        #split out numbers
        #create subordinate objects
        l_usernumber=[]
        l_username=[]

        with transaction.atomic():
            master=self.get_object()
            
            for e in l:
                if 'domain' in e:
                    try:
                        w= Website.objects.get(domain=e['domain'])
                        e['website']=w
                        del e['domain']
                    except Website.DoesNotExist:
                        return Response({'status':'fail','message':'There is no website with the domain {}'.format(e['domain'])},status=status.HTTP_404_NOT_FOUND)
                try:
                    n=int(e['name'])
                    e['number']=n
                    del e['name']
                    un,created=UserNumber.objects.get_or_create(e)
                    if not created and (un.belongs_to_id is not None or un.belongs_to_id != master.id):
                        return Response({'status':'fail','message':'{}@{} in use'.format(e['number'],e['website'])},status=status.HTTP_409_CONFLICT)
                    l_usernumber.append({'id':un.id})
                except:
                    un,created=UserName.objects.get_or_create(e)
                    if not created and (un.belongs_to_id is not None or un.belongs_to_id != master.id):
                        return Response({'status':'fail','message':'{}@{} in use'.format(e['name'],e['website'])},status=status.HTTP_409_CONFLICT)
                    l_username.append({'id':un.id})
            
            subordinate_field_name='usernames'
            subordinate_field_serializer = UsernameSerializer
            subordinate_type = UserName
            r= self.generic_master_detail_list_request_handler(request, master, subordinate_field_serializer, subordinate_field_name, subordinate_type,data=l_username)
            if r.status_code !=status.HTTP_200_OK:
                return r
            subordinate_field_name='user_numbers'
            subordinate_field_serializer = UserNumberSerializer
            subordinate_type = UserNumber
            r= self.generic_master_detail_list_request_handler(request, master, subordinate_field_serializer, subordinate_field_name, subordinate_type,data=l_usernumber)
            return r
        

    @action(detail=True, methods=['get','post','delete'])
    def distinguish_from(self, request, pk=None,format=None):
        master=self.get_object()
        subordinate_field_name='distinguish_from'
        subordinate_field_serializer = PersonSerializer
        subordinate_type = Person
        return self.generic_master_detail_list_request_handler(request, master, subordinate_field_serializer, subordinate_field_name, subordinate_type)

    @action(detail=True, methods=['get','post','delete'])
    def pseudonyms(self, request, pk=None,format=None):
        master=self.get_object()
        subordinate_field_name='pseudonyms'
        subordinate_field_serializer = None
        subordinate_type = Strings
        data= [ {'name':x} for x in request.data]

        with transaction.atomic():
            #create string objects as necessary
            for d in data:
                Strings.objects.get_or_create(**d)

            return self.generic_master_detail_list_request_handler(request, master, subordinate_field_serializer, subordinate_field_name, subordinate_type,data=data)
    
    # @action(detail=True, methods=['get','post','delete'])
    # def distinguish_from(self, request, pk=None,format=None):
    #     raise NotImplementedError()

            


class WebsiteSerializer(serializers.HyperlinkedModelSerializer):
    name = StringsField()

    #TODO derive tld automatically in model and make this readonly
    tld = StringsField()

    user_id_patterns= UrlPatternSerializer(many=True)

    class Meta:
        model = Website
        fields=['id','name','tld','domain',"description","user_id_format_string","parent_site","tags","user_id_patterns"]


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
        wanted='?'
        if 'wanted' in request.GET:
            if request.GET['wanted']=='0':wanted=False
            if request.GET['wanted']=='1':wanted=True
            if request.GET['wanted']=='unset':wanted=None

        if wanted =='?':
            name_set = site.user_names.all()
            number_set = site.user_numbers.all()
        else:
            name_set = site.user_names.filter(wanted=wanted)
            number_set = site.user_numbers.filter(wanted=wanted)

        if 'owners' in request.GET:
            lnames= list(map(lambda x: (x.name.name,x.belongs_to_id),name_set))
            lnumbers=map(lambda x: x.number,number_set)
            lnames.extend(lnumbers)
        else:
            lnames= list(map(lambda x: x.name.name,name_set))
            lnumbers=map(lambda x: x.number,number_set)
            lnames.extend(lnumbers)
        
        if format == "txt" and not 'owners' in request.GET:
            #BUG this breaks if names and numbers are mixed 
            lnames= "\n".join(lnames)

            return Response(lnames)
            
        return Response(lnames)


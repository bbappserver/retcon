from django.db import models
import datetime
from dateutil import tz
# Create your models here.
# class URLScheme(models.model):
#     name=models.CharField(max_length=16)
# class Hostname(models.model):
#     name=models.CharField(max_length=16)

class MergeError(ValueError):
    '''
    The merge failed, will contain a list of fields that field to merge and reasons.
    '''
    pass

class ImportableModelProtocol():
    @classmethod
    def import_from_dict(cls,d:dict):
        created,m=cls.get_or_create_from_dict(d)
        if created:
            return m
        else:
            if m.merge(d):
                return m

    @classmethod
    def get_or_create_from_dict(cls,d:dict,do_fuzzy=True):
        try:
            m=cls.get_with_alternate_keys(d)
        except cls.DoesNotExist:
            m=None
        if m:
            return (False,m)
        elif do_fuzzy:
            
            m= cls.fuzzy_get_from_dict(d)
            if m:
                return (False,m)
            else:
                return (True,cls.create_from_dict(d))
        else:
            return (True,cls.create_from_dict(d))
        


    @classmethod
    def fuzzy_get_from_dict(cls,d:dict):
        '''
        Gets the item that corresponds to the item with all of the given keys.
        If multiple candiadates raises Ambiguous.
        To just retrieve all possible use fuzy_filter_from_dict()

        Default implementation just checks for count(fuzzy_filter) len >1 this is pretty inefficient
        It is advised that you also override this in your subclass
        TODO can we make it raise not exists like the django builitn?, otherwise return None
        '''
        res=cls.fuzzy_filter_from_dict(d)
        if res is None:
            return None
        n=res.count()
        if n > 1:
            raise models.Model.MultipleObjectstReturned()
        elif n == 1:
            return res[0]
        else:
            return None

    # @classmethod
    # @abstractmethod
    # def fuzzy_filter_from_dict(cls,d:dict):
    #     raise NotImplementedError()
    
    @classmethod
    def direct_indirect_keys(cls):
        direct=set()
        indirect=set()
        for f in cls._meta.get_fields():
            if isinstance(f,models.fields.related.ManyToManyField) or isinstance(f,models.fields.ForeignKey):
                indirect.add(f.name)
            else:
                direct.add(f.name)
        return (direct,indirect)
        
    @classmethod
    def direct_indirect_dict(cls,d):
        dk,ik=cls.direct_indirect_keys()
        ddict={}
        idict={}
        for k in d:
            if k in dk:
                ddict[k]=d[k]
            elif k in ik:
                idict[k]=d[k]
            else:
                raise KeyError('Named key "{}" does not describe an object field, did your remember to convert it?'.format(k))

    @classmethod
    #@abstractmethod
    def decode_non_foreign_dict_fields(cls,d:dict):
        '''
        Sometimes a dictionary format contains multiple keys that do not refer to a foreing object but also don't nicely
        map right to a value, implment this method to preprocess values in d into keys the model constructor can accept.'''
        
    @classmethod
    def create_from_dict(cls, d:dict):
        '''
        Works the same as the constructor except it saves imediately and creates subordinate models.
        '''
        exception=None
        d=dict(d)
        with transaction.atomic():
            try:
                d=cls.create_foreign_objects_from_dict(d)
                d=cls.decode_non_foreign_dict_fields(d)
                dd,di=cls.direct_indirect_dict(d)
                m=cls(**dd)
                m.save()
                for k in di:
                    related_manager=getattr(m,k)
                    for x in di[k]:
                        related_manager.add(x)
                return m
            except Exception as e:
                exception=e
        raise exception
    
    @classmethod
    def create_foreign_objects_from_dict(cls,d:dict):
        for f in cls._meta.get_fields():
            if isinstance(f,models.fields.related.ManyToManyField):
                name=f.name
                field_class=f.related_model
                if name in d:
                    l=[]
                    for x in d[name]:
                        l.append(field_class.get_or_create_from_dict(x))
                    d[name]=l
                    
            elif isinstance(f,models.fields.ForeignKey):
                name=f.name
                field_class=f.related_model
                if name in d:
                    d[name]=field_class.get_or_create_from_dict(x)
        return d


        '''
        Calls super().create_foreign_objects_from_dict(), to recursivly add foreign objects
        in each superclass, then add objects for this class.
        '''
        return super().create_foreign_objects_from_dict(d)



    @classmethod
    #@abstractmethod
    def get_with_alternate_keys(cls, d:dict):
        '''
        Gets the object with alternate keys named in the dictionary, if multiple items raises models.FoundMultiple
        '''

    #@abstractmethod
    def merge(self,d : dict, overwritable_fields=[]):
        '''
        Will attempt to merge the given dictionary with the given dictionary.
        Field names in overwritable fields will be overwritten without error.
        If field is not blank and not overwritable but is replaced by d, a MergeError will be raised.
        '''
        raise NotImplementedError()

class Resource(models.Model,ImportableModelProtocol):
    url= models.CharField(max_length=2000)
    added_at= models.DateTimeField(auto_now=True)

    #The cache vaidity period usually provided by the webserver, null for indefinite
    valid_until =  models.DateTimeField(null=True,blank=True) 
    
    class Meta:
        abstract=True
    
    def __str__(self):
        return "{} {}".format(self.url,self.added_at)

class ContentResource(Resource):
    '''URLs which serve content often intended to remain the same for long periods of time or indefinitely'''
    content_last_modified = models.DateTimeField(null=True,blank=True)

    #This field should not be updated unless the cotnent was fully fetched, that way entities which need to 
    #reference the entity thes resource represents can be expnaded without needing to full expand this resource.
    content_last_fetched = models.DateTimeField(null=True,blank=True)

    @property
    def is_cache_valid(self):
        if self.valid_until is None:
            return True
        else:
            local = tz.gettz()
            now=datetime.datetime.now(tz=local)
            return now < self.valid_until

# class HTTPResource(ContentResource):
#     http_verbs={"GET":0,"POST":1}
#     verb = models.PositiveSmallIntegerField(default=0,choices=http_verbs)
#     request_body= models.CharField(max_length=2000,help_text="Body text to be sent,usually used to perform a post")

class EphemeralResource(Resource):
    '''Lots of URLS are temporary tokens valid for a short period put those here.
    If you aren't sure whether something is ephemeral use a contentURL as ephemeralURLS may be garbage collected.
    If the protocol gives a long cache interval for the response it probably means that the response is a ContentURL not
    an ephemeral URL. (e.g. Cache-Control:max-age=360000'''
    pass

# class RemoteEntity(models.model):
#     '''Particular metadata about an entity a URL represents'''
#     source_posted= models.DateTimeField(null=True)

# class DynamicRemoteEntity(RemoteEntity):
#     '''Lots of entities are not static, for non static entities use this'''
#     
#     local_created= models.DateTimeField(auto_now_add=True)
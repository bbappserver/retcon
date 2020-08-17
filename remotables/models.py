from django.db import models
import datetime
from dateutil import tz
# Create your models here.
# class URLScheme(models.model):
#     name=models.CharField(max_length=16)
# class Hostname(models.model):
#     name=models.CharField(max_length=16)

class Resource(models.Model):
    url= models.CharField(max_length=2000,help_text="The url without any percent notation characters or plus substitutions of spaces")
    added_at= models.DateTimeField(auto_now=True)

    #The cache vaidity period usually provided by the webserver, null for indefinite
    valid_until =  models.DateTimeField(null=True,blank=True) 
    
    class Meta:
        abstract=True
    
    def __str__(self):
        return "{} {}".format(self.unescaped_url,self.added_at)

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
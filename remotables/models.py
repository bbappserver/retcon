from django.db import models

# Create your models here.
# class URLScheme(models.model):
#     name=models.CharField(max_length=16)
# class Hostname(models.model):
#     name=models.CharField(max_length=16)

class Resource(models.Model):
    unescaped_url= models.CharField(max_length=2000,help_text="The url without any percent notation characters or plus substitutions of spaces")
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
    content_last_fetched = models.DateTimeField(null=True,blank=True)

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
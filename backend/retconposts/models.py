from django.db import models
from retconpeople.models import Person,Website,UserName,UserNumber
from semantictags.models import Taggable
import json
import re
# Create your models here.
class Post(Taggable):
    website = models.ForeignKey("retconpeople.Website",on_delete=models.PROTECT,related_name='posts')
    poster = models.ForeignKey("retconpeople.Person",on_delete=models.PROTECT,related_name='posts')
    raw_body = models.TextField(null=True,blank=True,editable=False)
    json_body = models.TextField(null=True,blank=True,editable=False)
    url = models.ForeignKey("remotables.ContentResource",on_delete=models.PROTECT)
    title = models.CharField(null=True,blank=True,editable=False,max_length=256)
    timestamp= models.DateTimeField(null=True,blank=True,editable=False)
    attachements = models.ForeignKey("retconstorage.Collection",on_delete=models.PROTECT,related_name='posts')

    def set_poster_by_name_and_domain(self,name,domain):
        self.poster = UserName.get(website__domain=domain,name__name=name)
    
    @property
    def plain_description(self):
        '''Assumes the description is html and strips tags'''
        body=self.description
        return re.sub('<[^>]+>',"",body)
    
    @property
    def description(self,key='description'):
        '''Convenience method for json.losads(post.json_body)['description'], caches JSON load'''
        return self.parse()[key]
    
    @property
    def post_id(self,key='post_id'):
        '''Convenience method for json.losads(post.json_body)['post_id'], caches JSON load'''
        return self.parse()[key] 
    
    @property
    def remote_poster_id(self,key='poster_id',allow_fallback=True):
        '''
        Convenience method for json.loads(post.json_body)['poster_id'], caches JSON load
        May fallback to Username.object.get(website=self.website,belongs_to=self.poster)
        '''
        try:
            return self.parse()[key] 
        except KeyError:
            if not allow_fallback:
                return None
            try:
                username=UserName.objects.get(website=self.website,belongs_to=self.poster)
                return username.name.name
            except UserName.NotFound:
                try:
                   return UserNumber.objects.get(website=self.website,belongs_to=self.poster)
                except Exception:
                    return None

    def parse(self):
        '''Some parts of posts are intentionally stored as JSON and not indexed,because there is no usecase for that
        Parse is run before getting those fields that are just in the JSON body.
        '''
        self._json_dict = json.loads(self.json_body)
        return self._json_dict

# class UsernameSubscription(models.Model):
#     '''Stores the timestamp of the last time data for this user was fetched
#     This should on be updated after all new posts have been saved, and should 
#     not be set to now(), because servers do not necessarily erve new posts immediately.
#     It is recommended that this should be at least 5 minutes earlier than now.
#     '''
#     username=models.ForeignKey("retconstrorage.Username",on_delete=models.PROTECT)
#     latestTimestamp = models.DateTimeField(null=True)

#     def bump(self):
#         pass
#         #self.latestTimestamp=time.now()-3600

# class UsernumberSubscription(models.Model):
#     usernumber=models.ForeignKey("retconstrorage.Usernumber",on_delete=models.PROTECT)
#     latestTimestamp =models.DateTimeField(null=True)
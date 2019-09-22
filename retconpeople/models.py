from django.db import models
from sharedstrings import models as sharedstrings
from semantictags import models as semantictags
# Create your models here.
# class Strings(models.Model):
#     id = models.AutoField(primary_key=True)
#     name = models.CharField()

class Website(models.Model):
    id = models.AutoField(primary_key=True)
    parent_site = models.ForeignKey("self",on_delete=models.DO_NOTHING,null=True,blank=True,related_name="child_sites")
    domain= models.CharField(max_length=256)
    name = models.ForeignKey("sharedstrings.Strings",related_name="+",on_delete=models.DO_NOTHING)
    tld = models.ForeignKey("sharedstrings.Strings",related_name="+",on_delete=models.DO_NOTHING)
    description=models.CharField(max_length=255)
    username_pattern=models.CharField(null=True,blank=True,max_length=1024)
    user_number_pattern=models.CharField(null=True,blank=True,max_length=1024)
    tags=models.ManyToManyField("semantictags.Tag",related_name="+",blank=True)

    def substitute_username_pattern(self,args):
        raise NotImplementedError()
    def substitute_user_number_pattern(self,args):
        raise NotImplementedError()

    def __str__(self):
        return "{} ({})".format(self.name,self.domain)

class Person(models.Model):
    id = models.AutoField(primary_key=True)
    first_name=models.ForeignKey("sharedstrings.Strings",related_name="+",on_delete=models.DO_NOTHING,null=True,blank=True)
    last_name=models.ForeignKey("sharedstrings.Strings",related_name="+",on_delete=models.DO_NOTHING,null=True,blank=True)
    pseudonyms = models.ManyToManyField("sharedstrings.Strings",related_name="+",blank=True)
    description=models.CharField(max_length=255,blank=True)
    merged_into=models.ForeignKey("self",related_name="merges_from",on_delete=models.DO_NOTHING,null=True,blank=True)
    tags=models.ManyToManyField("semantictags.Tag",related_name="+",blank=True)

    def get_usernames(self):
        raise NotImplementedError()
        l=[]
        for c in self._collect_children():
            l.append(c.usernames)
        return l

    def _collect_children(self):
        l=[]
        for c in self.merges_from:
            l.append(c._collect_children())
            l.append(c)
        l.append(self)
        return l
        
    def _merge_into(self,target):
        if self.merged_into is None:
            self.merged_into = target
        else:
            raise ValueError("Merge cannot be performed because this model is already merged")

    def merge_with(self,target):
        if target.id < self.id: 
            self._merge_into(target)
        else:
            target._merge_into(self)
        
        target.save(update_fields=['merged_into'])
    
    def save(self, *args, **kwargs):
        # Check how the current values differ from ._loaded_values. For example,
        # prevent changing the creator_id of the model. (This example doesn't
        # support cases where 'creator_id' is deferred).
        if merged_into != self._loaded_values['merged_into'] and merged_into is not None:
            raise ValueError("Altering merge target not supporte")
        super().save(*args, **kwargs)
#Todo person manager for getting only canonical person

class UserName(models.Model):
    id = models.AutoField(primary_key=True)
    website=models.ForeignKey("Website",related_name="user_names",on_delete=models.DO_NOTHING)
    name = models.ForeignKey("sharedstrings.Strings",related_name="+",on_delete=models.DO_NOTHING)
    tags=models.ManyToManyField("semantictags.Tag",related_name="+")
    belongs_to=models.ForeignKey("Person",related_name='usernames',on_delete=models.DO_NOTHING,null=True,blank=True)

    def get_url(self):
        raise NotImplementedError()

    class Meta:
        unique_together = ['website', 'name']

class UserNumber(models.Model):
    id = models.AutoField(primary_key=True)
    website=models.ForeignKey("Website",related_name="user_numbers",on_delete=models.DO_NOTHING)
    number = models.BigIntegerField()
    belongs_to=models.ForeignKey("Person",related_name='user_numbers',on_delete=models.DO_NOTHING,null=True,blank=True)

    class Meta:
        unique_together = ['website', 'number']
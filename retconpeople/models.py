from django.db import models
from django.core.exceptions import ValidationError
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
    merged_into=models.ForeignKey("self",related_name="merged_from",on_delete=models.DO_NOTHING,null=True,blank=True)
    tags=models.ManyToManyField("semantictags.Tag",related_name="+",blank=True)

    canonicalize=False

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
    
    def clean(self):

        #Cheap test first, aways need to do, doesn't hit db
        if self.merged_into_id is not None:
            if self.merged_into_id == self.id:
                raise ValidationError({'merged_into': ('Cannot merge into self')})
            if self.merged_into.merged_into.id is not None:
                raise ValidationError({'merged_into': ('Cannot merge into merged object')})

        if self.pk is not None:
            #this is an update
            if self.merged_into is not None:
                #django normally updates without select, but we need to select
                current = Person.objects.get(id=self.id)
                if  current.merged_into_id is not None:
                    if not self.canonicalize and  (current.merged_into_id !=self.merged_into_id):
                        raise ValidationError({'merged_into': ('Changing merge target violates integrity.')})
                    else:
                        #Do a long scan for the current name
                        target=self
                        visited=[]
                        while target.merged_into_id is not None:
                            visited.append(target.id)

                            #check both current and next id so we don't have to do unnecessary fetch
                            if target.id in visited or target.merged_into_id in visited:
                                raise ValidationError({'merged_into': ('Cycle detected:{}'.format(visited))})
                            target = target.merged_into
                        self.merged_into_id=target.id



    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

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
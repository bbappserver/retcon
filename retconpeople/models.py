from django.db import models
from sharedstrings import models as sharedstrings
from semantictags import models as semantictags
# Create your models here.
# class Strings(models.Model):
#     id = models.AutoField(primary_key=True)
#     name = models.CharField()

class Website(models.Model):
    id = models.AutoField(primary_key=True)
    domain= models.CharField(max_length=256)
    name = models.ForeignKey("sharedstrings.Strings",related_name="+",on_delete=models.DO_NOTHING)
    tld = models.ForeignKey("sharedstrings.Strings",related_name="+",on_delete=models.DO_NOTHING)
    description=models.CharField(max_length=255)
    user_name_pattern=models.CharField(null=True,max_length=1024)
    user_number_pattern=models.CharField(null=True,max_length=1024)
    tags=models.ManyToManyField("semantictags.Tag",related_name="+")

class Person(models.Model):
    id = models.AutoField(primary_key=True)
    first_name=models.ForeignKey("sharedstrings.Strings",related_name="+",on_delete=models.DO_NOTHING,null=True)
    last_name=models.ForeignKey("sharedstrings.Strings",related_name="+",on_delete=models.DO_NOTHING,null=True)
    pseudonyms = models.ManyToManyField("sharedstrings.Strings")
    description=models.CharField(max_length=255)
    merged_into=models.ForeignKey("self",related_name="merges_from",on_delete=models.DO_NOTHING,null=True)
    tags=models.ManyToManyField("semantictags.Tag",related_name="+")

    def get_usernames(self):
        raise NotImplementedError()
        l=[]
        for c in self._collect_children():
            l.append(c.usrnames)
        return l

    def _collect_children(self):
        l=[]
        for c in self.merges_from:
            l.append(c._collect_children())
            l.append(c)
        l.append(self)
        return l


class Username(models.Model):
    id = models.AutoField(primary_key=True)
    website=models.ForeignKey("Website",related_name="user_names",on_delete=models.DO_NOTHING)
    name = models.ForeignKey("sharedstrings.Strings",related_name="+",on_delete=models.DO_NOTHING)
    tags=models.ManyToManyField("semantictags.Tag",related_name="+")

    def get_url(self):
        raise NotImplementedError()

class UserNumber(models.Model):
    id = models.AutoField(primary_key=True)
    website=models.ForeignKey("Website",related_name="user_numbers",on_delete=models.DO_NOTHING)
    name = models.ForeignKey("sharedstrings.Strings",related_name="+",on_delete=models.DO_NOTHING)

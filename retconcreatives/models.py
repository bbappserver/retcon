from django.db import models
from sharedstrings import models as sharedstrings
# Create your models here.

class Studio(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.ForeignKey("sharedstrings.Strings",related_name="+",on_delete=models.DO_NOTHING)
    case_sensitive_name = models.BooleanField()

    parent_studio=models.ForeignKey("self",on_delete=models.DO_NOTHING,null=True)
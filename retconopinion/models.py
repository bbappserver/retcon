from django.db import models
from django.conf import settings
# Create your models here.


class UserOpinion(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="+"
    )
    like = models.BooleanField(blank=True, null=True, default=None)
    tags = models.ManyToManyField("semantictags.Tag",blank=True,related_name="+")
    class Meta:
        abstract=True


class UserPersonOpinion(UserOpinion):
    '''Represents a user's opinion of a person'''

    person = models.ForeignKey(
        "retconpeople.Person",
        on_delete=models.CASCADE,
    )

class UserCompanyOpinion(UserOpinion):
    '''Represents a user's opinion of a company'''

    person = models.ForeignKey(
        "retconcreatives.Company",
        on_delete=models.CASCADE,
    )

class UserCreativeWorkOpinion(UserOpinion):
    '''Represents a user's opinion of a CreativeWork'''

    person = models.ForeignKey(
        "retconcreatives.CreativeWork",
        on_delete=models.CASCADE,
    )

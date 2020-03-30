from django.db import models

# Create your models here.
class Post(models.Model):
    website = models.ForeignKey("retconpeople.Website",on_delete=models.PROTECT)
    person = models.ForeignKey("retconpeople.Person",on_delete=models.PROTECT)
    body = models.TextField()
    url = models.ForeignKey("remotables.ContentUrl",on_delete=models.PROTECT)
    attachements = models.ForeignKey("retconstorage.Collection",on_delete=models.PROTECT)

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
from django.test import TestCase
from rest_framework import status,test
from retcon.test.CRUDTest import CRUDTest
from .models import ContentResource,EphemeralResource
import datetime,django.db
from dateutil import tz
# Create your tests here.

class TestResourceCRUD(CRUDTest):

    def testCreateEphemeralResource(self):
        '''This test runs first since an ephemeral resource is just a concrete resource'''
        EphemeralResource(url='http://www.twitter.com/username/1234',valid_until=None).save()
    
    def testCreateContentResource(self):
        local = tz.gettz()

        # with self.assertRaises():
        c=ContentResource(url='http://www.twitter.com/username/1234',valid_until=None)
        c.save()
        with self.assertRaises(django.db.IntegrityError):
            #this should be imva;id because the url is duplicated
            c=ContentResource(url='http://www.twitter.com/username/1234',valid_until=None)
            c.save()
        c=ContentResource(url='http://www.twitter.com/username/12345',valid_until=None,content_last_fetched='1961-01-01 00:00:01+0000')
        c.save()
        c=ContentResource(url='http://www.twitter.com/username/12346',valid_until=None,content_last_modified='1961-01-01 00:00:01+0000')
        c.save()
        c=ContentResource(url='http://www.twitter.com/username/12347',valid_until=None,content_last_modified=datetime.datetime.now(tz=local))
        c.save()
    
    def testIsContentValid(self):
        local = tz.gettz()
        delta = datetime.timedelta(days=1)
        soon=datetime.datetime.now(tz=local)+delta
        c=ContentResource(url='http://www.twitter.com/username/1234',valid_until=None)
        self.assertTrue(c.is_cache_valid)
        c=ContentResource(url='http://www.twitter.com/username/1234',valid_until=soon)
        self.assertTrue(c.is_cache_valid)
        c=ContentResource(url='http://www.twitter.com/username/1234',valid_until='1961-01-01 00:00:01+0000')
        self.assertFalse(c.is_cache_valid)


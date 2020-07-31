from django.test import TestCase
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from rest_framework import test as rsttest
from .models import Series,Episode
# Create your tests here.

def create_series(d, parent):
        s=Series(**d)
        s.parent_series=parent
        s.save()
        return s

class SeriesEpisodeCRUDTestCase(TestCase):

    def setUp(self):
        d={
            "name":"parent",
            "published_on":"2000-01-01",
            "published_on_precision":"y",

            "created_by":None,


            "parent_series":None,

            "medium":Series.CARTOON
        }
        self.ps=create_series(d, None)
    
    def test_create(self):
        d={
            "name":"child",
            "published_on":"2000-01-01",
            "published_on_precision":"y",
            "created_by":None,
            "medium":Series.CARTOON
        }
        
        parent=None
        with self.subTest(parent=None):
            create_series(d, parent)
        
        parent=self.ps
        with self.subTest(parent=self.ps):
            create_series(d, parent)

        
    
    def test_fail_update_cyclic_parent(self):
        with self.assertRaises(IntegrityError):
            self.ps.parent_series=self.ps
            self.ps.save()

    # def test_retrieve(self):
    #     series.get()
    
    # def test_update(self):
    #     raise NotImplementedError()
    
    def test_destroy(self):
        raise NotImplementedError()
    def test_fail_destroy_parent(self):
        with self.assertRaises(ProtectedError):
            d={
                "name":"child",
                "published_on":"2000-01-01",
                "published_on_precision":"y",
                "created_by":None,
                "medium":Series.CARTOON
            }
            parent=self.ps
            create_series(d, parent)
            parent.delete()

    

class SeriesEpisodeAPICRUDTestCase(rsttest.APITestCase):
    
    
    def default_child(self):
        return {
                "name":"parent",
                "published_on":"2000-01-01",
                "published_on_precision":"y",

                "created_by":None,


                "parent_series":self.ps,

                "medium":Series.CARTOON
            }
    def setUp(self):
        d={
            "name":"parent",
            "published_on":"2000-01-01",
            "published_on_precision":"y",

            "created_by":None,


            "parent_series":None,

            "medium":Series.CARTOON
        }
        self.ps=create_series(d, None)
        
    def test_retrive_simple(self):
        raise NotImplementedError()
    
    def test_retrive_with_attributes(self):
        raise NotImplementedError()

        
    def test_create_child(self):
        self.post(self.default_child())
    def test_create_with_urls(self):
        raise NotImplementedError()
    def test_create_with_urls(self):
        raise NotImplementedError()
    def test_create_with_files(self):
        raise NotImplementedError()
    def test_create_with_publishers(self):
        raise NotImplementedError()
    def test_create_with_author(self):
        raise NotImplementedError()
    def test_create_with_produce(self):
        raise NotImplementedError()
    def test_create_with_related(self):
        raise NotImplementedError()
    def test_create_with_all_attributes(self):
        raise NotImplementedError()
        
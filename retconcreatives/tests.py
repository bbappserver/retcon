from django.test import TestCase
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from rest_framework import test as rsttest
from rest_framework import status
from retcon.test.CRUDTest import APICRUDTest
from retconpeople.models import Person
from .models import Series,Episode,Company
from retconstorage.models import ManagedFile
from remotables.models import ContentResource
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
        d={
            "name":"child",
            "published_on":"2000-01-01",
            "published_on_precision":"y",
            "created_by":None,
            "medium":Series.CARTOON
        }
        
        parent=None
        s=create_series(d, parent)
        s.delete()
        
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

    

class SeriesEpisodeAPICRUDTestCase(APICRUDTest):
    
    
    def default_child(self):
        return {
                "name":"parent",
                "published_on":"2000-01-01",
                "published_on_precision":"y",

                "created_by":None,


                "parent_series":self.ps.id,

                "medium":Series.CARTOON
            }
    def setUp(self):
        super().setUp()
        self.client.force_login(user=self.superUser)
        d={
            "name":"parent",
            "published_on":"2000-01-01",
            "published_on_precision":"y",

            "created_by":None,


            "parent_series":None,

            "medium":Series.CARTOON
        }
        self.ps=create_series(d, None)
        self.default_company=Company(name='ACME INC.')
        self.default_company.save()
        
    def test_retrive_simple(self):
        response=self.client.post('/api/series/',self.default_child(),format='json')
        id=int(response.json()['id'])
        self.client.get('/api/series/{}'.format(id),format='json')
    
    # def test_retrive_with_attributes(self):
    #     d=self.default_child()
    #     response = self.create_with_all_attributes(d)
    #     id=int(response.json()['id'])
    #     self.client.get('/api/series/{}/'.format(id),format='json')

        
    def test_create_child(self):
        d=self.default_child()
        response=self.client.post('/api/series/',d,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED,msg=response.content)
        self.assertDictContainsSubset(d,response.json())
    
    def test_create_with_urls(self):
        d=self.default_child()
        urls=['http://www.twitter.com/user/123','http://www.twitter.com/user/124']
        d['external_representation']=[ {'url':u} for u in urls ]
        response=self.client.post('/api/series/',d,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED,msg=response.content)
        id=int(response.json()['id'])
        response=self.client.get('/api/series/{}/'.format(id),format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK,msg=response.content)
    
        rd=response.json()
        self.assertCoverFilteredDict(d,rd,['external_representation'])
        for x in rd['external_representation']:
            self.assertIn(x['url'],urls)

    def test_create_with_files(self):
        d=self.default_child()
        hexstr='1234567890abcdef'
        files_unhex=[{'sha256':bytes.fromhex(hexstr)}]
        files=[{'sha256':hexstr}]
        file_ids=[x.id for x in self._create_files(files_unhex)]
        d['files']=files
        response=self.client.post('/api/series/',d,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED,msg=response.content)
        id=int(response.json()['id'])
        response=self.client.get('/api/series/{}/'.format(id),format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK,msg=response.content)

        rd=response.json()
        self.assertCoverFilteredDict(d,rd,['id'])
        for x in rd['files']:
            self.assertEqual(x['sha256'],hexstr)
    
    def test_get_producer(self):
        c=self.default_company
        d=self.default_child()
        response=self.client.post('/api/series/',d,format='json')
        id=response.json()['id']
        s=Series.objects.get(id=id)
        s.produced_by.add(c)
        s.save()
        response=self.client.get('/api/series/{}/producers/'.format(id),format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        rd=response.json()
        for x in rd:
            self.assertEqual(x['name'],c.name.name)
    def test_add_producer(self):
        c=self.default_company
        d=self.default_child()
        response=self.client.post('/api/series/',d,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        id=response.json()['id']
        response=self.client.post('/api/series/{}/producers/'.format(id),data=[{'id':c.id}],format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        s=Series.objects.get(id=id)
        self.assertEqual(s.produced_by.all()[0].id,c.id)
        
    def test_remove_producer(self):
        #add
        c=self.default_company
        d=self.default_child()
        response=self.client.post('/api/series/',d,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        id=response.json()['id']
        response=self.client.post('/api/series/{}/producers/'.format(id),data=[{'id':c.id}],format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        #remove
        response=self.client.delete('/api/series/{}/producers/'.format(id),data=[{'id':c.id}],format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        s=Series.objects.get(id=id)
        self.assertEqual( s.produced_by.count(),0)

        

    
    #TODO all wrong, creation should be with primary keys only for most subordinate resources.
    # def test_create_with_publishers(self):
    #     d=self.default_child()
    #     publishers = [{'name':'megacorp','case_sensitive_name':False},{'name':'megacorp2','case_sensitive_name':False}]
    #     d['published_by']= publishers
    #     response=self.client.post('/api/series/',d,format='json')
    #     self.assertEqual(response.status_code,status.HTTP_201_CREATED,msg=response.content)
    #     id=int(response.json()['id'])
    #     response=self.client.get('/api/series/{}/'.format(id),format='json')
    #     self.assertEqual(response.status_code,status.HTTP_200_OK,msg=response.content)

    #     rd=response.json()
    #     self.assertCoverFilteredDict(d,rd,['id','published_by'])
    #     for x in rd['published_by']:
    #         self.assertIn(x['name'],['megacorp','megacorp2'])

    # def test_create_with_author(self):
    #     d=self.default_child()
    #     d['created_by']={'first_name':'megacorp'}
    #     response=self.client.post('/api/series/',d,format='json')
    #     self.assertEqual(response.status_code,status.HTTP_201_CREATED,msg=response.content)
    #     id=int(response.json()['id'])
    #     response=self.client.get('/api/series/{}/'.format(id),format='json')
    #     self.assertEqual(response.status_code,status.HTTP_200_OK,msg=response.content)

    #     rd=response.json()
    #     self.assertCoverFilteredDict(d,rd,ignored_keys=['created_by'])
    #     self.assertCoverFilteredDict(d['created_by'],rd['created_by'])

    # def test_create_with_producer(self):
    #     d=self.default_child()
    #     producers = [{'name':'megacorp','case_sensitive_name':False},{'name':'megacorp2','case_sensitive_name':False}]
    #     d['produced_by']=producers
    #     response=self.client.post('/api/series/',d,format='json')
    #     self.assertEqual(response.status_code,status.HTTP_201_CREATED,msg=response.content)
    #     id=int(response.json()['id'])
    #     response=self.client.get('/api/series/{}/'.format(id),format='json')
    #     self.assertEqual(response.status_code,status.HTTP_200_OK,msg=response.content)

    #     rd=response.json()
    #     self.assertCoverFilteredDict(d,rd,['id','produced_by'])
    #     for x in rd['produced_by']:
    #         self.assertIn(x['name'],['megacorp','megacorp2'])

    # def test_create_with_all_attributes(self):
    #     d=self.default_child()
    #     response = self.create_with_all_attributes(d)
    #     self.assertEqual(response.status_code,status.HTTP_201_CREATED,msg=response.content)
    #     id=int(response.json()['id'])
    #     response=self.client.get('/api/series/{}/'.format(id),format='json')
    #     self.assertEqual(response.status_code,status.HTTP_200_OK,msg=response.content)
        
    #     rd=response.json()
    #     self.assertCoverFilteredDict(d,rd,['id','produced_by','published_by','created_by','external_representation'])
    #     for x in rd['produced_by']:
    #         self.assertIn(x['name'],['megacorp','megacorp2'])
    #     for x in rd['published_by']:
    #         self.assertIn(x['name'],['megacorp','megacorp2'])
    #     self.assertCoverFilteredDict(d['created_by'],rd['created_by'])
        

    # def create_with_all_attributes(self, d):
    #     d['created_by']={'first_name':'megacorp'}
    #     d['published_by']=[{'name':'megacorp'},{'name':'megacorp2'}]
    #     d['produced_by']=[{'name':'megacorp'}]
    #     d['external_representation']=[
    #         {'url':'http://www.twitter.com/user/123'},
    #         {'url':'http://www.twitter.com/user/124'}]
    #     response=self.client.post('/api/series/',d,format='json')
    #     return response
    
    # def test_create_destroy_with_all_attributes(self):
    #     d=self.default_child()
    #     response = self.create_with_all_attributes(d)
    #     self.assertEqual(response.status_code,status.HTTP_201_CREATED,msg=response.content)
    #     id=int(response.json()['id'])
    #     response=self.client.get('/api/series/{}/'.format(id),format='json')
    #     self.assertEqual(response.status_code,status.HTTP_200_OK,msg=response.content)
    #     self.client.delete('/api/series/{}/'.format(id),format='json')
    #     self.assertEqual(response.status_code,status.HTTP_200_OK,msg=response.content)
    #     response=self.client.get('/api/series/{}'.format(id),format='json')
    #     self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND,msg=response.content)

    def _create_files(self,dicts):
        for d in dicts:
            o=ManagedFile(**d)
            o.save()
            yield o
    
    def _create_companies(self,dicts):
        for d in dicts:
            o=Company(**d)
            o.clean()
            o.save()
            yield o
    
    def _create_urls(self,dicts):
        for d in dicts:
            o=ContentResource(**d)
            o.save()
            yield o
    
    def _create_people(self,dicts):
        for d in dicts:
            o=Person(**d)
            o.save()
            yield o
        
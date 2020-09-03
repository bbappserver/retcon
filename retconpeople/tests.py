from django.test import TestCase
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from rest_framework import test as rsttest
from rest_framework import status,response
from retcon.test.CRUDTest import APICRUDTest
from retconpeople.models import Person,Website,UserName,UserNumber,UrlPattern
from retconcreatives.models import Series,Episode,Company
from retconstorage.models import ManagedFile
from remotables.models import ContentResource
# Create your tests here.

class PersonCrudTest():
    pass

class PersonModelMethods(TestCase):
    pass


class PersonAPICrudTest(APICRUDTest):

    def setUp(self):
        super().setUp()
        self.client.force_login(user=self.superUser)
        #other setup here
    
    def defaultPersonDict(self):
        return {
            'first_name':'A',
            'last_name':'1',
            'description':'A human'
        }
    def defaultUsernameDict(self):
        return {'domain':'twitter.com','name':'someuser'}
    def defaultURLDict(self):
        return {'url':'ttp://www.somesite.com/person/1'}

    def defaultWebsiteDict(self):
        return {
            'domain':'twitter.com',
            'description':'the premier mircroblogging website'
        }
    def defaultTagDict(self):
        return {}

    def createDefaultPerson(self) -> Person:
        p=Person(**self.defaultPersonDict())
        p.save()
        return p
    def createDefaultWebsite(self) -> Website:
        p=Website(**self.defaultWebsiteDict())
        p.save()
        return p

    def createDefaultPersonAPI(self) -> response.Response:
        url='/api/people/'
        return self.client.post(url,data=self.defaultPersonDict(),format='json')

    def testPersonCreate(self):
        r=self.createDefaultPersonAPI()
        self.assertEqual(r.status_code,status.HTTP_201_CREATED,r.json())
        self.assertDictContainsSubset(self.defaultPersonDict(),r.json())

    def testPersonUpdate(self):
        p=self.createDefaultPerson()
        pid=p.id
        d={
            'first_name':'B',
            'last_name':'2',
            'description':'A vogon'
        }
        r=self.client.patch('/api/people/{}/'.format(pid),data=d,format='json')
        self.assertEqual(r.status_code,status.HTTP_200_OK)
        p.refresh_from_db()
        self.assertEqual(str(p.first_name),'B')
        self.assertEqual(str(p.last_name),'2')
        self.assertEqual(p.description,'A vogon')
        
        
    def testPersonDestroy(self):
        p=self.createDefaultPerson()
        pid=p.id
        r= self.client.get('/api/people/{}/'.format(pid),format='json')
        self.assertEqual(r.status_code,status.HTTP_200_OK)
        r= self.client.delete('/api/people/{}/'.format(pid),format='json')
        self.assertEqual(r.status_code,status.HTTP_204_NO_CONTENT)
        r= self.client.get('/api/people/{}/'.format(pid),format='json')
        self.assertEqual(r.status_code,status.HTTP_404_NOT_FOUND)
    

    def testPersonAddPseudonym(self):
        p=self.createDefaultPerson()
        url='/api/people/{}/pseudonyms'.format(p.id)
        with self.subTest("single"):
            d=['A']
            r=self.client.post(url,data=d,format='json')
            self.assertEqual(r.status_code,status.HTTP_200_OK)
            p.refresh_from_db()
            set(p.pseudonyms.all()) == set(d)

        with self.subTest("several"):
            d=['B','C']
            r=self.client.post(url,data=d,format='json')
            self.assertEqual(r.status_code,status.HTTP_200_OK,r.json())
            p.refresh_from_db()
            set(p.pseudonyms.all()) == set(d)
        with self.subTest("idempotent add"):
            d=['A']
            r=self.client.post(url,data=d,format='json')
            self.assertEqual(r.status_code,status.HTTP_200_OK)
            p.refresh_from_db()
            self.assertIn('A', (x.name for x in p.pseudonyms.all()))
    
    def testPersonAddUsername(self):
        p=self.createDefaultPerson()
        
        with self.subTest("Fail no such site"):
            url='/api/people/{}/users'.format(p.id)
            r=self.client.post(url,data=self.defaultUsernameDict(),format='json')
            self.assertEqual(r.status_code,status.HTTP_404_NOT_FOUND)

        with self.subTest("Success"):
            w=self.createDefaultWebsite()
            d=self.defaultUsernameDict()
            url='/api/people/{}/users'.format(p.id)
            r=self.client.post(url,data=d,format='json')
            self.assertEqual(r.status_code,status.HTTP_200_OK)
            un=p.usernames.all()[0]
            self.assertEqual(un.name.name,d['name'])
            self.assertEqual(un.website_id,w.id)
        with self.subTest("Fail conflict/in use"):
            p2=self.createDefaultPerson()
            url='/api/people/{}/users'.format(p2.id)
            r=self.client.post(url,data=self.defaultUsernameDict(),format='json')
            self.assertEqual(r.status_code,status.HTTP_409_CONFLICT)
    
    def testPersonAutomaticCreateAddUsername(self):
        
        d=[
            {
                'name':'a',
                'domain':'null.com'
            }
        ]
        with self.subTest("Malformed"):
            url='/api/people/autocreate/'
            r=self.client.post(url,data=d,format='json')
            self.assertEqual(r.status_code,status.HTTP_400_BAD_REQUEST)
        d={
            'identifiers':[{
                'name':'a',
                'domain':'null.com'
            }]
        }
        with self.subTest("Create nonexisting site"):
            url='/api/people/autocreate/'
            r=self.client.post(url,data=d,format='json')
            self.assertEqual(r.status_code,status.HTTP_404_NOT_FOUND)
        
        w=self.createDefaultWebsite()
        d={
            'identifiers':[{
                'name':'a',
                'domain':w.domain
            }]
        }
        with self.subTest("Create new"):
            url='/api/people/autocreate/'
            r=self.client.post(url,data=d,format='json')
            self.assertEqual(r.status_code,status.HTTP_201_CREATED)
        with self.subTest("Create existing"):
            r=self.client.post(url,data=d,format='json')
            self.assertEqual(r.status_code,status.HTTP_200_OK)
        with self.subTest("Augment existing"):
            d['identifiers'].append({
                'name':'b',
                'domain':w.domain
            })
            r=self.client.post(url,data=d,format='json')
            self.assertEqual(r.status_code,status.HTTP_200_OK)
        
        with self.subTest("Conflict"):
            aux={'name':'c','domain':w.domain}
            daux={'identifiers':[aux]}
            #create c as independant
            r=self.client.post(url,data=daux,format='json')
            d['identifiers'].append(aux)
            #try to associate c with a different existing person
            r=self.client.post(url,data=d,format='json')
            self.assertEqual(r.status_code,status.HTTP_409_CONFLICT)
        
        with self.subTest('Url'):
            upat=UrlPattern(website=w,pattern='^(?:https?:\/\/)?(?:www\.)?(?:twitter\.com\/){1,2}@?([^\/]+)\/?$')
            upat.save()
            d={'urls':'http://www.twitter.com/username'}
            r=self.client.post(url,data=d,format='json')
            self.assertEqual(r.status_code,status.HTTP_201_CREATED)
            #TODO check it got into DB, but I use this live so I'm pretty sure it does
            
    # def testPersonAddDistinguish(self):
    #     with self.subTest("Success"):
    #         raise NotImplementedError()
    #     with self.subTest("Fail duplicate reference"):
    #         raise NotImplementedError()

    # def testPersonAddURL(self):
    #     raise NotImplementedError()
    # def testPersonAddTag(self):
    #     with self.subTest("Success"):
    #         raise NotImplementedError()
    #     with self.subTest("Fail duplicate reference"):
    #         raise NotImplementedError()
    # def testPersonAddAmbiguousTag(self):
    #     with self.subTest("Success"):
    #         raise NotImplementedError()
    #     with self.subTest("Fail duplicate reference"):
    #         raise NotImplementedError()


    # def testPersonRemovePseudonym(self):
    #     with self.subTest("Success"):
    #         raise NotImplementedError()
    #     with self.subTest("Fail none existing"):
    #         raise NotImplementedError()
    # def testPersonRemoveUsername(self):
    #     with self.subTest("Success"):
    #         raise NotImplementedError()
    #     with self.subTest("Fail none existing"):
    #         raise NotImplementedError()
    # def testPersonRemoveDistinguish(self):
    #     with self.subTest("Success"):
    #         raise NotImplementedError()
    #     with self.subTest("Fail none existing"):
    #         raise NotImplementedError()
    # def testPersonRemovePseudonym(self):
    #     with self.subTest("Success"):
    #         raise NotImplementedError()
    #     with self.subTest("Fail none existing"):
    #         raise NotImplementedError()
    # def testPersonRemoveURL(self):
    #     with self.subTest("Success"):
    #         raise NotImplementedError()
    #     with self.subTest("Fail none existing"):
    #         raise NotImplementedError()
    # def testPersonRemoveTag(self):
    #     with self.subTest("Success"):
    #         raise NotImplementedError()
    #     with self.subTest("Fail none existing"):
    #         raise NotImplementedError()
    # def testPersonRemoveAmbiguousTag(self):
    #     with self.subTest("Success"):
    #         raise NotImplementedError()
    #     with self.subTest("Fail none existing"):
    #         raise NotImplementedError()
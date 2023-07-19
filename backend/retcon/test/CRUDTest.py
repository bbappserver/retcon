from rest_framework.test import APIRequestFactory,force_authenticate,APITestCase
from django.contrib.auth.models import User
import json
class CRUDTest:
    
    def setUp(self):
        self.superUser = User.objects.create_user('root', 'root@retcon.com', 'x',is_superuser=True)
        self.superUser.save()
        self.factory = APIRequestFactory()

class APICRUDTest(APITestCase):
    def setUp(self):
        self.superUser = User.objects.create_user('root', 'root@retcon.com', 'x',is_superuser=True)
        self.superUser.save()
        self.factory = APIRequestFactory()
    
    def assertEqualFilteredDict(self,a,b,ignored_keys=None,message=''):
        if ignored_keys is None: ignored_keys=set()
        aks=set(a.keys())
        bks=set(b.keys())
        ignored_keys=set(ignored_keys)
        aks-=ignored_keys
        bks-=ignored_keys

        self.assertEqual(aks,bks, message+"Dictionary keysets do not match")

        for k in aks:
            self.assertEqual(a[k],b[k],'a[{}] != b[{}]'.format(k,k))
    
    def assertCoverFilteredDict(self,subset,cover,ignored_keys=None,message=''):
        if ignored_keys is None: ignored_keys=set()
        aks=set(subset.keys())
        bks=set(cover.keys())
        ignored_keys=set(ignored_keys)
        aks-=ignored_keys
        bks-=ignored_keys

        self.assertLessEqual(aks,bks, message+"Covers keys do not cover subset")

        for k in aks:
            self.assertEqual(subset[k],cover[k],'a[{}] != b[{}]'.format(k,k))
    
    

        
    # def testCreate(self):
    #     raise NotImplementedError()
    #     factory = APIRequestFactory()
    #     request = factory.put('/notes/547/', {'title': 'remember to email dave'})
    #     force_authenticate(request, user=user)

    # def testCreateMultiple(self):
    #     raise NotImplementedError()
    #     factory = APIRequestFactory()
    #     request = factory.put('/notes/547/', {'title': 'remember to email dave'})
    
    # def testRetrieve(self):
    #     raise NotImplementedError

    # def testUpdate(self):
    #     raise NotImplementedError()
    #     factory = APIRequestFactory()
    #     request = self.factory.put('/notes/547/', {'title': 'remember to email dave'})
    
    # def testDelete(self):
    #     raise NotImplementedError

# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase
# from myproject.apps.core.models import Account

# class AccountTests(APITestCase):
#     def test_create_account(self):
#         """
#         Ensure we can create a new account object.
#         """
#         url = reverse('account-list')
#         data = {'name': 'DabApps'}
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Account.objects.count(), 1)
#         self.assertEqual(Account.objects.get().name, 'DabApps')
    
    
from rest_framework.test import APIRequestFactory,force_authenticate
from django.contrib.auth.models import User
class CRUDTest:
    
    def setUp(self):
        self.superUser = User.objects.create_user('root', 'root@retcon.com', 'x',is_superuser=True)
        self.superUser.save()
        self.factory = APIRequestFactory()

    
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
    
    
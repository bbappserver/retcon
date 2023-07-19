from django.test import TestCase as djTest
from rest_framework.test import DjangoClient
from retcon.test.CRUDTest import APICRUDTest
from unittest import skip

# Create your tests here.
class FileAPITest(APICRUDTest):

    def testCreateManagedFile(self):

        with self.subTest("With md5"):
            d={'md5':'1234'}
            self.client.post('/API/file_id.json',d)
        with self.subTest("With sha256"):
            d={'sha256':'1234'}
            self.client.post('/API/file_id.json',d)
        with self.subTest("With md5+sha256"):
            d={'md5':'1234',
            'sha256':'1234'
            }
        #    self.client.post('/API/file_id.json',d)
        # with self.subTest("With upload"):
        #     blob='x'*(4<<20)
        #     self.client.post('/API/file/upload',data=blob)
        #     #compute hashes
        #     #track file
        #     #test contents and expected hash

        #     #Now do it a gain with a file that exists
        #     self.client.post('/API/file/upload',data=blob)
        #     #compute hashes
        #     #track file
        #     #test contents and expected hash

        #     #erase file
        #     raise NotImplementedError()
    
    # def testRetrieveManagedFile(self):
    #     raise NotImplementedError()


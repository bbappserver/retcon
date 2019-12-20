from django.test import LiveServerTestCase
from retconclient.client import Retcon
from .models import Strings
# Create your tests here.
class SharedStringAPITestCase(LiveServerTestCase):
    def setUp(self):
        self.client=Retcon(domain = self.live_server_url)
        self.create()

    def create(self):
        self.testString=self.client.SharedString(name="sjhgvfdskjzbvgalrg")
        self.testString.save()
        

    def test_create(self):
        self.assertEqual(self.testString.id , Strings.objects.get(name="sjhgvfdskjzbvgalrg").id )
        self.assertEqual(self.testString.name , Strings.objects.get(name="sjhgvfdskjzbvgalrg").name )
    
    def test_update(self):
        self.testString.get_or_create()
        self.testString.name='abc'
        self.testString.save()
        other =Strings.objects.get(name="abc")
        self.assertEqual(self.testString.id , other.id )
        self.assertEqual(self.testString.name , other.name )
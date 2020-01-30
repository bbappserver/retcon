import requests,json
from common import *
# data={
# 'first_name':"Billy",
#  'last_name':"Harrington",
#  'pseudonyms':"Billyharrington",
#   'description':"Adult actor",
#    'tags':"gay pornstar",
#    'usernames':[
#        "domain":"twitter.com",
#        "name":"Billyharrington"],
#    'user_numbers':[
#        "domain":"pixiv.net",
#        "number":12345
#    ]
# }
# r=requests.post("http://localhost:8000/api/people/",data=data)
# print(r.text[0:1000])

class Retcon:

    def __init__(self,requests_session=requests.Session(),domain="http://localhost:8000"):
        self.session=requests_session
        self.domain=domain
    
    def login(self,user,password):
        d={'username':user,'password':password}
        url=self.domain+'/api-token-auth/'
        r=self.post(url,data=d)
        token = r.json()['token']
        #NB HTTP calls the authentication token authorization, 
        #because that didn't get caught in the OG spec
        self.session.headers['Authorization']='Token '+token

    def head(self,url,**kwargs):
        return self.session.head(url,**kwargs)
    
    def get(self,url,**kwargs):
        return self.session.get(url,**kwargs)
    
    def put(self,url,**kwargs):
        return self.session.put(url,**kwargs)
    
    def post(self,url,**kwargs):
        return self.session.post(url,**kwargs)
    
    def patch(self,url,**kwargs):
        return self.session.patch(url,**kwargs)
    
    def delete(self,url,**kwargs):
        return self.session.delete(url,**kwargs)
    
    def options(self,url,**kwargs):
        return self.session.options(url,**kwargs)
    
    def SharedString(self,**kwargs):
        return SharedString(self,**kwargs)
    
    def Person(self,**kwargs):
        return Person(self,**kwargs)






# print("test")

# if __name__=="main":
# c=Retcon()
c.login('root','testpass')
data=[
    # {'website':'twitter.com','name':'fakeuser1'},
    # {'website':'twitter.com','name':'fakeuser2'},
    {'website':'twitter.com','number':100},
]
c.post("http://127.0.0.1:8000/api/people/2/users/",json=data)
# #    s=c.SharedString(id=1).get_or_create()
# # s.name="com"
# # s.save()
# # s=c.SharedString(id=1).get_or_create()
# p=c.Person(id=2)
# p.get()
# print(p)
# assert(s.name=='com')
#print(SharedString.list(c))
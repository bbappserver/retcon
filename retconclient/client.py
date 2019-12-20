import requests
import json
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
        raise NotImplementedError()

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

class DoesNotExist(Exception):
    pass

class Exists(Exception):
    pass
class MultipleRows(Exception):
    pass

class ClientObject:
    endpoint=None
    def __init__(self,client,id=None):
        self.client=client
        self.endpoint=self._endpoint
        self.id=id

    def save(self):
        if self.id is None:
            self.create()
        else:
            self.update()

    def get_or_create(self):
        try:
            self.get()
        except DoesNotExist:
            self.create()
        return self
    
    def get(self):
        if self.id is None:
            raise NotImplementedError("TODO DRF filters")
        
        r=self.client.get(self.pk_url)
        if r.status_code == 200:
            d=json.loads(r.text)
            for k in d.keys():
                setattr(self,k,d[k])
            return self
        else:
            raise DoesNotExist()
    
    def filter(self):
        '''TODO Not Implemented'''
        raise NotImplementedError("TODO DRF filters")

    def create(self):
        r=self.client.post(self.endpoint,data=self.as_dict())
        if r.status_code == 201:
            d=json.loads(r.text)
            for k in d.keys():
                setattr(self,k,d[k])
        else:
            raise Exists()
    
    def update(self):
        d=self.as_dict()
        if 'id' in d:
            del d['id']
        r=self.client.patch(self.pk_url,json=d)

        if r.status_code != 200:
            raise Exception(r.text)

    @property
    def pk_url(self):
        #The terminating slash is required without extra settings
        return self.endpoint+str(self.id)+'/'
    
    @property
    def _endpoint(self):
        return self.client.domain+self.endpoint
    
    def as_dict(self):
        d=dict(self.__dict__)
        del d["client"]
        del d["endpoint"]
        return d

class SharedString(ClientObject):
    endpoint="/api/strings/"
    def __init__(self,client,id=None,name=None):
        super().__init__(client,id)
        self.name=name
        
    @property
    def exists(self):
        raise NotImplementedError

    def list(self):
        r=self.client.get(self.endpoint)
        for e in r:
            s=self.alloc()
            d=json.loads(r.text)
            for k in d.keys():
                setattr(s,k,d[k])
            yield e
    def alloc(self):
        '''Create an empty clone of this class type connected to the same client'''
        return self.client.SharedString()



#print(r.text[0:1000])

class Person(ClientObject):
    def __init__(self,
        id=None,
        first_name=None,
        last_name=None,
        pseudonyms=[],
        description=None,
        tags=[],
        usernames=[],
        usernumbers=[]
    ):
        self.id=id
        self.first_name=first_name
        self.last_name=last_name
        self.pseudonyms=pseudonyms,
        self.description=description,
        self.tags=tags,
        self.usernames=usernames,
        self.usernumbers=usernumbers



# print("test")

if __name__=="main":
    c=Retcon()
    s=c.SharedString(id=1).get_or_create()
    s.name="hello"
    s.save()
    #print(SharedString.list(c))
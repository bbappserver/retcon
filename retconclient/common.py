import requests,json



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
    
    def __str__(self):
        return str(json.dumps(self.as_dict()))

class DoesNotExist(Exception):
    pass

class Exists(Exception):
    pass
class MultipleRows(Exception):
    pass



class Person(ClientObject):
    endpoint="/api/people/"
    def __init__(self,client,
        id=None,
        first_name=None,
        last_name=None,
        pseudonyms=[],
        description=None,
        tags=[],
        usernames=[],
        usernumbers=[]
    ):
        super().__init__(client)
        self.id=id
        self.first_name=first_name
        self.last_name=last_name
        self.pseudonyms=pseudonyms,
        self.description=description,
        self.tags=tags,
        self.usernames=usernames,
        self.usernumbers=usernumbers
    

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
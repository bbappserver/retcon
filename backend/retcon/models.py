# from django.db import models
# from abc import ABC,abstractmethod
# class TransferabbleModelMixin(ABC):

#     @abstractmethod
#     def get_transfer_key(self):
#         '''Returns a key that can be used to uniquely identify this row in remote databases'''
#         raise NotImplementedError("Subclasses of Transferabble Model must implement this")
    
#     def merge(self,other):
#         '''Generates a merge between self or other where self is the object to be kept
#         or raises a ValueError on conflict.  Note: this does not invoke save()
#         '''
#         raise NotImplementedError()
    
#     @abstractmethod
#     @classmethod
#     def get_with_transfer_key(cls,tk):
#         '''Returns the item which is uniquely identified by the transfer key'''
#         raise NotImplementedError()

#     @classmethod
#     def create_with_transfer_key(cls,tk):
#         '''Create with key if that's possible, allows use of convenience methos geto_or_create_with_transfer_key'''
#         raise NotImplementedError()

#     @classmethod
#     def get_or_create_with_transfer_key(cls,tk):
#         try:
#             o=cls.get_with_transfer_key(tk)
#             return (o,False)
#         except cls.ObjectNotFound:
#             return (create_with_transfer_key,True)


#     class Meta:
#         abstract=True



# class TransferSerializer(ABC):

#     '''
# {
#     "key":"jslkfdjsldf"
#     "version":""
#     "payload":
#     {

#     }
# }
# '''

#     @abstractmethod
#     def pack():
#         '''Generates a serialized representation of an object and all of its dependencies'''
#         raise NotImplementedError

#     def packMany():
#         '''Generates a serialized representation of several object and all of their dependencies
#         @returns 
#         '''
#         raise NotImplementedError
    
#     @abstractmethod
#     def unpack():
#         '''Converts an object serialization and all of its dependencies back into the origional object
#         or throws a ValueError on conflict
#         It and its dependant many be resolved into objects already in the local database
#         @returns (created,object)
#         '''
#         raise NotImplementedError

#     def unpackMany():
#         '''Converts an multiobject serialization and all of its dependencies back into the origional object
#         or throws a ValueError on conflict
#         They and their dependants many be resolved into objects already in the local database
#         @returns [(created,object)]
#         '''
#         raise NotImplementedError

#     def version():
#         raise NotImplementedError


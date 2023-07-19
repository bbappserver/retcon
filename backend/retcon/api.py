from rest_framework import serializers,viewsets,status,response,renderers
from rest_framework.decorators import action,renderer_classes
from django.db import transaction
from django.conf import settings
from sharedstrings.models import Strings
import django.db.models.fields.related as rf
import djangorestframework_camel_case

class CamelSnakeRenderer(renderers.JSONRenderer):
    '''Answers non browser clients in snake case, but talks to browsers in camelCase'''
    def render(self, data, accepted_media_type=None, renderer_context=None):
        r=renderer_context['request']
        if 'HTTP_USER_AGENT' in r.META and r.META['HTTP_USER_AGENT'].startswith('Mozilla'):
            return djangorestframework_camel_case.render.CamelCaseJSONRenderer().render(data,accepted_media_type=accepted_media_type,renderer_context=renderer_context)
        else:
            return super().render(data,accepted_media_type=accepted_media_type,renderer_context=renderer_context)
            
    

class RetconModelViewSet(viewsets.ModelViewSet):
    renderer_classes = [CamelSnakeRenderer]
    '''A modelviewset with variaous helpful extensio methods'''
    def generic_master_detail_list_request_handler(self, request, master, subordinate_field_serializer, subordinate_field_name, subordinate_type,data=None):
        '''Treats POSTs as adding body list elements to a list,GETs as requesting the list, and DELTES as removing elements'''
        ret= response.Response({},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        subordinate_field = getattr(master,subordinate_field_name)
        
        if data is None:
            rd=request.data
        else:
            rd=data

        try:
            if request.method == 'GET':
                serializer=subordinate_field_serializer(subordinate_field.all(),many=True)
                ret= response.Response(serializer.data,status=status.HTTP_200_OK)
            else:
                # serializer=subordinate_field_serializer(data=request.data,many=True)
                # if serializer.is_valid():
                #Don't need to validate because name is required on creation, but we might be doing lookup by just id
                #If we fail on get then we will drop out of the transaction and we can report malformed

                if request.method == 'POST':
                    ret = self._existing_item_add_handler(rd, subordinate_type, subordinate_field, master)
                elif request.method == 'DELETE':
                    ret = self._existing_item_delete_handler(rd, subordinate_type, subordinate_field, master)
                # else:
                #     return response.Response({'status':'fail','message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            if settings.DEBUG:
                ret= response.Response(str(e),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                ret= response.Response({},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return ret

    def generic_master_detail_get_or_create_list_request_handler(self, request, master, subordinate_field_serializer, subordinate_field_name, subordinate_type,data=None):
        '''Treats POSTs as adding body list elements to a list,GETs as requesting the list, and DELTES as removing elements'''
        ret= response.Response({},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        subordinate_field = getattr(master,subordinate_field_name)
        
        if data is None:
            rd=request.data
        else:
            rd=data

        try:
            if request.method == 'GET':
                serializer=subordinate_field_serializer(subordinate_field.all(),many=True)
                ret= response.Response(serializer.data,status=status.HTTP_200_OK)
            else:
                # serializer=subordinate_field_serializer(data=request.data,many=True)
                # if serializer.is_valid():
                #Don't need to validate because name is required on creation, but we might be doing lookup by just id
                #If we fail on get then we will drop out of the transaction and we can report malformed

                if request.method == 'POST':
                    ret=self._get_create_item_add_handler(rd, subordinate_type, subordinate_field, master)
                elif request.method == 'DELETE':
                    ret=self._existing_item_delete_handler(rd, subordinate_type, subordinate_field, master)
                # else:
                #     return response.Response({'status':'fail','message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            if settings.DEBUG:
                ret= response.Response(str(e),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                ret= response.Response({},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return ret    
    
    def _existing_item_add_handler(self, rd, subordinate_type, subordinate_field, master):
        #method= subordinate_field.add
        success=False
        with transaction.atomic():
            for d in rd:
                o=subordinate_type.objects.get(**d)
                subordinate_field.add(o)
            master.save()
            success=True
        if success:
            ret= response.Response({'status':'success'},status=status.HTTP_200_OK)
            # serializer=subordinate_field_serializer(list(subordinate_field.all()),many=True)
            # ret=response.Response(serializer.data,status=status.HTTP_200_OK)
        else:
            ret= response.Response({'status':'fail','message':'One or more of the requested objects to be added did not exist.'},status=status.HTTP_428_PRECONDITION_REQUIRED)
        return ret
    
    def _get_create_item_add_handler(self, rd, subordinate_type, subordinate_field, master):
        #method= subordinate_field.add
        success=False
        with transaction.atomic():
            for d in rd:
                created,o=subordinate_type.objects.get_or_create(**d)
                subordinate_field.add(o)
            master.save()
            success=True
        if success:
            ret= response.Response({'status':'success'},status=status.HTTP_200_OK)
            # serializer=subordinate_field_serializer(list(subordinate_field.all()),many=True)
            # ret=response.Response(serializer.data,status=status.HTTP_200_OK)
        else:
            ret= response.Response({'status':'fail','message':'One or more of the requested objects to be added did not exist.'},status=status.HTTP_428_PRECONDITION_REQUIRED)
        return ret

    def _existing_item_delete_handler(self, rd, subordinate_type, subordinate_field, master):
        #method = subordinate_field.remove
        success=False
        with transaction.atomic():
                for d in rd:
                    o=subordinate_type.objects.get(**d)
                    subordinate_field.remove(o)
                master.save()
                success=True
        if success:
            ret= response.Response({'status':'success'},status=status.HTTP_200_OK)
            # serializer=subordinate_field_serializer(list(subordinate_field.all()),many=True)
            # ret=response.Response(serializer.data,status=status.HTTP_200_OK)
        else:
            ret= response.Response({'status':'fail','message':'One or more of the requested objects to be removed did not exist.'},status=status.HTTP_428_PRECONDITION_REQUIRED)
        return ret

    def _request_to_filter_dict(self,d):
        '''
        Subclasses must implement this method to support filtering.
        Converts a requests dicitonary to input for Model.queryset.filter(**d)

        :returns: null if result would find no items (for eaxmple not found foreign item), else a dict for queryset
        '''

        # for k in d:
        #     if isinstance(k[d],dict):
        #         #foreign key
        #         elif isinstance(k[d],list):
        #             #many to many
        # field_spec=self.serializer_class.Meta.model._meta.get_fields()
        # for f in field_spec:
        #     if f in d:
        #         if isinstance(f,rf.ManyToManyRel):
        #             #m2m
        #             subordinates=f.related_model.filter(d[f.field_name])
        #         elif isinstance(f,rf.ManyToOneRel):
        #             subordinate=f.related_model.get(d[f.field_name])
                #fk
            # elif isinstance(f,rf.ForeignKey):


        raise NotImplementedError('This view needs to implement _request_to_filter_dict to support the filter action')
    
    def _filter_objects(self,filter_dict):
        '''
        The object set retured by the filter(self,request), 
        by default just calls get_queryset().filter(**filter_dict)

        Override for more sophisticated query behaviour.
        '''
        return self.get_queryset().filter(**d)
    
    def _substitute_fk_for_shared_string(self,shared_string):
        return Strings.objects.get(name=shared_string)

    @action(methods=['POST','GET'],detail=False)
    def filter(self,request):
        d=self._request_to_filter_dict(request.data)
        if d is None:
            return []
        return self.get_paginated_response(self._filter_objects(d))





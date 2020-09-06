from rest_framework import serializers,viewsets,status,response
from rest_framework.decorators import action,renderer_classes
from django.db import transaction
from django.conf import settings


class RetconModelViewSet(viewsets.ModelViewSet):
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
                    self._existing_item_add_handler(rd, subordinate_type, subordinate_field, master)
                elif request.method == 'DELETE':
                    self._existing_item_delete_handler(rd, subordinate_type, subordinate_field, master)
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


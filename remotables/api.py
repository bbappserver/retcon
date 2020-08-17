from rest_framework import serializers,viewsets,response
from .models import ContentResource

class ContentResourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContentResource
        fields = ['id','url','content_last_modified','valid_until','content_last_fetched','valid_until']
    
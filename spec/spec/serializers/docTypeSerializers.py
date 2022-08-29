from rest_framework import serializers

from ..models import DocType

class DocTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocType
        fields = ('name', 'descr', 'confidential', 'jira_temp', )

class DocTypePutSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocType
        fields = ('descr', 'confidential', 'jira_temp', )


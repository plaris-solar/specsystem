from rest_framework import serializers

from ..models import Spec, SpecFile, SpecHist, SpecReference, SpecSig


class SpecSigSerializer(serializers.ModelSerializer):
    spec_one = serializers.BooleanField(source='role.spec_one')
    class Meta:
        model = SpecSig
        fields = ('role', 'signed_dt', 'from_am', 'spec_one', )

    def to_representation(self, value):
        data = super(SpecSigSerializer, self).to_representation(value)
        data['signer'] = value.signer.username if value.signer else None
        data['delegate'] = value.delegate.username if value.delegate else None
        return data

class SpecHistSerializer(serializers.ModelSerializer):
    upd_by = serializers.CharField(source='upd_by.username')
    class Meta:
        model = SpecHist
        fields = ('mod_ts', 'upd_by', 'change_type', 'comment', )

class SpecFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecFile
        fields = ('seq', 'filename', 'incl_pdf', 'file', )

class SpecReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecReference
        fields = ('num', 'ver', )

class SpecSerializer(serializers.ModelSerializer):
    doc_type = serializers.StringRelatedField()
    department = serializers.StringRelatedField()
    created_by = serializers.StringRelatedField()
    class Meta:
        model = Spec
        fields = ('num', 'ver', 'title', 'doc_type', 'department', 'keywords', 'state', 'created_by', 'create_dt', 'mod_ts', 'jira', )

    def to_representation(self, value):
        data = super(SpecSerializer, self).to_representation(value)
        # Sort the related fields
        sigs = value.sigs.order_by('-from_am', 'role', ).all()
        data['sigs'] = SpecSigSerializer(sigs, many=True, context=self.context).data
        
        files = value.files.order_by('seq', ).all()
        data['files'] = SpecFileSerializer(files, many=True, context=self.context).data
        
        refs = value.refs.order_by('num', 'ver', ).all()
        data['refs'] = SpecReferenceSerializer(refs, many=True, context=self.context).data
        
        hist = value.hist.order_by('-mod_ts', ).all()
        data['hist'] = SpecHistSerializer(hist, many=True, context=self.context).data

        return data
        
class SpecSigPostSerializer(serializers.Serializer):
    role = serializers.CharField()
    signer = serializers.CharField(required=False, default=None, allow_null=True)
    from_am = serializers.BooleanField(required=False, default=False)
        
class SpecFilePostSerializer(serializers.Serializer):
    filename = serializers.CharField()
    incl_pdf = serializers.BooleanField(required=False, default=False)

class SpecPostSerializer(serializers.Serializer):
    title = serializers.CharField()
    doc_type = serializers.CharField()
    department = serializers.CharField()
    keywords = serializers.CharField(required=False, default=None, allow_blank=True, allow_null=True)
    jira = serializers.CharField(required=False, default=None, allow_blank=True, allow_null=True)
    sigs = SpecSigPostSerializer(many=True)
    files = SpecFilePostSerializer(many=True)
    refs = SpecReferenceSerializer(many=True)
        
class FilePostSerializer(serializers.Serializer):
    file = serializers.FileField(required=False, default=None, allow_null=True)

class SpecSignSerializer(serializers.Serializer):
    role = serializers.CharField()
    signer = serializers.CharField(required=False, default=None, allow_blank=True, allow_null=True)

class SpecRejectSerializer(serializers.Serializer):
    comment = serializers.CharField()


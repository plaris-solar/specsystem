import re
from spec.serializers.specSerializers import SpecDetailSerializer
from user.models import User
from rest_framework import serializers

from ..models import Spec, UserDelegate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active', 'email', )

    def to_representation(self, value):
        data = super(UserSerializer, self).to_representation(value)
        data['delegates'] = ', '.join(sorted(list(value.delegates.values_list('delegate__username', flat=True))))
        data['delegates_for'] = sorted(list(value.delegates_for.values_list('user__username', flat=True)))
        data['watches'] = sorted(list(value.watches.values_list('num', flat=True)))
        
        # Lookup any specs waiting for a signature from this user
        # Directly assigned
        req_sig = Spec.objects.filter(state='Signoff', sigs__signed_dt__isnull=True, sigs__signer=value)
        data['req_sig'] = SpecDetailSerializer(req_sig, many=True, context=self.context).data
        # Assigned to someone user is a delegate for
        req_sig_delegate = Spec.objects.filter(state='Signoff', sigs__signed_dt__isnull=True, sigs__signer__delegates__delegate=value)
        data['req_sig_delegate'] = SpecDetailSerializer(req_sig_delegate, many=True, context=self.context).data
        # Assigned to a role generally for which user is signer
        req_sig_role = Spec.objects.filter(state='Signoff', sigs__signed_dt__isnull=True, sigs__signer__isnull=True, sigs__role__users__user=value)
        data['req_sig_role'] = SpecDetailSerializer(req_sig_role, many=True, context=self.context).data

        # Inprocess specs user created
        in_process = Spec.objects.filter(state__in=['Draft', 'Signoff'], created_by=value)
        data['in_process'] = SpecDetailSerializer(in_process, many=True, context=self.context).data

        return data

class UserUpdateSerializer(serializers.Serializer):
    delegates = serializers.CharField(required=False, default=None, allow_blank=True, allow_null=True)
    
    def update(self, user, validated_data):
        UserDelegate.objects.filter(user=user).delete()           
        if validated_data["delegates"]:         
            delegates = re.split(r"[\s:;,]+", validated_data["delegates"])
            for delegate in delegates:
                if len(delegate) > 0:
                    d = User.lookup(username=delegate)
                    user_delegate = UserDelegate.objects.create(user=user, delegate=d)

        return user



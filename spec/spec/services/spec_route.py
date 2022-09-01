from rest_framework.exceptions import ValidationError
from spec.models import Spec, SpecHist


def specSubmit(request, spec):
    if spec.state != 'Draft':
        raise ValidationError({"errorCode":"SPEC-R01", "error": "Spec must be in Draft state to submit for signatures"})
    if spec.files.all().count() == 0:
        raise ValidationError({"errorCode":"SPEC-R02", "error": "Spec must be have at least one attached file."})
    if spec.sigs.all().count() == 0:
        raise ValidationError({"errorCode":"SPEC-R03", "error": "Spec must be have at least one signature."})
    missingSigs = list(spec.sigs.filter(role__spec_one=True, signer__isnull=True).values_list('role', flat=True))
    if len(missingSigs) > 0:
        raise ValidationError({"errorCode":"SPEC-R04", "error": f"Signer must be specified for Role(s): {', '.join(missingSigs)}"})
        
    errMsgs = []
    sigs = spec.sigs.filter(signer__isnull=False)
    for sig in sigs:
        validSigners = sig.role.users.values_list('user__username', flat=True)
        if sig.signer.username not in validSigners:
            errMsgs.append(f"Signer {sig.signer} for Role {sig.role.role} needs to be in list: {', '.join(validSigners)}")
    if len(errMsgs) > 0:
        raise ValidationError({"errorCode":"SPEC-R05", "error": ', '.join(errMsgs)})

    spec.mod_ts = request._req_dt
    spec.state = 'Signoff'
    spec.save()

    # Clear any signatures that may have been inadvertantly left
    for sig in spec.sigs.all():
        sig.delegate = None
        sig.signed_dt = None
        sig.save()

    SpecHist.objects.create(
        spec=spec,
        mod_ts = request._req_dt,
        upd_by = request.user,
        change_type = 'Submit',
        comment = ''
    )

    return spec

def specSign(request, spec, validated_data):
    if spec.state != 'Signoff':
        raise ValidationError({"errorCode":"SPEC-R10", "error": "Spec must be in Signoff state to accept signatures"})
        
    sig = spec.sigs.filter(role__role=validated_data['role'], signer__username=validated_data['signer']).first()
    if sig is None:
        raise ValidationError({"errorCode":"SPEC-R11", "error": f"Spec does not have Role {validated_data['role']} / Signer {validated_data['signer']} entry."})
    if sig.delegate is not None:
        return spec # Already signed
    # If user is not the designated signer, see if they are an admin or delegate
    if request.user != sig.signer:
        if not request.user.is_superuser:
            if request.user.username not in sig.signer.delegates.values_list('delegate__username', flat=True):
                raise ValidationError({"errorCode":"SPEC-R12", "error": f"Current user {request.user.username} is not a delegate for {sig.signer.username}"})
    sig.delegate = request.user
    sig.signed_dt = request._req_dt
    sig.save()
    SpecHist.objects.create(
        spec=spec,
        mod_ts = request._req_dt,
        upd_by = request.user,
        change_type = 'Sign',
        comment = f'Signature of Role: {sig.role.role}, Signer: {sig.signer.username}, Performed by: {request.user.username}'
    )

    # If not completely signed, return the current spec
    toBeSigned = spec.sigs.filter(delegate__isnull=True).count()
    if toBeSigned > 0:
        return spec

    # Signatures complete, so Obsolete any previous version and activate this one.
    specs = Spec.objects.filter(num=spec.num, state='Active')
    for s in specs:
        s.mod_ts = request._req_dt
        s.state = 'Obsolete'
        s.save()

        SpecHist.objects.create(
            spec=s,
            mod_ts = request._req_dt,
            upd_by = request.user,
            change_type = 'Obsolete',
            comment = f'Obsoleted by release of {spec.num}/{spec.ver}'
        )

    spec.mod_ts = request._req_dt
    spec.state = 'Active'
    spec.save()

    SpecHist.objects.create(
        spec=spec,
        mod_ts = request._req_dt,
        upd_by = request.user,
        change_type = 'Activate',
        comment = f''
    )

    return spec

def specReject(request, spec, validated_data):
    spec.mod_ts = request._req_dt
    spec.state = 'Draft'
    spec.save()

    # Clear any signatures
    for sig in spec.sigs.all():
        sig.delegate = None
        sig.signed_dt = None
        sig.save()

    SpecHist.objects.create(
        spec=spec,
        mod_ts = request._req_dt,
        upd_by = request.user,
        change_type = 'Reject',
        comment = validated_data['comment']
    )

    return spec


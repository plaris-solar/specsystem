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

    SpecHist.objects.create(
        spec=spec,
        mod_ts = request._req_dt,
        upd_by = request.user,
        change_type = 'Submit',
        comment = ''
    )

    return spec

def specSign(request, spec, validated_data):
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

    SpecHist.objects.create(
        spec=spec,
        mod_ts = request._req_dt,
        upd_by = request.user,
        change_type = 'Reject',
        comment = validated_data['comment']
    )

    return spec


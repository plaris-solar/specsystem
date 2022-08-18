from xml.dom import ValidationErr
from spec.models import Spec, SpecHist


def specSubmit(request, spec):
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


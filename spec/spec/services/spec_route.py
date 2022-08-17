from spec.models import Spec


def specSubmit(request, spec):
    spec.mod_ts = request._req_dt
    spec.state = 'Signoff'
    spec.save()

    return spec

def specSign(request, spec, validated_data):
    specs = Spec.objects.filter(num=spec.num, state='Active')
    for s in specs:
        s.mod_ts = request._req_dt
        s.state = 'Obsolete'
        s.save()

    spec.mod_ts = request._req_dt
    spec.state = 'Active'
    spec.save()

    return spec

def specReject(request, spec, validated_data):
    spec.mod_ts = request._req_dt
    spec.state = 'Draft'
    spec.save()

    return spec


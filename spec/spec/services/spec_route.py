
def specSubmit(request, spec, validated_data):
    spec.mod_ts = request._req_dt
    spec.state = 'Signoff'
    spec.save()

    return spec

def specSign(request, spec, validated_data):
    spec.mod_ts = request._req_dt
    spec.state = 'Signoff'
    spec.save()

    return spec

def specReject(request, spec, validated_data):
    spec.mod_ts = request._req_dt
    spec.state = 'Signoff'
    spec.save()

    return spec


from .spec_create import specSigCreate
from ..models import Category, Role, SpecReference

def specUpdate(request, spec, validated_data):
    spec.mod_ts = request._req_dt

    sigs_data = validated_data.pop("sigs")
    refs_data = validated_data.pop("refs")

    spec.cat = Category.lookup(validated_data.pop("cat"))
    spec.title = validated_data.pop("title")
    spec.keywords = validated_data.pop("keywords")
    spec.save()

    for sig in spec.sigs.all():
        if sig.from_cat:
            sig.singer = None
            sig.save()
        else:
            sig.delete()
    for sig_data in sigs_data:
        specSigCreate(request, spec, Role.lookup(sig_data['role']), sig_data['signer'], False)

    SpecReference.objects.filter(spec=spec).delete()
    for ref_data in refs_data:
        ref_data['spec'] = spec
        SpecReference.objects.create(**ref_data)

    return spec
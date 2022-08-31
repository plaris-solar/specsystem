from .spec_create import specSetReqSigs, specSigCreate
from ..models import Role, SpecFile, SpecReference

def specUpdate(request, spec, validated_data):
    spec.mod_ts = request._req_dt

    sigs_data = validated_data.pop("sigs")
    refs_data = validated_data.pop("refs")
    files_data = validated_data.pop("files")

    spec.created_by = request.user
    spec.title = validated_data.pop("title")
    spec.keywords = validated_data.pop("keywords")
    spec.jira = validated_data.pop("jira")
    spec.save()

    # Clear previous sig entries, preload required sigs
    specSetReqSigs(request, spec)
    for sig_data in sigs_data:
        if sig_data['from_am'] and not sig_data['signer']:
            continue
        specSigCreate(request, spec, Role.lookup(sig_data['role']), sig_data['signer'], False)

    # Clear the previous references
    spec.refs.all().delete()
    for ref_data in refs_data:
        ref_data['spec'] = spec
        SpecReference.objects.create(**ref_data)

    # For files, this update will only update the attributes
    seq = 0
    for file_data in files_data:
        seq += 1
        spec.files.filter(filename=file_data['filename']).update(seq=seq)
        spec.files.filter(filename=file_data['filename']).update(incl_pdf=file_data['incl_pdf'])

    return spec


def specFileUpload(request, spec, validated_data):
    validated_data['spec'] = spec
    validated_data['seq'] = spec.files.count()
    validated_data['filename'] = validated_data['file'].name
    validated_data['incl_pdf'] = False

    specFile = SpecFile.objects.create(**validated_data)

    return spec    
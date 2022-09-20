from rest_framework.exceptions import ValidationError
from .spec_create import specSetReqSigs, specSigCreate
from ..models import Department, DocType, Role, SpecFile, SpecHist, SpecReference

def specUpdate(request, spec, validated_data):
    if spec.state != validated_data['state']:
        if not request.user.is_superuser:
            raise ValidationError({"errorCode":"SPEC-U51", "error": "State changes via update can only be done by an administrator."})
        if not validated_data['comment'] or len(validated_data['comment']) == 0:
            raise ValidationError({"errorCode":"SPEC-U52", "error": "State changes updates require a comment."})
        spec.state = validated_data['state']
    
    # Only superusers can set the anon_access.
    if request.user.is_superuser:
        spec.anon_access = validated_data['anon_access']

    spec.mod_ts = request._req_dt

    sigs_data = validated_data.pop("sigs")
    refs_data = validated_data.pop("refs")
    files_data = validated_data.pop("files")

    spec.created_by = request.user
    spec.doc_type = DocType.lookup(validated_data.pop("doc_type"))
    spec.department = Department.lookup(validated_data.pop("department"))
    spec.title = validated_data.pop("title")
    spec.keywords = validated_data.pop("keywords")
    spec.jira = validated_data.pop("jira")
    spec.save()

    # TODO: Check that user can't save when not in draft state
    # TODO; verify admins can change files without clearing signatures
    # If spec is not in draft state, don't touch the signatures for an admin edit.
    if spec.state == 'Draft':
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

    if validated_data['comment'] and len(validated_data['comment']) > 0:
        SpecHist.objects.create(
            spec=spec,
            mod_ts = request._req_dt,
            upd_by = request.user,
            change_type = 'Update',
            comment = validated_data['comment']
        )

    return spec


def specFileUpload(request, spec, validated_data):
    validated_data['spec'] = spec
    validated_data['seq'] = spec.files.count()+1
    validated_data['filename'] = validated_data['file'].name
    validated_data['incl_pdf'] = False

    specFile = SpecFile.objects.create(**validated_data)

    return spec    
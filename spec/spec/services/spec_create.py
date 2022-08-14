from user.models import User
from ..models import ApprovalMatrix, Department, DocType, Role, Spec, SpecSig, SpecFile, SpecReference

def specSigCreate(request, spec, role, signerName, from_am):
    if signerName:
        signer = User.lookup(username=signerName)
    else:
        signer = None

    if not from_am and signer:
        specRole = SpecSig.objects.filter(spec=spec, role=role, role__users__user=signer, signer=None, from_am=True).first()
        if specRole:
            specRole.signer = signer
            specRole.save()
            return

    specRole = SpecSig.objects.create(spec=spec, role=role, signer=signer, from_am=from_am)

def specFileCreate(request, spec, filename, seq):
    specRole = SpecFile.objects.create(spec=spec, filename=filename, seq=seq)

def specCreate(request, validated_data):
    sigs_data = validated_data.pop("sigs")
    files_data = validated_data.pop("files")
    refs_data = validated_data.pop("refs")
    docTypeName = validated_data.pop("doc_type")
    deptName = validated_data.pop("department")

    validated_data['doc_type'] = DocType.lookup(docTypeName)
    validated_data['department'] = Department.lookup(deptName)

    specNum = Spec.objects.values('num').order_by('-num').values_list('num', flat=True).first()
    validated_data['num'] = specNum + 1 if specNum and specNum >= 300000 else 300000
    validated_data['ver'] = 'A'
    validated_data['state'] = 'Draft'
    validated_data['created_by'] = request.user
    validated_data['create_dt'] = request._req_dt
    validated_data['mod_ts'] = request._req_dt

    spec = Spec.objects.create(**validated_data)

    apvl_mt = ApprovalMatrix.lookup(docTypeName, deptName)
    for signRole in apvl_mt.signRoles.all():
        specSigCreate(request, spec, signRole.role, None, True)
    for sig_data in sigs_data:
        specSigCreate(request, spec, Role.lookup(sig_data['role']), sig_data['signer'], False)

    for file_data in files_data:
        specFileCreate(request, spec, file_data['filename'], file_data['seq'])

    for ref_data in refs_data:
        ref_data['spec'] = spec
        SpecReference.objects.create(**ref_data)

    return spec
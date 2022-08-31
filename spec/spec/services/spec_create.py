from django.core.files.base import ContentFile
from spec.services.revletter import get_next_version
from user.models import User
from ..models import ApprovalMatrix, Department, DocType, Role, Spec, SpecSig, SpecFile, SpecReference

def specSigCreate(request, spec, role, signerName, from_am):
    if signerName:
        signer = User.lookup(username=signerName)
    else:
        signer = None

    if not from_am and signer:
        specRole = SpecSig.objects.filter(spec=spec, role=role, signer=None, from_am=True).first()
        if specRole:
            specRole.signer = signer
            specRole.save()
            return

    specRole = SpecSig.objects.create(spec=spec, role=role, signer=signer, from_am=from_am)

def specSetReqSigs(request, spec):
    spec.sigs.all().delete()
    signRoles = ApprovalMatrix.lookupRoles(spec.doc_type, spec.department.name)
    for signRole in signRoles:
        specSigCreate(request, spec, signRole.role, None, True)

def specFileCreate(request, spec, filename, seq):
    specFile = SpecFile.objects.create(spec=spec, filename=filename, seq=seq)

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

    specSetReqSigs(request, spec)
    for sig_data in sigs_data:
        specSigCreate(request, spec, Role.lookup(sig_data['role']), sig_data['signer'], False)

    for file_data in files_data:
        specFileCreate(request, spec, file_data['filename'], file_data['seq'])

    for ref_data in refs_data:
        ref_data['spec'] = spec
        SpecReference.objects.create(**ref_data)

    return spec

def specRevise(request, spec):
    orig_spec = Spec.objects.get(id=spec.id)

    spec.id = None
    spec.ver = get_next_version(spec.ver)
    spec.state = 'Draft'
    spec.created_by = request.user
    spec.create_dt = request._req_dt
    spec.mod_ts = request._req_dt
    
    spec.save()
    
    specSetReqSigs(request, spec)
       
    for specFile in orig_spec.files.all():      
        if specFile.seq == 0: # Skip the rendered PDF
            continue  
        specFile.id = None
        specFile.spec=spec
        # Create a copy of the file, so it is independent
        # This assures the original file is not deleted from disk as the new spec is edited.
        new_file = ContentFile(specFile.file.read())
        new_file.name = specFile.filename
        specFile.file = new_file
        specFile.save()

    for ref_data in orig_spec.refs.all():
        ref_data.id = None
        ref_data.spec=spec
        ref_data.save()

    return spec
import os
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from rest_framework.exceptions import ValidationError
from spec.services.revletter import get_next_version
from user.models import User
from ..models import ApprovalMatrix, Department, DocType, Role, Spec, SpecHist, SpecSig, SpecFile, SpecReference, UserWatch
from . import jira


def specImport(request, validated_data):
    """Used for initial import of specs to specified state with specified dates"""
    comment = validated_data.pop("comment")

    validated_data['doc_type'] = DocType.lookupOrCreate(validated_data['doc_type'])
    validated_data['department'] = Department.lookupOrCreate(validated_data['department'])

    validated_data['created_by'] = request.user

    spec = Spec.objects.filter(num = validated_data['num'], ver = validated_data['ver']).first()
    if spec:
        spec.state = validated_data['state']
        spec.title = validated_data['title']
        spec.doc_type = validated_data['doc_type']
        spec.department = validated_data['department']
        spec.keywords = validated_data['keywords']
        spec.reason = validated_data['reason']
        spec.jira = validated_data['jira']
        spec.create_dt = validated_data['create_dt']
        spec.approved_dt = validated_data['approved_dt']
        spec.mod_ts = validated_data['mod_ts']
        spec.save()
    else:
        spec = Spec.objects.create(**validated_data)
    
    if len(comment) == 0:
        comment = 'Initial Load'
    SpecHist.objects.create(
        spec=spec,
        mod_ts = request._req_dt,
        upd_by = request.user,
        change_type = 'Import',
        comment = comment
    )

    return spec
    
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
    comment = validated_data.pop("comment")

    validated_data['doc_type'] = DocType.lookup(docTypeName)
    validated_data['department'] = Department.lookup(deptName)

    specNum = Spec.objects.values('num').order_by('-num').values_list('num', flat=True).first()
    validated_data['num'] = specNum + 1 if specNum and specNum >= 300000 else 300000
    validated_data['ver'] = 'A'
    validated_data['state'] = 'Draft'
    validated_data['created_by'] = request.user
    validated_data['create_dt'] = request._req_dt
    validated_data['mod_ts'] = request._req_dt
    validated_data['reason'] = 'Initial Version'

    spec = Spec.objects.create(**validated_data)

    specSetReqSigs(request, spec)
    for sig_data in sigs_data:
        specSigCreate(request, spec, Role.lookup(sig_data['role']), sig_data['signer'], False)

    for file_data in files_data:
        specFileCreate(request, spec, file_data['filename'], file_data['seq'])

    for ref_data in refs_data:
        ref_data['spec'] = spec
        SpecReference.objects.create(**ref_data)

    jira.create(spec)

    return spec

def specRevise(request, spec, validated_data):
    # Grab a copy of the spec being copied for related items below.
    orig_spec = Spec.objects.get(id=spec.id)

    inProcessSpec = Spec.objects.filter(num=spec.num, state__in=['Draft', 'Signoff']).first()
    if inProcessSpec is not None:
        raise ValidationError({"errorCode":"SPEC-C01", "error": f"Version {inProcessSpec.ver} is in state {inProcessSpec.state}. Cannot start a new revision."})

    # Get the latest revision, incase they are copying an obsolete version instead of the active version
    latestSpec = Spec.objects.filter(num=spec.num).order_by('-ver').first()

    spec.id = None
    spec.ver = get_next_version(latestSpec.ver)
    spec.state = 'Draft'
    spec.created_by = request.user
    spec.create_dt = request._req_dt
    spec.mod_ts = request._req_dt
    spec.jira = None
    spec.reason = validated_data['reason']
    spec.approved_dt = None
    spec.sunset_extended_dt = None
    
    spec.save()
    
    specSetReqSigs(request, spec)
       
    for specFile in orig_spec.files.all():    
        if specFile.filename == f"{orig_spec.num}_{orig_spec.ver}.pdf": # Skip the rendered PDF
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

    jira.create(spec)

    to = UserWatch.objects.filter(num=spec.num, user__email__isnull=False).values_list('user__email', flat=True)
    if len(to) > 0 and settings.EMAIL_HOST is not None and len(settings.EMAIL_HOST) > 0:
        email = EmailMessage(
            subject=f'{"[From Test]" if os.environ["AD_SUFFIX"] == "Test" else ""} Spec {spec.num} "{spec.title}" you are watching is being revised by {spec.created_by.username}',
            body=f'''{"[From Test]" if os.environ["AD_SUFFIX"] == "Test" else ""} Spec {spec.num} "{spec.title}" you are watching is being revised by {spec.created_by.username}
            {request.build_absolute_uri('/ui-spec/'+str(spec.num)+'/'+spec.ver)}

            Reason for change:
            {spec.reason}
            ''',
            from_email=settings.EMAIL_HOST_USER,
            to=to,
            reply_to=[spec.created_by.email],
        )
        email.send(fail_silently=False)

    return spec
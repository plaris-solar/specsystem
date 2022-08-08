from user.models import User
from ..models import Category, Role, Spec, SpecSig, SpecFile, SpecReference

def specSigCreate(request, spec, role, signerName, from_cat):
    if signerName:
        signer = User.lookup(username=signerName)
    else:
        signer = None

    if not from_cat and signer:
        specRole = SpecSig.objects.filter(spec=spec, role=role, role__users__user=signer, signer=None, from_cat=True).first()
        if specRole:
            specRole.signer = signer
            specRole.save()
            return

    specRole = SpecSig.objects.create(spec=spec, role=role, signer=signer, from_cat=from_cat)

def specFileCreate(request, spec, filename, seq):
    specRole = SpecFile.objects.create(spec=spec, _uuid=filename, _filename=filename, seq=seq)

def specCreate(request, validated_data):
    sigs_data = validated_data.pop("sigs")
    files_data = validated_data.pop("files")
    refs_data = validated_data.pop("refs")
    catName = validated_data.pop("cat")

    cat = Category.lookup(catName)
    validated_data['cat'] = cat

    specNum = Spec.objects.values('num').order_by('-num').values_list('num', flat=True).first()
    validated_data['num'] = specNum + 1 if specNum else 300000
    validated_data['ver'] = 'A'
    validated_data['state'] = 'Draft'
    validated_data['create_dt'] = request._req_dt
    validated_data['mod_ts'] = request._req_dt

    spec = Spec.objects.create(**validated_data)

    for signRole in cat.signRoles.all():
        specSigCreate(request, spec, signRole.role, None, True)
    for sig_data in sigs_data:
        specSigCreate(request, spec, Role.lookup(sig_data['role']), sig_data['signer'], False)

    fileSeq = 0
    for file_data in files_data:
        fileSeq += 1
        specFileCreate(request, spec, file_data['filename'], fileSeq)

    for ref_data in refs_data:
        ref_data['spec'] = spec
        SpecReference.objects.create(**ref_data)

    return spec
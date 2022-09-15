import re
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from rest_framework.exceptions import ValidationError

class UserDelegate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delegates')
    delegate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delegates_for')

    class Meta:
        managed = True
        db_table = 'user_delegate'

    def __str__(self):
        return self.delegate.username

class UserWatch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watches')
    num = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'user_watch'

    def __str__(self):
        return str(self.num)

class DocType(models.Model):
    name = models.CharField(primary_key=True, max_length=50)
    descr = models.CharField(max_length=4000, blank=True, null=True)
    confidential = models.BooleanField(default=False, blank=True)
    jira_temp = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'doc_type'

    def __str__(self):
        return self.name

    @staticmethod
    def lookup(docTypeName):
        doctype = DocType.objects.filter(name=docTypeName).first()
        if not doctype:
            raise ValidationError({"errorCode":"SPEC-M01", "error": f"Document Type: {docTypeName} does not exist."})
        return doctype

class Role(models.Model):
    role = models.CharField(primary_key=True, max_length=50)
    descr = models.CharField(max_length=4000, blank=True, null=True)
    spec_one = models.BooleanField(default=True, blank=True)

    class Meta:
        managed = True
        db_table = 'role'

    @staticmethod
    def lookup(roleName):
        role = Role.objects.filter(role=roleName).first()
        if not role:
            raise ValidationError({"errorCode":"SPEC-M02", "error": f"Role: {roleName} does not exist."})
        return role
    
    def isMember(self, user):
        if user in self.users.all():
            return True
        return False

class RoleUser(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='users')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')

    class Meta:
        managed = True
        db_table = 'role_user'

    def __str__(self):
        return self.user.username

class Department(models.Model):
    name = models.CharField(primary_key=True, max_length=150)

    class Meta:
        managed = True
        db_table = 'department'

    def __str__(self):
        return self.name

    @staticmethod
    def lookup(deptName):
        dept = Department.objects.filter(name=deptName).first()
        if not dept:
            raise ValidationError({"errorCode":"SPEC-M03", "error": f"Department: {deptName} does not exist."})
        return dept
    
    def isReader(self, user):
        for role in self.readRoles.all():
            if role.isMember(user):
                return True
        return False

class DepartmentReadRole(models.Model):
    dept = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='readRoles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'dept_read_role'
        
    def __str__(self):
        return self.role.role

class ApprovalMatrix(models.Model):
    doc_type = models.ForeignKey(DocType, on_delete=models.CASCADE, related_name='+')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='+', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'apvl_mt'
        unique_together = (('doc_type', 'department'),)
        
    def __str__(self):
        return f'{self.doc_type}-{self.department}'

    @staticmethod
    def lookupRoles(doc_type, deptName, orig_dept=None):
        """
        Find all the Roles required.
        Match on doc_type and department. Then remove the tail of the department after the colon and check again.
        The combined list of roles from the specific department upto the __Generic__ department are added into the list.
        """
        ret = []

        if deptName is None:
            deptName = '__Generic__'
        
        apvl_mt = None
        try: # Department not being found will be retried below, so eat any error on missing part
            department = Department.lookup(deptName)
            apvl_mt = ApprovalMatrix.objects.filter(doc_type=doc_type, department=department).first()
        except:
            pass
        if apvl_mt:
            ret = list(apvl_mt.signRoles.all())
        
        if orig_dept is None:
            orig_dept = deptName
        if deptName and ':' in deptName:
            # Remove the last : and everything after it, to check on the department's parent
            parent_dept = re.sub(':[^:]*$', '', deptName)
            return ret + ApprovalMatrix.lookupRoles(doc_type, parent_dept, orig_dept)
        
        # Finally, try with department named __Generic__ as a coomon root department
        if deptName != '__Generic__':
            return ret + ApprovalMatrix.lookupRoles(doc_type, None, orig_dept)
        
        return ret

class ApprovalMatrixSignRole(models.Model):
    apvl_mt = models.ForeignKey(ApprovalMatrix, on_delete=models.CASCADE, related_name='signRoles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'apvl_mt_sign_role'
        
    def __str__(self):
        return self.role.role

class Spec(models.Model):
    num = models.IntegerField()
    ver = models.CharField(max_length=50)
    title = models.CharField(max_length=4000)
    doc_type = models.ForeignKey(DocType, on_delete=models.PROTECT, related_name='+')
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='+')
    keywords = models.CharField(max_length=4000, blank=True, null=True)
    state = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    create_dt = models.DateTimeField()
    mod_ts = models.DateTimeField()
    jira = models.CharField(max_length=4000, blank=True, null=True)
    anon_access = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'spec'
        unique_together = (('num', 'ver'),)
        
    def __str__(self):
        return f'{self.num}-{self.ver} {self.state}: {self.title}'

    def checkEditable(self, user):
        if self.state == 'Draft':
            return

        raise ValidationError({"errorCode":"SPEC-M07", "error": f"Spec is not in Draft state, it cannot be edited."})
        

    @staticmethod
    def lookup(num, ver, user):
        if ver != "*":
            try:
                spec = Spec.objects.get(num=num, ver=ver)
            except Spec.DoesNotExist:
                raise ValidationError({"errorCode":"SPEC-M04", "error": f"Spec ({num}/{ver}) does not exist."})
        else:
            try:
                spec = Spec.objects.get(num=num, state="Active")
            except Spec.DoesNotExist:
                raise ValidationError({"errorCode":"SPEC-M06", "error": f"No actve version of Spec ({num})."})           
        if not spec.anon_access and not user.is_authenticated:
            raise ValidationError({"errorCode":"SPEC-M08", "error": f"spec {spec.num}-{spec.ver} cannot read without logging in."})
        if spec.doc_type.confidential:
            if not spec.department.isReader(user):
                if spec.state != "Draft" or user != spec.created_by:
                    raise ValidationError({"errorCode":"SPEC-M05", "error": f"User {user} cannot read confiential specs in department {spec.department}."})
        return spec

class SpecSig(models.Model):
    spec = models.ForeignKey(Spec, on_delete=models.CASCADE, related_name='sigs')
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name='+')
    signer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    delegate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    signed_dt = models.DateTimeField(blank=True, null=True)
    from_am = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'spec_sig'
        unique_together = (('spec', 'role', 'signer'),)

class SpecHist(models.Model):
    spec = models.ForeignKey(Spec, on_delete=models.CASCADE, related_name='hist')
    mod_ts = models.DateTimeField()
    upd_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+')
    change_type = models.CharField(max_length=50)
    comment = models.CharField(max_length=4000)

    class Meta:
        managed = True
        db_table = 'spec_hist'

class SpecFile(models.Model):
    spec = models.ForeignKey(Spec, on_delete=models.CASCADE, related_name='files')
    filename = models.CharField(max_length=4000)
    file = models.FileField(blank=True, null=True)
    seq = models.IntegerField()
    incl_pdf = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'spec_file'
        unique_together = (('spec', 'filename'),)        

    @staticmethod
    def lookup(num, ver, fileName, user):
        try:
            spec = Spec.lookup(num, ver, user)
            if fileName is None:
                fileName = "*"
                specFile = spec.files.order_by('seq').first()
            else:
                specFile = spec.files.filter(filename=fileName).first()
            if specFile is not None:
                return specFile
            raise SpecFile.DoesNotExist()
        except SpecFile.DoesNotExist:
            raise ValidationError({"errorCode":"SPEC-M09", "error": f"File {fileName} is not attached to spec ({num}/{ver})."})

class SpecReference(models.Model):
    spec = models.ForeignKey(Spec, on_delete=models.CASCADE, related_name='refs')
    num = models.IntegerField()
    ver = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'spec_reference'

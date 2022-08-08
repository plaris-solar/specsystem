from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from rest_framework.exceptions import ValidationError

class Role(models.Model):
    role = models.CharField(primary_key=True, max_length=50)
    descr = models.CharField(max_length=4000, blank=True, null=True)
    any = models.BooleanField(default=False, blank=True)
    active = models.BooleanField(default=True, blank=True)

    class Meta:
        managed = True
        db_table = 'role'

    @staticmethod
    def lookup(roleName):
        role = Role.objects.filter(role=roleName).first()
        if not role:
            raise ValidationError({"errorCode":"SPEC-M01", "error": f"Role: {roleName} does not exist."})
        return role

class RoleUser(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='users')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')

    class Meta:
        managed = True
        db_table = 'role_user'

    def __str__(self):
        return self.user.username

class Category(models.Model):
    cat = models.CharField(max_length=50)
    sub_cat = models.CharField(max_length=50)
    descr = models.CharField(max_length=4000, blank=True, null=True)
    active = models.BooleanField(default=False, blank=True, null=True)
    confidential = models.BooleanField(default=False, blank=True, null=True)
    jira_temp = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'category'
        unique_together = (('cat', 'sub_cat'),)
        
    def __str__(self):
        return f'{self.cat}/{self.sub_cat}'

    @staticmethod
    def parse(catName):
        catNameArr = catName.split('/', 1)
        if len(catNameArr) != 2:
            raise ValidationError({"errorCode":"SPEC-M03", "error": f"Category name must have one '/' separating category and sub category."})
        return catNameArr

    @staticmethod
    def lookup(catName):
        catNameArr = Category.parse(catName)
        cat = Category.objects.filter(cat=catNameArr[0], sub_cat=catNameArr[1]).first()
        if not cat:
            raise ValidationError({"errorCode":"SPEC-M02", "error": f"Category: {catName} does not exist."})
        return cat

class CategorySignRole(models.Model):
    cat = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='signRoles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'cat_sign_role'
        
    def __str__(self):
        return self.role.role

class CategoryReadRole(models.Model):
    cat = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='readRoles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'cat_read_role'
        
    def __str__(self):
        return self.role.role

class Spec(models.Model):
    num = models.IntegerField()
    ver = models.CharField(max_length=50)
    title = models.CharField(max_length=4000)
    keywords = models.CharField(max_length=4000, blank=True, null=True)
    state = models.CharField(max_length=50)
    cat = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='specs')
    create_dt = models.DateTimeField()
    mod_ts = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'spec'
        unique_together = (('num', 'ver'),)
        
    def __str__(self):
        return f'{self.num}-{self.ver} {self.state}: {self.title}'

class SpecSig(models.Model):
    spec = models.ForeignKey(Spec, on_delete=models.CASCADE, related_name='sigs')
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name='+')
    signer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    delegate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    signed_dt = models.DateTimeField(blank=True, null=True)
    from_cat = models.BooleanField(default=False)

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
    _uuid = models.CharField(max_length=48)
    _filename = models.CharField(max_length=4000)
    seq = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'spec_file'
        unique_together = (('spec', '_uuid'),)

class SpecReference(models.Model):
    spec = models.ForeignKey(Spec, on_delete=models.CASCADE, related_name='refs')
    num = models.IntegerField()
    ver = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'spec_reference'

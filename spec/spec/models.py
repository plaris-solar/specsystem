from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from rest_framework.exceptions import ValidationError

class Role(models.Model):
    role = models.CharField(primary_key=True, max_length=50)
    descr = models.CharField(max_length=4000, blank=True, null=True)
    any = models.BooleanField(default=False, blank=True, null=True)

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
    file_temp = models.CharField(max_length=4000, blank=True, null=True)
    jira_temp = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'category'
        unique_together = (('cat', 'sub_cat'),)

class CategoryRole(models.Model):
    cat = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'category_role'
        
    def __str__(self):
        return self.role.role

class Spec(models.Model):
    num = models.IntegerField()
    ver = models.CharField(max_length=50)
    title = models.CharField(max_length=4000)
    keywords = models.CharField(max_length=4000)
    state = models.CharField(max_length=50)
    cat = models.ForeignKey(Category, on_delete=models.CASCADE)
    create_dt = models.DateTimeField()
    mod_ts = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'spec'
        unique_together = (('num', 'ver'),)

class SpecSig(models.Model):
    spec = models.ForeignKey(Spec, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    signer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+')
    delegate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+')
    signed_dt = models.DateTimeField(null=True)

    class Meta:
        managed = True
        db_table = 'spec_sig'
        unique_together = (('spec', 'role', 'signer'),)

class SpecHist(models.Model):
    spec = models.ForeignKey(Spec, on_delete=models.CASCADE)
    mod_ts = models.DateTimeField()
    upd_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+')
    change_type = models.CharField(max_length=50)
    comment = models.CharField(max_length=4000)

    class Meta:
        managed = True
        db_table = 'spec_hist'

class SpecFile(models.Model):
    spec = models.ForeignKey(Spec, on_delete=models.CASCADE)
    seq = models.IntegerField()
    _filename = models.CharField(max_length=4000)
    _uuid = models.CharField(max_length=48)

    class Meta:
        managed = True
        db_table = 'spec_file'

class SpecReference(models.Model):
    spec = models.ForeignKey(Spec, on_delete=models.CASCADE)
    ref_spec = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = 'spec_reference'

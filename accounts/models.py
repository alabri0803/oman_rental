from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class CustomUser(AbstractUser):
  USER_TYPE = (
    ('OWNER', _('مالك المبني')),
    ('INVESTOR', _('مستثمر شركة مالكة')),
    ('TENANT', _('مستأجر شركة')),
    ('SIGNER', _('مفوض التوقيع')),
    ('ADMIN', _('مسؤول النظام')),
  )
  user_type = models.CharField(
    max_length=10,
    choices=USER_TYPE,
    verbose_name=_('نوع المستخدم'),
  )
  company_name = models.CharField(
    max_length=100,
    blank=True,
    verbose_name=_('اسم الشركة'),
  )
  phone_number = models.CharField(
    max_length=15,
    verbose_name=_('رقم الهاتف'),
  )
  is_authorized = models.BooleanField(
    default=False,
    verbose_name=_('مفعل'),
  )
  commercial_registration = models.CharField(
    max_length=50,
    blank=True,
    verbose_name=_('السجل التجاري')
  )
  tax_number = models.CharField(
    max_length=50,
    blank=True,
    verbose_name=_('الرقم الضريبي')
  )
  groups = models.ManyToManyField(
    Group,
    verbose_name=_('المجموعات'),
    blank=True,
    help_text=_(
      'المجموعات التي ينتمي إليها هذا المستخدم'
    ),
    related_name="customuser_groups",
    related_query_name="customuser",
  )
  user_permissions = models.ManyToManyField(
    Permission,
    verbose_name=_('صلاحيات المستخدم'),
    blank=True,
    help_text=_(
      'الصلاحيات المحددة لهذا المستخدم'
    ),
    related_name="customuser_permissions",
    related_query_name="customuser"
  )

  def __str__(self):
    return f"{self.get_full_name() or self.username} ({self.get_user_type_display()})"

  class Meta:
    verbose_name = _('مستخدم')
    verbose_name_plural = _('المستخدمون')
    ordering = ['-date_joined']
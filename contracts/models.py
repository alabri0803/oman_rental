import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.models import CustomUser
from properties.models import Unit

# Create your models here.

class Contract(models.Model):
  CONTRACT_STATUS = (
    ('DRAFT', _('مسودة')),
    ('PENDING', _('بانتظار التوقيع')),
    ('ACTIVE', _('نشط')),
    ('EXPIRED', _('منتهي')),
    ('TERMINATED', _('ملغى')),
  )
  PAYMENT_TERMS = (
    ('MONTHLY', _('شهري')),
    ('QUARTERLY', _('ربع سنوي')),
    ('SEMI_ANNUAL', _('نصف سنوي')),
    ('ANNUAL', _('سنوي')),
  )
  id = models.UUIDField(
    primary_key=True, 
    default=uuid.uuid4, 
    editable=False
  )
  contract_number = models.CharField(
    max_length=20,
    unique=True,
    verbose_name=_('رقم العقد')
  )
  unit = models.ForeignKey(
    Unit,
    on_delete=models.PROTECT,
    verbose_name=_('الوحدة')
  )
  tenant = models.ForeignKey(
    CustomUser,
    on_delete=models.PROTECT,
    limit_choices_to={'user_type': 'TENANT'},
    verbose_name=_('المستأجر')
  )
  start_date = models.DateField(
    verbose_name=_('تاريخ البدء')
  )
  end_date = models.DateField(
    verbose_name=_('تاريخ الانتهاء')
  )
  monthly_rent = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    verbose_name=_('الإيجار الشهري (ر.ع.)'),
    validators=[MinValueValidator(0)]
  )
  payment_terms = models.CharField(
    max_length=20,
    choices=PAYMENT_TERMS,
    default='MONTHLY',
    verbose_name=_('فترة الدفع')
  )
  security_deposit = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    verbose_name=_('الضمان المالي (ر.ع.)'),
    validators=[MinValueValidator(0)]
  )
  status = models.CharField(
    max_length=20,
    choices=CONTRACT_STATUS,
    default='DRAFT',
    verbose_name=_('حالة العقد')
  )
  terms_and_conditions = models.TextField(
    verbose_name=_('الشروط والأحكام')
  )
  notes = models.TextField(
    blank=True,
    verbose_name=_('ملاحظات')
  )
  created_by = models.ForeignKey(
    CustomUser,
    on_delete=models.PROTECT,
    related_name='created_contracts',
    verbose_name=_('تم الإنشاء بواسطة')
  )
  created_at = models.DateTimeField(
    auto_now_add=True,
  )
  updated_at = models.DateTimeField(
    auto_now=True,
  )
  signed_by_landlord = models.ForeignKey(
    CustomUser,
    on_delete=models.PROTECT,
    related_name='signed_landlord_contracts',
    limit_choices_to={'user_type__in': ['INVESTOR', 'OWNER']},
    verbose_name=_('موقع من المالك')
  )
  signed_by_tenant = models.ForeignKey(
    CustomUser,
    on_delete=models.PROTECT,
    related_name='signed_tenant_contracts',
    limit_choices_to={'user_type': 'TENANT'},
    verbose_name=_('موقع من المستأجر')
  )
  signed_at = models.DateTimeField(
    blank=True,
    null=True,
    verbose_name=_('تاريخ التوقيع')
  )

  class Meta:
    verbose_name = _('عقد إيجار')
    verbose_name_plural = _('عقود الإيجار')
    ordering = ['-start_date']
    permissions = [
      ('can_sign_contract', _('يمكنه توقيع العقود'))
    ]

  def __str__(self):
    return f"{self.contract_number} - {self.unit} - {self.tenant}"

  def save(self, *args, **kwargs):
    if not self.contract_number:
      last_contract = Contract.objects.order_by('-id').first()
      last_id = last_contract.id if last_contract else 0
      self.contract_number = f"CNT-{last_id + 1:04d}"
    if self.pk:
      original = Contract.objects.get(pk=self.pk)
      if original.status != self.status:
        if self.status == 'ACTIVE':
          self.unit.status = 'OCCUPIED'
          self.unit.save()
        elif self.status in ['EXPIRED', 'TERMINATED']:
          self.unit.status = 'VACANT'
          self.unit.save()
        super().save(*args, **kwargs)
  @property
  def is_active(self):
    return self.status == 'ACTIVE' and self.start_date <= timezone.now().date() <= self.end_date
  @property
  def remainig_days(self):
    if self.is_active:
      return (self.end_date - timezone.now().date()).days
    return 0

class ContractDocument(models.Model):
  contract = models.ForeignKey(
    Contract,
    on_delete=models.CASCADE,
    related_name='documents',
    verbose_name=_('العقد')
  )
  document = models.FileField(
    upload_to='contracts_documents/',
    verbose_name=_('الملف')
  )
  description = models.CharField(
    max_length=200,
    verbose_name=_('وصف الملف')
  )
  uploaded_at = models.DateTimeField(
    auto_now_add=True,
  )

  class Meta:
    verbose_name = _('ملف العقد')
    verbose_name_plural = _('ملفات العقود')

  def __str__(self):
    return f"ملف لـ {self.contract}"

class ContractAmendment(models.Model):
  contract = models.ForeignKey(
    Contract,
    on_delete=models.CASCADE,
    related_name='amendments',
    verbose_name=_('العقد الاصلي')
  )
  amendment_number = models.CharField(
    max_length=20,
    unique=True,
    verbose_name=_('رقم التعديل')
  )
  reason = models.CharField(
    max_length=200,
    verbose_name=_('سبب التعديل')
  )
  changes = models.TextField(
    verbose_name=_('التغييرات المطبقة')
  )
  new_monthly_rent = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    null=True,
    blank=True,
    verbose_name=_('الإيجار الشهري الجديد (ر.ع.)'),
  )
  new_end_date = models.DateField(
    null=True,
    blank=True,
    verbose_name=_('تاريخ الانتهاء الجديد')
  )
  created_by = models.ForeignKey(
    CustomUser,
    on_delete=models.PROTECT,
    verbose_name=_('تم الإنشاء بواسطة')
  )
  created_at = models.DateTimeField(
    auto_now_add=True,
  )
  approved = models.BooleanField(
    default=False,
    verbose_name=_('تمت الموافقة')
  )
  approved_by = models.ForeignKey(
    CustomUser,
    on_delete=models.PROTECT,
    null=True,
    blank=True,
    related_name='approved_amendments',
    verbose_name=_('تمت الموافقة بواسطة')
  )
  approved_at = models.DateTimeField(
    null=True,
    blank=True,
    verbose_name=_('تاريخ الموافقة')
  )

  class Meta:
    verbose_name = _('تعديل العقد')
    verbose_name_plural = _('تعديلات العقود')
    ordering = ['-created_at']
    unique_together = ('contract', 'amendment_number')

  def __str__(self):
    return f"تعديل لـ {self.contract} - {self.amendment_number}"

class ContractTermination(models.Model):
  contract = models.ForeignKey(
    Contract,
    on_delete=models.CASCADE,
    related_name='terminations',
    verbose_name=_('العقد')
  )
  termination_date = models.DateField(
    verbose_name=_('تاريخ الإنهاء')
  )
  reason = models.CharField(
    max_length=200,
    verbose_name=_('سبب الإنهاء')
  )
  penalty_amount = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    verbose_name=_('مبلغ الغرامة (ر.ع.)'),
  )
  refund_amount = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    verbose_name=_('مبلغ الاسترداد (ر.ع.)'),
  )
  notes = models.TextField(
    blank=True,
    verbose_name=_('ملاحظات')
  )
  initiated_by = models.ForeignKey(
    CustomUser,
    on_delete=models.PROTECT,
    related_name='initiated_terminations',
    verbose_name=_('تم البدء بواسطة')
  )
  approved_by = models.ForeignKey(
    CustomUser,
    on_delete=models.PROTECT,
    related_name='approved_terminations',
    verbose_name=_('تمت الموافقة بواسطة')
  )
  created_at = models.DateTimeField(
    auto_now_add=True,
  )

  class Meta:
    verbose_name = _('إنهاء العقد')
    verbose_name_plural = _('إنهاءات العقود')
    ordering = ['-termination_date']

  def __str__(self):
    return f"إنهاء عقد{self.contract}"
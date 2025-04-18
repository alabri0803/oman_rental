from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import CustomUser

# Create your models here.

class Building(models.Model):
  name = models.CharField(
    max_length=100,
    verbose_name=_('اسم المبني'),
  )
  location = models.CharField(
    max_length=255,
    verbose_name=_('الموقع'),
  )
  city = models.CharField(
    max_length=50,
    verbose_name=_('المدينة'),
  )
  total_floors = models.PositiveIntegerField(
    verbose_name=_('عدد الطوابق'),
  )
  owner = models.ForeignKey(
    CustomUser,
    on_delete=models.CASCADE,
    limit_choices_to={'user_type': 'INVESTOR'},
    verbose_name=_('المالك'),
  )
  description = models.TextField(
    blank=True,
    verbose_name=_('وصف المبني'),
  )
  created_at = models.DateTimeField(
    auto_now_add=True,
  )
  updated_at = models.DateTimeField(
    auto_now=True,
  )

  class Meta:
    verbose_name = _('مبني')
    verbose_name_plural = _('المباني')
    ordering = ['-created_at']

  def __str__(self):
    return f"{self.name} - {self.location}"

class UnitType(models.Model):
  name = models.CharField(
    max_length=50,
    verbose_name=_('نوع الوحدة'),
  )
  description = models.TextField(
    blank=True,
    verbose_name=_('الوصف'),
  )

  class Meta:
    verbose_name = _('نوع الوحدة')
    verbose_name_plural = _('أنواع الوحدات')

  def __str__(self):
    return self.name

class Unit(models.Model):
  UNIT_STATUS = (
    ('VACANT', _('شاغرة')),
    ('OCCUPIED', _('مشغولة')),
    ('UNDER_MAINTENANCE', _('قيد الصيانة')),
  )
  building = models.ForeignKey(
    Building,
    on_delete=models.CASCADE,
    verbose_name=_('المبني'),
  )
  unit_type = models.ForeignKey(
    UnitType,
    on_delete=models.CASCADE,
    verbose_name=_('نوع الوحدة'),
  )
  unit_number = models.CharField(
    max_length=20,
    verbose_name=_('رقم الوحدة')
  )
  floor = models.PositiveIntegerField(
    verbose_name=_('الطابق'),
  )
  area = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    verbose_name=_('المساحة'),
    validators=[MinValueValidator(0)],
  )
  monthly_rent = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    verbose_name=_('الإيجار الشهري (ر.ع.)'),
    validators=[MinValueValidator(0)],
  )
  status = models.CharField(
    max_length=20,
    choices=UNIT_STATUS,
    default='VACANT',
    verbose_name=_('الحالة'),
  )
  features = models.TextField(
    blank=True,
    verbose_name=_('المميزات'),
  )
  created_at = models.DateTimeField(
    auto_now_add=True,
  )
  updated_at = models.DateTimeField(
    auto_now=True,
  )

  class Meta:
    verbose_name = _('وحدة')
    verbose_name_plural = _('الوحدات')
    ordering = ['building', 'floor', 'unit_number']
    unique_together = ('building', 'unit_number')

  def __str__(self):
    return f"{self.building.name} - {self.unit_type} {self.unit_number}"

class UnitImage(models.Model):
  unit = models.ForeignKey(
    Unit,
    on_delete=models.CASCADE,
    related_name='images',
    verbose_name=_('الوحدة'),
  )
  image = models.ImageField(
    upload_to='unit_images/',
    verbose_name=_('صورة'),
  )
  caption = models.CharField(
    max_length=100,
    blank=True,
    verbose_name=_('وصف الصورة'),
  )
  is_featured = models.BooleanField(
    default=False,
    verbose_name=_('صورة رئيسية'),
  )

  class Meta:
    verbose_name = _('صورة الوحدة')
    verbose_name_plural = _('صور الوحدات')

  def __str__(self):
    return f"صورة لـ {self.unit}"
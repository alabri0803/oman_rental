import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from .models import Building, Unit


class BuildingTable(tables.Table):
  actions = tables.TemplateColumn(
    template_name='properties/building_actions.html',
    verbose_name=_('إجراءات'),
    orderable=False,
  )

  class Meta:
    model = Building
    template_name = 'django_tables2/bootstrap4.html'
    fields = ('name', 'location', 'city', 'total_floors', 'owner')
    attrs = {'class': 'table table-striped table-bordered'}

class UnitTable(tables.Table):
  building = tables.Column(accessor='building.name', verbose_name=_('المبنى'))
  unit_type = tables.Column(accessor='unit_type.name', verbose_name=_('نوع الوحدة'))
  status = tables.Column(verbose_name=_('الحالة'))
  actions = tables.TemplateColumn(
    template_name='properties/unit_actions.html',
    verbose_name=_('إجراءات'),
    orderable=False,
  )

  class Meta:
    model = Unit
    template_name = 'django_tables2/bootstrap4.html'
    fields = ('unit_number', 'building', 'unit_type', 'floor', 'area', 'monthly_rent', 'status')
    attrs = {'class': 'table table-striped table-bordered'}
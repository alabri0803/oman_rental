from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
  CreateView,
  DeleteView,
  DetailView,
  ListView,
  UpdateView,
)
from django.views.generic.edit import FormMixin

from .forms import BuildingForm, UnitForm, UnitImageForm
from .models import Building, Unit, UnitImage, UnitType

# Create your views here.

class BuildingListView(LoginRequiredMixin, ListView):
  model = Building
  template_name = 'properties/building_list.html'
  context_object_name = 'buildings'
  
  def get_queryset(self):
    queryset = super().get_queryset()
    if self.request.user.user_type == 'INVESTOR':
      return queryset.filter(owner=self.request.user)
    return queryset

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('قائمة المباني')
    return context

class BuildingDetailView(LoginRequiredMixin, DetailView):
  model = Building
  template_name = 'properties/building_detail.html'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('تفاصيل المبنى')
    context['units'] = Unit.objects.filter(building=self.object)
    return context

class BuildingCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
  model = Building
  form_class = BuildingForm
  template_name = 'properties/building_form.html'
  success_url = reverse_lazy('properties:building_list')

  def test_func(self):
    return self.request.user.user_type in ['INVESTOR', 'ADMIN']

  def form_valid(self, form):
    form.instance.owner = self.request.user
    return super().form_valid(form)

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('إضافة مبنى جديد')
    return context

class BuildingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
  model = Building
  form_class = BuildingForm
  template_name = 'properties/building_form.html'

  def test_func(self):
    building = self.get_object()
    return self.request.user == building.owner or self.request.user.user_type == 'ADMIN'

  def get_success_url(self):
    return reverse_lazy('properties:building_detail', kwargs={'pk': self.object.pk})

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('تعديل بيانات المبنى')
    return context


class BuildingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
  model = Building
  template_name = 'properties/building_confirm_delete.html'
  success_url = reverse_lazy('properties:building_list')

  def test_func(self):
    building = self.get_object()
    return self.request.user == building.owner or self.request.user.user_type == 'ADMIN'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('حذف المبنى')
    return context

class UnitTypeListView(LoginRequiredMixin, ListView):
  model = UnitType
  template_name = 'properties/unit_type_list.html'
  context_object_name = 'unit_types'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('أنواع الوحدات')
    return context

class UnitListView(LoginRequiredMixin, ListView):
  model = Unit
  template_name = 'properties/unit_list.html'
  context_object_name = 'units'

  def get_queryset(self):
    queryset = super().get_queryset()
    building_id = self.request.GET.get('building')
    unit_type_id = self.request.GET.get('unit_type')
    status = self.request.GET.get('status')
    if building_id:
      queryset = queryset.filter(building_id=building_id)
    if unit_type_id:
      queryset = queryset.filter(unit_type_id=unit_type_id)

    if status:
      queryset = queryset.filter(status=status)

    if self.request.user.user_type == 'INVESTOR':
      queryset = queryset.filter(building__owner=self.request.user)
    return queryset

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('قائمة الوحدات')
    context['buildings'] = Building.objects.all()
    context['unit_types'] = UnitType.objects.all()
    return context

class UnitDetailView(FormMixin, LoginRequiredMixin, DetailView):
  model = Unit
  template_name = 'properties/unit_detail.html'
  form_class = UnitImageForm

  def get_success_url(self):
    return reverse_lazy('properties:unit_detail', kwargs={'pk': self.object.pk})

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('تفاصيل الوحدة')
    context['images'] = UnitImage.objects.filter(unit=self.object)
    context['form'] = self.get_form()
    return context

  def post(self, request, *args, **kwargs):
    self.object = self.get_object()
    form = self.get_form()
    if form.is_valid():
      return self.form_valid(form)
    else:
      return self.form_invalid(form)

  def form_valid(self, form):
    image = form.save(commit=False)
    image.unit = self.object
    image.save()
    return super().form_valid(form)

class UnitCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
  model = Unit
  form_class = UnitForm
  template_name = 'properties/unit_form.html'

  def test_func(self):
    return self.request.user.user_type in ['INVESTOR', 'ADMIN']

  def get_form_kwargs(self):
    kwargs = super().get_form_kwargs()
    kwargs['user'] = self.request.user
    return kwargs

  def get_success_url(self):
    return reverse_lazy('properties:unit_detail', kwargs={'pk': self.object.pk})

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('إضافة وحدة جديدة')
    return context

class UnitUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
  model = Unit
  form_class = UnitForm
  template_name = 'properties/unit_form.html'

  def test_func(self):
    unit = self.get_object()
    return self.request.user == unit.building.owner or self.request.user.user_type == 'ADMIN'

  def get_form_kwargs(self):
    kwargs = super().get_form_kwargs()
    kwargs['user'] = self.request.user
    return kwargs

  def get_success_url(self):
    return reverse_lazy('properties:unit_detail', kwargs={'pk': self.object.pk})

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('تعديل بيانات الوحدة')
    return context

class UnitDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
  model = Unit
  template_name = 'properties/unit_confirm_delete.html'
  success_url = reverse_lazy('properties:unit_list')

  def test_func(self):
    unit = self.get_object()
    return self.request.user == unit.building.owner or self.request.user.user_type == 'ADMIN'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('حذف الوحدة')
    return context

def delete_unit_images(request, pk):
  image = get_object_or_404(UnitImage, pk=pk)
  unit = image.unit
  if request.user == unit.building.owner or request.user.user_type == 'ADMIN':
    image.delete()
  return redirect('properties:unit_detail', pk=unit.pk)


from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
  CreateView,
  DeleteView,
  DetailView,
  ListView,
  UpdateView,
)

from .forms import (
  ContractAmendmentForm,
  ContractDocument,
  ContractForm,
  ContractSignForm,
  ContractTerminationForm,
)
from .models import Contract, ContractAmendment, ContractDocument, ContractTermination

# Create your views here.

class ContractListView(LoginRequiredMixin, ListView):
  model = Contract
  template_name = 'contracts/contract_list.html'
  context_object_name = 'contracts'

  def get_queryset(self):
    queryset = super().get_queryset()
    status = self.request.GET.get('status')
    if status:
      queryset = queryset.filter(status=status)
    if self.request.user.user_type == 'TENANT':
      queryset = queryset.filter(tenant=self.request.user)
    elif self.request.user.user_type in ['INVESTOR', 'OWNER']:
      return queryset.filter(unit__building__owner=self.request.user)
    return queryset

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('قائمة العقود')
    return context

class ContractDetailView(LoginRequiredMixin, DetailView):
  model = Contract
  template_name = 'contracts/contract_detail.html'
  context_object_name = 'contract'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('تفاصيل العقد')
    context['documents'] = ContractDocument.objects.filter(contract=self.object)
    context['amendments'] = ContractAmendment.objects.filter(contract=self.object)
    context['can_sign'] = self.can_user_sign()
    context['sign_form'] = ContractSignForm(contract=self.object, user=self.request.user)
    return context

  def can_user_sign(self):
    contract = self.get_object()
    user = self.request.user
    if contract.status != 'PENDING':
      return False
    if user.user_type in ['INVESTOR', 'OWNER'] and not contract.signed_by_landlord:
      return True
    if user.user_type == 'TENANT' and not contract.signed_by_tenant:
      return True
    return False

class ContractCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
  model = Contract
  form_class = ContractForm
  template_name = 'contracts/contract_form.html'

  def test_func(self):
    return self.request.user.user_type in ['INVESTOR', 'OWNER', 'ADMIN']

  def form_valid(self, form):
    form.instance.created_by = self.request.user
    form.instance.status = 'DRAFT'
    return super().form_valid(form)

  def get_success_url(self):
    return reverse_lazy('contracts:contract_detail', kwargs={'pk': self.object.pk})

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('إنشاء عقد جديد')
    return context

class ContractUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
  model = Contract
  form_class = ContractForm
  template_name = 'contracts/contract_form.html'

  def test_func(self):
    reurn (self.request.user == self.get_object().created_by or self.request.user.user_type == 'ADMIN' or self.request.user == contract.unit.building.owner)

  def get_success_url(self):
    return reverse_lazy('contracts:contract_detail', kwargs={'pk': self.object.pk})

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('تعديل العقد')
    return context

class ContractDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
  model = Contract
  template_name = 'contracts/contract_confirm_delete.html'
  success_url = reverse_lazy('contracts:contract_list')

  def test_func(self):
    contract = self.get_object()
    return (self.request.user == contract.created_by or self.request.user.user_type == 'ADMIN' or self.request.user == contract.unit.building.owner)

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('حذف العقد')
    return context

class ContractSubmitView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
  model = Contract
  fields = []
  template_name = 'contracts/contract_submit.html'

  def test_func(self):
    contract = self.get_object()
    return (self.request.user == contract.created_by or self.request.user.user_type == 'ADMIN' or self.request.user == contract.unit.building.owner)

  def form_valid(self, form):
    form.instance.status = 'PENDING'
    messages.success(self.request, _('تم إرسال العقد للتوقيع بنجاح بانتظار التوقيع.'))
    return super().form_valid(form)

  def get_success_url(self):
    return reverse_lazy('contracts:contract_detail', kwargs={'pk': self.object.pk})

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('إرسال العقد للتوقيع')
    return context

class ContractSignView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
  model = Contract
  form_class = ContractSignForm
  template_name = 'contracts/contract_sign.html'

  def test_func(self):
    contract = self.get_object()
    user = self.request.user
    if contract.status != 'PENDING':
      return False
    if user.user_type in ['INVESTOR', 'OWNER'] and not contract.signed_by_landlord:
      return True
    if user.user_type == 'TENANT' and not contract.signed_by_tenant:
      return True
    return False

  def form_valid(self, form):
    sign_as = form.cleaned_data['sign_as']
    if sign_as == 'landlord':
      form.instance.signed_by_landlord = self.request.user
    elif sign_as == 'tenant':
      form.instance.signed_by_tenant = self.request.user
    if form.instance.signed_by_landlord and form.instance.signed_by_tenant:
      form.instance.status = 'ACTIVE'
      form.instance.signed_at = timezone.now()
      self.object.unit.status = 'OCCUPIED'
      self.object.unit.save()
    messages.success(self.request, _('تم توقيع العقد بنجاح.'))
    return super().form_valid(form)

  def get_success_url(self):
    return reverse_lazy('contracts:contract_detail', kwargs={'pk': self.object.pk})

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('توقيع العقد')
    context['sign_as'] = 'landlord' if self.request.user.user_type in ['INVESTOR', 'OWNER'] else 'tenant'
    return context

class ContractDocumentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
  model = ContractDocument
  #form_class = ContractDocumentForm
  template_name = 'contracts/document_form.html'

  def test_func(self):
    contract = get_object_or_404(Contract, pk=self.kwargs['contract_pk'])
    return (self.request.user == contract.created_by or self.request.user.user_type == 'ADMIN' or self.request.user == contract.unit.building.owner)

  def form_valid(self, form):
    form.instance.contract = get_object_or_404(Contract, pk=self.kwargs['contract_pk'])
    return super().form_valid(form)

  def get_success_url(self):
    return reverse_lazy('contracts:contract_detail', kwargs={'pk': self.kwargs['contract_pk']})

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('إضافة مستند للعقد')
    context['contract'] = get_object_or_404(Contract, pk=self.kwargs['contract_pk'])
    return context

class ContractDocumentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
  model = ContractDocument
  template_name = 'contracts/document_confirm_delete.html'

  def test_func(self):
    document = self.get_object()
    return (self.request.user == document.contract.created_by or self.request.user.user_type == 'ADMIN' or self.request.user == document.contract.unit.building.owner)

  def get_success_url(self):
    return reverse_lazy('contracts:contract_detail', kwargs={'pk': self.object.contract.pk})

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('حذف المستند العقد')
    return context

class ContractAmendmentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
  model = ContractAmendment
  form_class = ContractAmendmentForm
  template_name = 'contracts/amendment_form.html'

  def test_func(self):
    contract = get_object_or_404(Contract, pk=self.kwargs['contract_pk'])
    return (self.request.user == contract.created_by or self.request.user.user_type == 'ADMIN' or self.request.user == contract.unit.building.owner)

  def form_valid(self, form):
    contract = get_object_or_404(Contract, pk=self.kwargs['contract_pk'])
    last_amendment = ContractAmendment.objects.filter(contract=contract).order_by('-amendment_number').first()
    form.instance.contract = contract
    form.instance.amendment_number = last_amendment.amendment_number + 1 if last_amendment else 1
    form.instance.created_by = self.request.user
    return super().form_valid(form)

  def get_success_url(self):
    return reverse_lazy('contracts:contract_detail', kwargs={'pk': self.kwargs['contract_pk']})

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('إنشاء تعديل للعقد')
    context['contract'] = get_object_or_404(Contract, pk=self.kwargs['contract_pk'])
    return context

class ContractTerminationCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
  model = ContractTermination
  form_class = ContractTerminationForm
  template_name = 'contracts/termination_form.html'

  def test_func(self):
    contract = get_object_or_404(Contract, pk=self.kwargs['contract_pk'])
    return (self.request.user == contract.created_by or self.request.user.user_type == 'ADMIN' or self.request.user == contract.unit.building.owner)

  def form_valid(self, form):
    contract = get_object_or_404(Contract, pk=self.kwargs['contract_pk'])
    form.instance.contract = contract
    form.instance.initiated_by = self.request.user
    return super().form_valid(form)

  def get_success_url(self):
    return reverse_lazy('contracts:contract_detail', kwargs={'pk': self.kwargs['contract_pk']})

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('إنهاء العقد')
    context['contract'] = get_object_or_404(Contract, pk=self.kwargs['contract_pk'])
    return context

def approve_amendment(request, pk):
  amendment = get_object_or_404(ContractAmendment, pk=pk)
  if request.user.has_perm('contracts.can_sign_contract') and not amendment.approved:
    amendment.approved = True
    amendment.approved_by = request.user
    amendment.approved_at = timezone.now()
    amendment.save()
    if amendment.new_monthly_rent:
      amendment.contract.monthly_rent = amendment.new_monthly_rent
    if amendment.new_end_date:
      amendment.contract.end_date = amendment.new_end_date
    amendment.contract.save()
    messages.success(request, _('تمت الموافقة على التعديل بنجاح.'))
    return redirect('contracts:contract_detail', pk=amendment.contract.pk)

def approve_termination(request, pk):
  termination = get_object_or_404(ContractTermination, pk=pk)
  if request.user.user_type in ['INVESTOR', 'OWNER', 'ADMIN']:
    termination.approved_by = request.user
    termination.save()
    contract = termination.contract
    contract.status = 'TERMINATED'
    contract.unit.status = 'VACANT'
    contract.unit.save()
    contract.save()
    messages.success(request, _('تمت الموافقة على إنهاء العقد بنجاح.'))
    return redirect('contracts:contract_detail', pk=contract.pk)
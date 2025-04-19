from django.urls import path

from .views import (
  ContractAmendmentCreateView,
  ContractCreateView,
  ContractDeleteView,
  ContractDetailView,
  ContractDocumentCreateView,
  ContractDocumentDeleteView,
  ContractListView,
  ContractSignView,
  ContractSubmitView,
  ContractTerminationCreateView,
  ContractUpdateView,
  approve_amendment,
  approve_termination,
)

app_name = 'contracts'

urlpatterns = [
  path('', ContractListView.as_view(), name='contract_list'),
  path('<uuid:pk>/', ContractDetailView.as_view(), name='contract_detail'),
  path('create/', ContractCreateView.as_view(), name='contract_create'),
  path('<uuid:pk>/update/', ContractUpdateView.as_view(), name='contract_update'),
  path('<uuid:pk>/delete/', ContractDeleteView.as_view(), name='contract_delete'),
  path('<uuid:pk>/submit/', ContractSubmitView.as_view(), name='contract_submit'),
  path('<uuid:pk>/sign/', ContractSignView.as_view(), name='contract_sign'),
  path('<uuid:contract_pk>/documents/create/', ContractDocumentCreateView.as_view(), name='contract_document_create'),
  path('documents/<int:pk>/delete/', ContractDocumentDeleteView.as_view(), name='contract_document_delete'),
  path('<uuid:contract_pk>/amendments/create/', ContractAmendmentCreateView.as_view(), name='contract_amendment_create'),
  path('<uuid:contract_pk>/terminations/create/', ContractTerminationCreateView.as_view(), name='contract_termination_create'),
  path('amendments/<int:pk>/approve/', approve_amendment, name='approve_amendment'),
  path('terminations/<int:pk>/approve/', approve_termination, name='approve_termination'),
]
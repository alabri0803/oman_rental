from django.urls import path

from .views import (
  BuildingCreateView,
  BuildingDeleteView,
  BuildingDetailView,
  BuildingListView,
  BuildingUpdateView,
  UnitCreateView,
  UnitDeleteView,
  UnitDetailView,
  UnitListView,
  UnitTypeListView,
  UnitUpdateView,
  delete_unit_images,
)

app_name = 'properties'

urlpatterns = [
  path('buildings/', BuildingListView.as_view(), name='building_list'),
  path('buildings/<int:pk>/', BuildingDetailView.as_view(), name='building_detail'),
  path('buildings/add/', BuildingCreateView.as_view(), name='building_create'),
  path('buildings/<int:pk>/edit/', BuildingUpdateView.as_view(), name='building_update'),
  path('buildings/<int:pk>/delete/', BuildingDeleteView.as_view(), name='building_delete'),
  
  path('unit-types/', UnitTypeListView.as_view(), name='unit_type_list'),
  
  path('units/', UnitListView.as_view(), name='unit_list'),
  path('units/<int:pk>/', UnitDetailView.as_view(), name='unit_detail'),
  path('units/add/', UnitCreateView.as_view(), name='unit_create'),
  path('units/<int:pk>/edit/', UnitUpdateView.as_view(), name='unit_update'),
  path('units/<int:pk>/delete/', UnitDeleteView.as_view(), name='unit_delete'),
  path('units/images/<int:pk>/delete/', delete_unit_images, name='delete_unit_images'),
]
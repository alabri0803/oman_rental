from django.contrib import admin

from .models import Building, Unit, UnitImage, UnitType

# Register your models here.

class UnitImageInline(admin.TabularInline):
  model = UnitImage
  extra = 1

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
  list_display = ('name', 'location', 'city', 'owner', 'total_floors')
  list_filter = ('city', 'owner')
  search_fields = ('name', 'location', 'city')
  ordering = ('name',)

@admin.register(UnitType)
class UnitTypeAdmin(admin.ModelAdmin):
  list_display = ('name',)
  search_fields = ('name',)

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
  list_display = ('unit_number', 'building', 'unit_type', 'floor', 'area', 'monthly_rent', 'status')
  list_filter = ('building', 'unit_type', 'status', 'floor')
  search_fields = ('unit_number', 'building__name', 'unit_type__name', 'features')
  inlines = [UnitImageInline]
  ordering = ('building', 'floor', 'unit_number')

@admin.register(UnitImage)
class UnitImageAdmin(admin.ModelAdmin):
  list_display = ('unit', 'image', 'is_featured')
  list_filter = ('is_featured',)
  search_fields = ('unit__unit_number', 'caption')
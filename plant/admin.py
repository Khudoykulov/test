from django.contrib import admin
from .models import PlantType, Plant, IrrigationEvent, PlantCareLog, IrrigationZone


@admin.register(PlantType)
class PlantTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'scientific_name', 'icon', 'optimal_soil_moisture_min', 'optimal_soil_moisture_max']
    search_fields = ['name', 'scientific_name']


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ['name', 'plant_type', 'location', 'growth_stage', 'health_status', 'planted_date']
    list_filter = ['plant_type', 'growth_stage', 'health_status', 'planted_date']
    search_fields = ['name', 'plant_id', 'location']
    date_hierarchy = 'planted_date'


@admin.register(IrrigationEvent)
class IrrigationEventAdmin(admin.ModelAdmin):
    list_display = ['plant', 'event_type', 'status', 'scheduled_time', 'duration_minutes', 'water_amount_ml']
    list_filter = ['event_type', 'status', 'scheduled_time']
    search_fields = ['plant__name', 'trigger_reason']
    date_hierarchy = 'scheduled_time'


@admin.register(PlantCareLog)
class PlantCareLogAdmin(admin.ModelAdmin):
    list_display = ['plant', 'care_type', 'care_date', 'description']
    list_filter = ['care_type', 'care_date']
    search_fields = ['plant__name', 'description']
    date_hierarchy = 'care_date'


@admin.register(IrrigationZone)
class IrrigationZoneAdmin(admin.ModelAdmin):
    list_display = ['zone_id', 'name', 'status', 'area_sqm', 'plant_count', 'last_irrigated']
    list_filter = ['status', 'soil_type']
    search_fields = ['zone_id', 'name', 'description']
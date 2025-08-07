from django.contrib import admin
from .models import SensorType, Sensor, SensorReading, WeatherData, SystemStatus


@admin.register(SensorType)
class SensorTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit', 'icon', 'description']
    search_fields = ['name']


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ['name', 'sensor_id', 'sensor_type', 'location', 'status', 'last_updated']
    list_filter = ['sensor_type', 'status', 'is_critical']
    search_fields = ['name', 'sensor_id', 'location']


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ['sensor', 'value', 'timestamp', 'is_anomaly']
    list_filter = ['sensor', 'is_anomaly', 'timestamp']
    search_fields = ['sensor__name']
    date_hierarchy = 'timestamp'


@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ['location', 'temperature', 'humidity', 'weather_condition', 'timestamp']
    list_filter = ['location', 'weather_condition', 'timestamp']
    date_hierarchy = 'timestamp'


@admin.register(SystemStatus)
class SystemStatusAdmin(admin.ModelAdmin):
    list_display = ['status', 'cpu_usage', 'memory_usage', 'active_sensors', 'timestamp']
    list_filter = ['status', 'timestamp']
    date_hierarchy = 'timestamp'
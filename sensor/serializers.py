from rest_framework import serializers
from .models import Sensor, SensorType, SensorReading, WeatherData, SystemStatus, WeatherForecast


class SensorTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorType
        fields = '__all__'


class SensorReadingSerializer(serializers.ModelSerializer):
    sensor_name = serializers.CharField(source='sensor.name', read_only=True)
    sensor_unit = serializers.CharField(source='sensor.sensor_type.unit', read_only=True)
    sensor_icon = serializers.CharField(source='sensor.sensor_type.icon', read_only=True)
    
    class Meta:
        model = SensorReading
        fields = ['id', 'sensor', 'sensor_name', 'sensor_unit', 'sensor_icon', 
                 'value', 'timestamp', 'is_anomaly']


class SensorSerializer(serializers.ModelSerializer):
    sensor_type_name = serializers.CharField(source='sensor_type.name', read_only=True)
    sensor_type_unit = serializers.CharField(source='sensor_type.unit', read_only=True)
    sensor_type_icon = serializers.CharField(source='sensor_type.icon', read_only=True)
    latest_reading = serializers.SerializerMethodField()
    
    class Meta:
        model = Sensor
        fields = ['id', 'sensor_id', 'name', 'sensor_type', 'sensor_type_name', 
                 'sensor_type_unit', 'sensor_type_icon', 'location', 'depth', 
                 'status', 'last_updated', 'is_critical', 'latest_reading']
    
    def get_latest_reading(self, obj):
        latest = obj.get_latest_reading()
        if latest:
            return {
                'value': latest.value,
                'timestamp': latest.timestamp,
                'is_anomaly': latest.is_anomaly
            }
        return None


class WeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherData
        fields = '__all__'


class WeatherForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherForecast
        fields = '__all__'


class SystemStatusSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = SystemStatus
        fields = ['id', 'status', 'status_display', 'cpu_usage', 'memory_usage', 
                 'disk_usage', 'internet_connectivity', 'active_sensors', 
                 'last_ai_analysis', 'timestamp']


class DashboardDataSerializer(serializers.Serializer):
    """Serializer for dashboard data aggregation"""
    system_status = SystemStatusSerializer()
    sensors = SensorSerializer(many=True)
    weather = WeatherDataSerializer()
    critical_alerts = serializers.ListField()
    statistics = serializers.DictField()
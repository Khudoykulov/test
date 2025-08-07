from django.db import models
from django.utils import timezone
import random


class SensorType(models.Model):
    """Model for different types of sensors"""
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20)  # %, °C, mm, etc.
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='📡')
    
    def __str__(self):
        return f"{self.name} ({self.unit})"


class Sensor(models.Model):
    """Model for individual sensors"""
    SENSOR_STATUS_CHOICES = [
        ('active', 'Faol'),
        ('inactive', 'Nofaol'),
        ('maintenance', 'Kalibrlash'),
        ('error', 'Xato'),
    ]
    
    sensor_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    sensor_type = models.ForeignKey(SensorType, on_delete=models.CASCADE)
    location = models.CharField(max_length=200)
    depth = models.FloatField(null=True, blank=True)  # for soil sensors
    status = models.CharField(max_length=20, choices=SENSOR_STATUS_CHOICES, default='active')
    last_updated = models.DateTimeField(auto_now=True)
    is_critical = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.location}"
    
    def get_latest_reading(self):
        """Get the latest sensor reading"""
        return self.readings.filter(timestamp__gte=timezone.now() - timezone.timedelta(minutes=5)).first()


class SensorReading(models.Model):
    """Model for sensor readings"""
    sensor = models.ForeignKey(Sensor, related_name='readings', on_delete=models.CASCADE)
    value = models.FloatField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_anomaly = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.sensor.name}: {self.value}{self.sensor.sensor_type.unit} at {self.timestamp}"
    
    @classmethod
    def generate_random_reading(cls, sensor):
        """❌ MOCK DATA GENERATION DISABLED - REAL SENSOR APIs REQUIRED"""
        raise Exception(f"MOCK_SENSOR_DATA_DISABLED: {sensor.name} requires real sensor API integration. No mock data generation allowed.")
    
    # ❌ ALL MOCK DATA GENERATION METHODS REMOVED - REAL SENSOR APIs REQUIRED


class WeatherData(models.Model):
    """Model for weather data from external API"""
    location = models.CharField(max_length=100, default='Tashkent')
    temperature = models.FloatField()
    humidity = models.FloatField()
    pressure = models.FloatField()
    wind_speed = models.FloatField()
    wind_direction = models.CharField(max_length=20)
    rainfall = models.FloatField(default=0)
    solar_radiation = models.FloatField(null=True, blank=True)
    weather_condition = models.CharField(max_length=100)
    icon = models.CharField(max_length=10)
    
    # Qo'shimcha yangi maydonlar
    visibility = models.FloatField(default=10000)  # Visibility in meters
    uv_index = models.FloatField(null=True, blank=True)  # UV Index
    air_quality_index = models.IntegerField(null=True, blank=True)  # AQI
    feels_like_temperature = models.FloatField(null=True, blank=True)  # Feels like temp
    cloud_coverage = models.IntegerField(default=0)  # Cloud coverage percentage
    dew_point = models.FloatField(null=True, blank=True)  # Dew point
    wind_gust = models.FloatField(null=True, blank=True)  # Wind gust speed
    
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"Weather at {self.location}: {self.temperature}°C, {self.humidity}% humidity"


class WeatherForecast(models.Model):
    """Model for weather forecast data"""
    location = models.CharField(max_length=100, default='Tashkent')
    forecast_date = models.DateField()
    
    # Temperature data
    temp_min = models.FloatField()
    temp_max = models.FloatField()
    temp_day = models.FloatField()
    temp_night = models.FloatField()
    feels_like_day = models.FloatField(null=True, blank=True)
    feels_like_night = models.FloatField(null=True, blank=True)
    
    # Other weather parameters
    humidity = models.FloatField()
    pressure = models.FloatField()
    wind_speed = models.FloatField()
    wind_direction = models.CharField(max_length=20)
    wind_gust = models.FloatField(null=True, blank=True)
    
    # Precipitation
    rainfall = models.FloatField(default=0)
    precipitation_probability = models.IntegerField(default=0)  # percentage
    
    # Sky conditions
    weather_condition = models.CharField(max_length=100)
    weather_description = models.TextField(blank=True)
    icon = models.CharField(max_length=10)
    cloud_coverage = models.IntegerField(default=0)
    
    # Additional data
    uv_index = models.FloatField(null=True, blank=True)
    visibility = models.FloatField(default=10000)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['forecast_date']
        unique_together = ['location', 'forecast_date']
        
    def __str__(self):
        return f"Forecast for {self.location} on {self.forecast_date}: {self.temp_min}°C - {self.temp_max}°C"


class SystemStatus(models.Model):
    """Model for overall system status"""
    STATUS_CHOICES = [
        ('active', 'FAOL'),
        ('maintenance', 'TEXNIK_XIZMAT'),
        ('error', 'XATO'),
        ('offline', 'OFLAYN'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    cpu_usage = models.FloatField(default=0)
    memory_usage = models.FloatField(default=0)
    disk_usage = models.FloatField(default=0)
    internet_connectivity = models.FloatField(default=100)
    active_sensors = models.IntegerField(default=0)
    last_ai_analysis = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"System Status: {self.get_status_display()} at {self.timestamp}"
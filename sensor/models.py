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
        """Generate realistic random sensor data for testing"""
        import datetime
        current_hour = timezone.now().hour
        current_season = cls._get_current_season()
        
        # Vaqt va faslga bog'liq o'zgarishlar
        value_ranges = {
            'soil_moisture': cls._get_soil_moisture_range(current_season, sensor.is_critical),
            'soil_temperature': cls._get_soil_temperature_range(current_season, current_hour),
            'air_temperature': cls._get_air_temperature_range(current_season, current_hour),
            'air_humidity': cls._get_air_humidity_range(current_season, current_hour),
            'rainfall': cls._get_rainfall_range(current_season),
            'ph': cls._get_ph_range(sensor.location),
            'conductivity': cls._get_conductivity_range(current_season),
            'light_intensity': cls._get_light_intensity_range(current_hour, current_season),
        }
        
        sensor_type_key = sensor.sensor_type.name.lower().replace(' ', '_')
        if sensor_type_key in value_ranges:
            min_val, max_val = value_ranges[sensor_type_key]
            
            # Normal taqsimot bilan qiymat yaratish
            avg_val = (min_val + max_val) / 2
            std_dev = (max_val - min_val) / 6  # 99.7% qiymatlar chegarada bo'lsin
            value = random.normalvariate(avg_val, std_dev)
            value = max(min_val, min(max_val, value))  # Chegaralarda ushlab turish
            value = round(value, 2)
        else:
            value = round(random.uniform(0, 100), 2)
        
        # Anomaliya ehtimoli (1% hodisa)
        is_anomaly = random.random() < 0.01
        if is_anomaly and sensor_type_key == 'soil_moisture':
            value = random.uniform(5, 15)  # Juda quruq holat
            
        return cls.objects.create(sensor=sensor, value=value, is_anomaly=is_anomaly)
    
    @staticmethod
    def _get_current_season():
        """Joriy faslni aniqlash"""
        month = timezone.now().month
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'autumn'
    
    @staticmethod
    def _get_soil_moisture_range(season, is_critical):
        """Tuproq namligi diapazonini aniqlash"""
        if is_critical:
            # Kritik datchik - qurg'oq sharoitlarda
            base_ranges = {
                'winter': (20, 35),
                'spring': (25, 40),
                'summer': (15, 30),  # Yozda eng quruq
                'autumn': (30, 45)
            }
        else:
            # Normal datchiklar
            base_ranges = {
                'winter': (45, 70),
                'spring': (50, 75),
                'summer': (35, 60),  # Yozda pastroq
                'autumn': (55, 80)
            }
        return base_ranges[season]
    
    @staticmethod
    def _get_soil_temperature_range(season, hour):
        """Tuproq harorati diapazonini aniqlash"""
        base_ranges = {
            'winter': (5, 15),
            'spring': (12, 22),
            'summer': (20, 35),
            'autumn': (15, 25)
        }
        min_temp, max_temp = base_ranges[season]
        
        # Kun davomidagi o'zgarishlar (tuproq sekin isiydi/soviydi)
        if 6 <= hour <= 18:  # Kunduzi
            return (min_temp + 2, max_temp + 3)
        else:  # Tunda
            return (min_temp, max_temp - 2)
    
    @staticmethod
    def _get_air_temperature_range(season, hour):
        """Havo harorati diapazonini aniqlash"""
        base_ranges = {
            'winter': (0, 15),
            'spring': (15, 25),
            'summer': (25, 40),
            'autumn': (10, 20)
        }
        min_temp, max_temp = base_ranges[season]
        
        # Kun davomidagi o'zgarishlar
        if 10 <= hour <= 16:  # Eng issiq vaqt
            return (min_temp + 5, max_temp + 5)
        elif 6 <= hour <= 9 or 17 <= hour <= 20:  # O'rtacha vaqt
            return (min_temp + 2, max_temp + 2)
        else:  # Tunda
            return (min_temp, max_temp - 3)
    
    @staticmethod
    def _get_air_humidity_range(season, hour):
        """Havo namligi diapazonini aniqlash"""
        base_ranges = {
            'winter': (60, 85),
            'spring': (50, 75),
            'summer': (35, 65),
            'autumn': (55, 80)
        }
        min_hum, max_hum = base_ranges[season]
        
        # Ertalab namlik yuqori, kunduzi past
        if 5 <= hour <= 8:  # Ertalab
            return (min_hum + 10, max_hum + 5)
        elif 12 <= hour <= 17:  # Kunduzi
            return (min_hum - 10, max_hum - 15)
        else:  # Kechqurun va tunda
            return (min_hum, max_hum)
    
    @staticmethod
    def _get_rainfall_range(season):
        """Yomg'ir miqdori diapazonini aniqlash"""
        # Ko'p vaqt yomg'ir bo'lmaydi (70% holatlarda 0)
        if random.random() < 0.7:
            return (0, 0)
            
        base_ranges = {
            'winter': (0, 5),
            'spring': (2, 15),
            'summer': (5, 25),  # Yozgi yomg'irlar kuchliroq
            'autumn': (3, 12)
        }
        return base_ranges[season]
    
    @staticmethod
    def _get_ph_range(location):
        """pH diapazonini joylashuvga qarab aniqlash"""
        if 'A sektori' in location:
            return (6.2, 7.0)  # Biroz kislotali
        elif 'B sektori' in location:
            return (6.8, 7.5)  # Neutral-ishqoriy
        else:
            return (6.5, 7.2)  # Ideal diapazon
    
    @staticmethod
    def _get_conductivity_range(season):
        """O'tkazuvchanlik diapazonini aniqlash"""
        base_ranges = {
            'winter': (0.8, 1.8),
            'spring': (1.0, 2.2),
            'summer': (1.5, 2.8),  # Yozda tuz konsentratsiyasi yuqori
            'autumn': (1.2, 2.0)
        }
        return base_ranges[season]
    
    @staticmethod
    def _get_light_intensity_range(hour, season):
        """Yorug'lik intensivligi diapazonini aniqlash"""
        if hour < 6 or hour > 20:  # Tunda
            return (0, 50)
        elif 6 <= hour <= 8 or 18 <= hour <= 20:  # Tong/kech
            return (100, 400)
        elif 9 <= hour <= 17:  # Kunduzi
            base_ranges = {
                'winter': (300, 700),
                'spring': (600, 900),
                'summer': (800, 1200),
                'autumn': (400, 800)
            }
            return base_ranges[season]
        else:
            return (200, 600)


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
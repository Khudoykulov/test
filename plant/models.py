from django.db import models
from django.utils import timezone


class PlantType(models.Model):
    """Model for different types of plants"""
    name = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, default='🌱')
    
    # Optimal growing conditions
    optimal_soil_moisture_min = models.FloatField(default=60)  # %
    optimal_soil_moisture_max = models.FloatField(default=80)  # %
    optimal_temperature_min = models.FloatField(default=18)    # °C
    optimal_temperature_max = models.FloatField(default=25)    # °C
    optimal_ph_min = models.FloatField(default=6.0)
    optimal_ph_max = models.FloatField(default=7.0)
    
    # Growth stages
    germination_days = models.IntegerField(default=7)
    vegetative_days = models.IntegerField(default=30)
    flowering_days = models.IntegerField(default=60)
    maturity_days = models.IntegerField(default=90)
    
    def __str__(self):
        return self.name


class Plant(models.Model):
    """Model for individual plants or plant groups"""
    GROWTH_STAGES = [
        ('seed', 'Urug\''),
        ('germination', 'Unish'),
        ('seedling', 'Ko\'chat'),
        ('vegetative', 'Vegetativ o\'sish'),
        ('flowering', 'Gullash'),
        ('fruiting', 'Mevali'),
        ('mature', 'Pishgan'),
    ]
    
    HEALTH_STATUS = [
        ('excellent', 'A\'lo'),
        ('good', 'Yaxshi'),
        ('fair', 'O\'rtacha'),
        ('poor', 'Yomon'),
        ('critical', 'Kritik'),
    ]
    
    plant_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    plant_type = models.ForeignKey(PlantType, on_delete=models.CASCADE)
    location = models.CharField(max_length=200)
    planted_date = models.DateField()
    growth_stage = models.CharField(max_length=20, choices=GROWTH_STAGES, default='seed')
    health_status = models.CharField(max_length=20, choices=HEALTH_STATUS, default='good')
    
    # Plant metrics
    height = models.FloatField(null=True, blank=True)  # cm
    leaf_count = models.IntegerField(null=True, blank=True)
    fruit_count = models.IntegerField(null=True, blank=True)
    
    # Care tracking
    last_watered = models.DateTimeField(null=True, blank=True)
    water_amount_ml = models.IntegerField(default=0)  # Total water given
    last_fertilized = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.plant_type.name})"
    
    @property
    def days_since_planted(self):
        return (timezone.now().date() - self.planted_date).days
    
    @property
    def expected_growth_stage(self):
        days = self.days_since_planted
        if days <= self.plant_type.germination_days:
            return 'germination'
        elif days <= self.plant_type.vegetative_days:
            return 'vegetative'
        elif days <= self.plant_type.flowering_days:
            return 'flowering'
        else:
            return 'mature'
    
    @property
    def is_growth_on_track(self):
        stages_order = ['seed', 'germination', 'seedling', 'vegetative', 'flowering', 'fruiting', 'mature']
        current_index = stages_order.index(self.growth_stage)
        expected_index = stages_order.index(self.expected_growth_stage)
        return current_index >= expected_index


class IrrigationEvent(models.Model):
    """Model for irrigation events"""
    EVENT_TYPES = [
        ('automatic', 'Avtomatik'),
        ('manual', 'Qo\'lda'),
        ('scheduled', 'Rejalashtirilgan'),
        ('emergency', 'Favqulodda'),
    ]
    
    EVENT_STATUS = [
        ('scheduled', 'Rejalashtirilgan'),
        ('in_progress', 'Davom etmoqda'),
        ('completed', 'Yakunlangan'),
        ('cancelled', 'Bekor qilingan'),
        ('failed', 'Muvaffaqiyatsiz'),
    ]
    
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='irrigation_events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    status = models.CharField(max_length=20, choices=EVENT_STATUS, default='scheduled')
    
    scheduled_time = models.DateTimeField()
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    
    duration_minutes = models.IntegerField()  # Planned duration
    actual_duration_minutes = models.IntegerField(null=True, blank=True)
    water_amount_ml = models.IntegerField()  # Planned amount
    actual_water_amount_ml = models.IntegerField(null=True, blank=True)
    
    trigger_reason = models.TextField()  # Why this irrigation was triggered
    ai_confidence = models.FloatField(null=True, blank=True)  # AI confidence level
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.plant.name} - {self.get_event_type_display()} at {self.scheduled_time}"
    
    @property
    def is_overdue(self):
        if self.status == 'scheduled':
            return timezone.now() > self.scheduled_time
        return False


class PlantCareLog(models.Model):
    """Model for plant care activities log"""
    CARE_TYPES = [
        ('watering', 'Sug\'orish'),
        ('fertilizing', 'O\'g\'itlash'),
        ('pruning', 'Kesish'),
        ('pesticide', 'Zararkunandalarga qarshi'),
        ('transplanting', 'Ko\'chirish'),
        ('observation', 'Kuzatish'),
    ]
    
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='care_logs')
    care_type = models.CharField(max_length=20, choices=CARE_TYPES)
    description = models.TextField()
    care_date = models.DateTimeField(default=timezone.now)
    
    # Specific fields for different care types
    water_amount_ml = models.IntegerField(null=True, blank=True)
    fertilizer_type = models.CharField(max_length=100, blank=True)
    fertilizer_amount_g = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.plant.name} - {self.get_care_type_display()} on {self.care_date.date()}"


class IrrigationZone(models.Model):
    """Model for irrigation zones/sectors"""
    ZONE_STATUS = [
        ('active', 'Faol'),
        ('inactive', 'Nofaol'),
        ('maintenance', 'Ta\'mirlash'),
        ('error', 'Xato'),
    ]
    
    zone_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Zone specifications
    area_sqm = models.FloatField()  # Area in square meters
    plant_count = models.IntegerField(default=0)
    soil_type = models.CharField(max_length=50, default='loam')
    
    # Irrigation settings
    default_duration_minutes = models.IntegerField(default=15)
    flow_rate_lpm = models.FloatField(default=10)  # Liters per minute
    
    status = models.CharField(max_length=20, choices=ZONE_STATUS, default='active')
    last_irrigated = models.DateTimeField(null=True, blank=True)
    total_water_used_l = models.FloatField(default=0)  # Total liters used
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Zone {self.zone_id}: {self.name}"
    
    @property
    def plants_in_zone(self):
        return Plant.objects.filter(location__icontains=self.name)
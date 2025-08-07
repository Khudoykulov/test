from django.db import models
from django.utils import timezone
import json


class AIModel(models.Model):
    """Model for AI model metadata"""
    MODEL_TYPES = [
        ('irrigation_predictor', 'Sug\'orish Bashoratchi'),
        ('plant_health', 'O\'simlik Sog\'ligi'),
        ('weather_analyzer', 'Ob-havo Tahlilchi'),
        ('water_optimizer', 'Suv Optimizatori'),
    ]
    
    name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=30, choices=MODEL_TYPES)
    version = models.CharField(max_length=20, default='1.0.0')
    description = models.TextField(blank=True)
    
    # Model performance metrics
    accuracy = models.FloatField(default=0.0)  # 0-100%
    precision = models.FloatField(default=0.0)
    recall = models.FloatField(default=0.0)
    f1_score = models.FloatField(default=0.0)
    
    # Training information
    training_data_count = models.IntegerField(default=0)
    last_trained = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} v{self.version} - {self.get_model_type_display()}"


class AIPrediction(models.Model):
    """Model for AI predictions and recommendations"""
    PREDICTION_TYPES = [
        ('irrigation_need', 'Sug\'orish Zaruriyati'),
        ('optimal_timing', 'Optimal Vaqt'),
        ('water_amount', 'Suv Miqdori'),
        ('plant_health_risk', 'O\'simlik Sog\'ligi Xavfi'),
        ('weather_impact', 'Ob-havo Ta\'siri'),
        ('pest_detection', 'Zararkunanda Aniqlash'),
    ]
    
    CONFIDENCE_LEVELS = [
        ('very_low', 'Juda Past'),
        ('low', 'Past'),
        ('medium', 'O\'rtacha'),
        ('high', 'Yuqori'),
        ('very_high', 'Juda Yuqori'),
    ]
    
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE)
    prediction_type = models.CharField(max_length=30, choices=PREDICTION_TYPES)
    
    # Input data (stored as JSON)
    input_data = models.JSONField()
    
    # Prediction results
    prediction_value = models.FloatField()  # Main prediction value
    confidence_score = models.FloatField()  # 0-100%
    confidence_level = models.CharField(max_length=20, choices=CONFIDENCE_LEVELS)
    
    # Additional prediction details
    recommendation = models.TextField()
    reasoning = models.TextField(blank=True)
    alternative_actions = models.JSONField(default=dict)
    
    # Validation and feedback
    is_validated = models.BooleanField(default=False)
    actual_outcome = models.FloatField(null=True, blank=True)
    feedback_score = models.IntegerField(null=True, blank=True)  # 1-5 rating
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_prediction_type_display()} - {self.confidence_score:.1f}% confidence"
    
    @property
    def is_accurate(self):
        """Check if prediction was accurate (if actual outcome is available)"""
        if self.actual_outcome is not None:
            error_margin = abs(self.prediction_value - self.actual_outcome) / self.prediction_value
            return error_margin <= 0.15  # 15% error margin
        return None


class AIAnalysisSession(models.Model):
    """Model for AI analysis sessions"""
    SESSION_TYPES = [
        ('routine', 'Muntazam Tahlil'),
        ('triggered', 'Avtomatik Ishga Tushgan'),
        ('manual', 'Qo\'lda Boshlangan'),
        ('emergency', 'Favqulodda'),
    ]
    
    STATUS_CHOICES = [
        ('running', 'Davom etmoqda'),
        ('completed', 'Yakunlangan'),
        ('failed', 'Muvaffaqiyatsiz'),
        ('cancelled', 'Bekor qilingan'),
    ]
    
    session_id = models.CharField(max_length=50, unique=True)
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    
    # Session data
    input_sensors = models.JSONField()  # List of sensors analyzed
    weather_data = models.JSONField(null=True, blank=True)
    plant_data = models.JSONField(null=True, blank=True)
    
    # Results
    predictions_generated = models.IntegerField(default=0)
    recommendations = models.JSONField(default=list)
    critical_alerts = models.JSONField(default=list)
    
    # Performance metrics
    processing_time_seconds = models.FloatField(null=True, blank=True)
    cpu_usage_peak = models.FloatField(null=True, blank=True)
    memory_usage_peak = models.FloatField(null=True, blank=True)
    
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"AI Analysis {self.session_id} - {self.get_status_display()}"
    
    @property
    def duration_minutes(self):
        """Get session duration in minutes"""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds() / 60
        return (timezone.now() - self.started_at).total_seconds() / 60


class AILearningData(models.Model):
    """Model for storing data used for AI learning"""
    DATA_SOURCES = [
        ('sensors', 'Datchiklar'),
        ('weather', 'Ob-havo'),
        ('irrigation', 'Sug\'orish'),
        ('plant_growth', 'O\'simlik O\'sishi'),
        ('user_feedback', 'Foydalanuvchi Fikri'),
    ]
    
    source_type = models.CharField(max_length=20, choices=DATA_SOURCES)
    data_point = models.JSONField()  # The actual data
    
    # Metadata
    quality_score = models.FloatField(default=1.0)  # 0-1, data quality
    is_anomaly = models.BooleanField(default=False)
    is_validated = models.BooleanField(default=False)
    
    # Usage tracking
    used_for_training = models.BooleanField(default=False)
    training_weight = models.FloatField(default=1.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_source_type_display()} data - {self.created_at.date()}"


class AIInsight(models.Model):
    """Model for AI-generated insights and patterns"""
    INSIGHT_TYPES = [
        ('pattern_discovery', 'Naqsh Kashfiyoti'),
        ('optimization_opportunity', 'Optimizatsiya Imkoniyati'),
        ('risk_assessment', 'Xavf Baholash'),
        ('trend_analysis', 'Trend Tahlili'),
        ('correlation_finding', 'Korrelyatsiya Topish'),
    ]
    
    IMPORTANCE_LEVELS = [
        ('low', 'Past'),
        ('medium', 'O\'rtacha'),
        ('high', 'Yuqori'),
        ('critical', 'Kritik'),
    ]
    
    insight_type = models.CharField(max_length=30, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Supporting data
    supporting_data = models.JSONField()
    statistical_significance = models.FloatField(null=True, blank=True)
    confidence_level = models.FloatField(default=0.0)
    
    # Classification
    importance_level = models.CharField(max_length=20, choices=IMPORTANCE_LEVELS)
    tags = models.JSONField(default=list)  # Tags for categorization
    
    # Action items
    recommended_actions = models.JSONField(default=list)
    potential_impact = models.TextField(blank=True)
    
    # Validation
    is_implemented = models.BooleanField(default=False)
    implementation_date = models.DateTimeField(null=True, blank=True)
    outcome_rating = models.IntegerField(null=True, blank=True)  # 1-5
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} ({self.get_importance_level_display()})"
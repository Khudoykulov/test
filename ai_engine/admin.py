from django.contrib import admin
from .models import AIModel, AIPrediction, AIAnalysisSession, AILearningData, AIInsight


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_type', 'version', 'accuracy', 'is_active', 'last_trained']
    list_filter = ['model_type', 'is_active', 'last_trained']
    search_fields = ['name', 'description']


@admin.register(AIPrediction)
class AIPredictionAdmin(admin.ModelAdmin):
    list_display = ['model', 'prediction_type', 'confidence_score', 'is_validated', 'created_at']
    list_filter = ['model', 'prediction_type', 'confidence_level', 'is_validated']
    search_fields = ['recommendation', 'reasoning']
    date_hierarchy = 'created_at'


@admin.register(AIAnalysisSession)
class AIAnalysisSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'session_type', 'status', 'predictions_generated', 'started_at', 'completed_at']
    list_filter = ['session_type', 'status', 'started_at']
    search_fields = ['session_id']
    date_hierarchy = 'started_at'


@admin.register(AILearningData)
class AILearningDataAdmin(admin.ModelAdmin):
    list_display = ['source_type', 'quality_score', 'is_validated', 'used_for_training', 'created_at']
    list_filter = ['source_type', 'is_validated', 'used_for_training', 'is_anomaly']
    date_hierarchy = 'created_at'


@admin.register(AIInsight)
class AIInsightAdmin(admin.ModelAdmin):
    list_display = ['title', 'insight_type', 'importance_level', 'confidence_level', 'is_implemented', 'created_at']
    list_filter = ['insight_type', 'importance_level', 'is_implemented']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'
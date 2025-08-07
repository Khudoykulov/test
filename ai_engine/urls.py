from django.urls import path
from . import views

urlpatterns = [
    path('analyze-irrigation/', views.analyze_irrigation_need, name='analyze-irrigation'),
    path('analyze-plant-health/', views.analyze_plant_health, name='analyze-plant-health'),
    path('comprehensive-analysis/', views.comprehensive_analysis, name='comprehensive-analysis'),
    path('insights/', views.get_ai_insights, name='ai-insights'),
    path('models/status/', views.get_ai_model_status, name='ai-model-status'),
    path('analysis-history/', views.get_analysis_history, name='analysis-history'),
    path('train-model/', views.train_model, name='train-model'),
]
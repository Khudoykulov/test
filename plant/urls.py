from django.urls import path
from . import views

urlpatterns = [
    path('types/', views.PlantTypeListCreateView.as_view(), name='plant-types'),
    path('plants/', views.PlantListCreateView.as_view(), name='plants-list'),
    path('plants/<int:pk>/', views.PlantDetailView.as_view(), name='plant-detail'),
    path('irrigation-events/', views.IrrigationEventListCreateView.as_view(), name='irrigation-events'),
    path('care-logs/', views.PlantCareLogListCreateView.as_view(), name='care-logs'),
    path('zones/', views.IrrigationZoneListCreateView.as_view(), name='irrigation-zones'),
    path('irrigation-summary/', views.get_irrigation_summary, name='irrigation-summary'),
    path('health-status/', views.get_plant_health_status, name='plant-health-status'),
    path('trigger-irrigation/', views.trigger_irrigation, name='trigger-irrigation'),
    path('create-sample-plants/', views.create_sample_plants, name='create-sample-plants'),
]
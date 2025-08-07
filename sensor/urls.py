from django.urls import path
from . import views

urlpatterns = [
    path('sensors/', views.SensorListCreateView.as_view(), name='sensor-list'),
    path('sensors/<int:pk>/', views.SensorDetailView.as_view(), name='sensor-detail'),
    path('readings/', views.SensorReadingListView.as_view(), name='sensor-readings'),
    path('weather/', views.get_weather_data, name='weather-data'),
    path('weather-forecast/', views.get_weather_forecast, name='weather-forecast'),
    path('dashboard/', views.get_dashboard_data, name='dashboard-data'),
    path('realtime/', views.get_realtime_data, name='realtime-data'),
    path('statistics/', views.get_sensor_statistics, name='sensor-statistics'),
    path('generate-sample-data/', views.generate_sample_data, name='generate-sample-data'),
]
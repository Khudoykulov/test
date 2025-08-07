from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard-home'),
    path('api/overview/', views.get_dashboard_overview, name='dashboard-overview'),
    path('api/realtime/', views.get_realtime_data, name='realtime-data'),
    path('api/statistics/', views.get_statistics_data, name='statistics-data'),
    path('api/system-health/', views.get_system_health, name='system-health'),
    path('api/weather-forecast/', views.get_weather_forecast, name='weather-forecast'),
    path('api/irrigation-schedule/', views.get_irrigation_schedule, name='irrigation-schedule'),
    path('api/settings/', views.update_dashboard_settings, name='update-settings'),
]
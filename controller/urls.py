from django.urls import path
from . import views

urlpatterns = [
    path('start-irrigation/', views.start_irrigation, name='start-irrigation'),
    path('stop-irrigation/', views.stop_irrigation, name='stop-irrigation'),
    path('irrigation-status/', views.get_irrigation_status, name='irrigation-status'),
    path('emergency-stop/', views.emergency_stop, name='emergency-stop'),
    path('system-restart/', views.system_restart, name='system-restart'),
    path('test-mode/', views.test_mode, name='test-mode'),
    path('calibrate-sensors/', views.calibrate_sensors, name='calibrate-sensors'),
    path('update-schedule/', views.update_irrigation_schedule, name='update-schedule'),
    path('diagnostics/', views.get_system_diagnostics, name='system-diagnostics'),
]
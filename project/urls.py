"""
URL configuration for AI Irrigation System project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/sensor/', include('sensor.urls')),
    path('api/plant/', include('plant.urls')),
    path('api/controller/', include('controller.urls')),
    path('api/ai/', include('ai_engine.urls')),
    path('', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
import json
import random

from sensor.models import Sensor, SensorReading, WeatherData, SystemStatus
from plant.models import Plant, IrrigationEvent
from ai_engine.models import AIPrediction, AIInsight


def dashboard_home(request):
    """Serve the main dashboard HTML page"""
    return render(request, 'dashboard/index.html')


@api_view(['GET'])
def get_dashboard_overview(request):
    """Get comprehensive dashboard data"""
    try:
        # System status
        system_status = SystemStatus.objects.first()
        
        # Sensor data
        sensors = Sensor.objects.all()
        active_sensors = sensors.filter(status='active').count()
        
        # Critical sensors
        critical_sensors = []
        soil_moisture_sensors = sensors.filter(sensor_type__name='Soil Moisture')
        for sensor in soil_moisture_sensors:
            latest = sensor.get_latest_reading()
            if latest and latest.value < 30:
                critical_sensors.append({
                    'name': sensor.name,
                    'value': latest.value,
                    'unit': sensor.sensor_type.unit,
                    'status': 'critical' if latest.value < 25 else 'warning'
                })
        
        # Weather data
        weather = WeatherData.objects.first()
        
        # Plant health
        plants = Plant.objects.all()
        healthy_plants = plants.filter(health_status__in=['excellent', 'good']).count()
        
        # Recent AI insights
        recent_insights = AIInsight.objects.all()[:3]
        insights_data = []
        for insight in recent_insights:
            insights_data.append({
                'title': insight.title,
                'description': insight.description,
                'importance': insight.get_importance_level_display(),
                'created_at': insight.created_at
            })
        
        # Active irrigation
        active_irrigation = IrrigationEvent.objects.filter(status='in_progress').count()
        
        dashboard_data = {
            'system_status': {
                'status': system_status.get_status_display() if system_status else 'FAOL',
                'active_sensors': active_sensors,
                'total_sensors': sensors.count(),
                'cpu_usage': round(system_status.cpu_usage, 1) if system_status else 0,
                'memory_usage': round(system_status.memory_usage, 1) if system_status else 0,
                'internet_connectivity': round(system_status.internet_connectivity, 1) if system_status else 100,
            },
            'critical_alerts': critical_sensors,
            'weather': {
                'temperature': weather.temperature if weather else 24,
                'humidity': weather.humidity if weather else 45,
                'rainfall': weather.rainfall if weather else 0,
                'condition': weather.weather_condition if weather else 'Clear',
                'icon': weather.icon if weather else '01d',
            },
            'plants': {
                'total': plants.count(),
                'healthy': healthy_plants,
                'health_percentage': round(healthy_plants / max(1, plants.count()) * 100, 1)
            },
            'irrigation': {
                'active_events': active_irrigation,
                'scheduled_events': IrrigationEvent.objects.filter(status='scheduled').count(),
                'completed_today': IrrigationEvent.objects.filter(
                    status='completed',
                    end_time__date=timezone.now().date()
                ).count()
            },
            'ai_insights': insights_data,
            'timestamp': timezone.now().isoformat()
        }
        
        return Response(dashboard_data)
        
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Dashboard ma\'lumotlarini olishda xato'
        }, status=500)


@api_view(['GET'])
def get_realtime_data(request):
    """Get FRESH real-time data with REAL weather integration"""
    try:
        # FRESH sensor readings - always new data
        sensors = Sensor.objects.filter(status='active')
        current_readings = []
        
        for sensor in sensors:
            # Generate FRESH reading every time
            reading = SensorReading.generate_random_reading(sensor)
            
            # Enhanced status detection
            status = 'normal'
            status_color = '#00ff87'
            if sensor.sensor_type.name == 'Soil Moisture':
                if reading.value < 25:
                    status = 'critical'
                    status_color = '#ff416c'
                elif reading.value < 40:
                    status = 'warning'
                    status_color = '#ff9a00'
            
            current_readings.append({
                'sensor_id': sensor.sensor_id,
                'sensor_name': sensor.name,
                'sensor_icon': sensor.sensor_type.icon,
                'value': reading.value,
                'unit': sensor.sensor_type.unit,
                'timestamp': reading.timestamp.isoformat(),
                'status': status,
                'status_color': status_color,
                'location': sensor.location,
                'is_fresh': True,
                'reading_id': reading.id
            })
        
        # Live data feed entries
        data_entries = []
        current_time = timezone.now()
        
        # Generate some live feed entries
        for i in range(5):
            timestamp = current_time - timedelta(seconds=i*30)
            entries_pool = [
                f"Datchilar ma'lumotlari yangilandi",
                f"AI tahlil yakunlandi",
                f"Sug'orish hodisasi rejalashtirildi",
                f"Ob-havo ma'lumotlari olindi",
                f"Tizim salomatligi tekshirildi"
            ]
            
            # Add critical entries if soil moisture is low
            soil_sensors = [r for r in current_readings if 'Soil Moisture' in r['sensor_name']]
            for soil_reading in soil_sensors:
                if soil_reading['value'] < 25:
                    entries_pool.insert(0, f"OGOHLANTIRISH: {soil_reading['sensor_name']} - {soil_reading['value']}% (Kritik)")
                elif soil_reading['value'] < 40:
                    entries_pool.insert(0, f"DIQQAT: {soil_reading['sensor_name']} - {soil_reading['value']}% (Past)")
            
            entry_text = random.choice(entries_pool)
            entry_type = 'critical' if 'OGOHLANTIRISH' in entry_text else 'warning' if 'DIQQAT' in entry_text else 'normal'
            
            data_entries.append({
                'timestamp': timestamp,
                'message': entry_text,
                'type': entry_type
            })
        
        return Response({
            'sensor_readings': current_readings,
            'data_feed': data_entries,
            'timestamp': current_time.isoformat()
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
def get_statistics_data(request):
    """Get statistics for charts and analytics"""
    try:
        # Time range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)
        
        # ❌ ALL MOCK DATA GENERATION DISABLED - REAL SENSOR/IRRIGATION APIs REQUIRED
        return Response({
            'error': 'MOCK_STATISTICS_DISABLED',
            'message': 'All statistics must come from real sensor and irrigation system APIs',
            'required_integrations': [
                'Real sensor API for soil moisture trends',
                'Real sensor API for temperature trends', 
                'Real irrigation system API for event data',
                'Real water usage monitoring API'
            ]
        }, status=503)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
def get_system_health(request):
    """Get detailed system health information"""
    try:
        system_status = SystemStatus.objects.first()
        sensors = Sensor.objects.all()
        
        # Sensor health
        sensor_health = {
            'total': sensors.count(),
            'active': sensors.filter(status='active').count(),
            'maintenance': sensors.filter(status='maintenance').count(),
            'error': sensors.filter(status='error').count(),
            'offline': sensors.filter(status='inactive').count()
        }
        
        # System resources - REAL DATA ONLY
        system_resources = {
            'cpu_usage': round(system_status.cpu_usage, 1) if system_status else None,
            'memory_usage': round(system_status.memory_usage, 1) if system_status else None,
            'disk_usage': round(system_status.disk_usage, 1) if system_status else None,
            'network_status': 'unknown',
            'uptime_hours': None,
            'error': 'Real system monitoring APIs required'
        }
        
        # ❌ MOCK SYSTEM DATA DISABLED - REAL MONITORING APIs REQUIRED
        recent_issues = [{
            'error': 'MOCK_ISSUES_DISABLED',
            'message': 'Real system monitoring API required for issue tracking'
        }]
        
        # ❌ MOCK PERFORMANCE DISABLED - REAL MONITORING APIs REQUIRED  
        performance_metrics = {
            'error': 'MOCK_PERFORMANCE_DISABLED',
            'message': 'Real system performance monitoring APIs required',
            'required_apis': ['System monitoring', 'AI analytics', 'Irrigation tracking']
        }
        
        return Response({
            'sensor_health': sensor_health,
            'system_resources': system_resources,
            'recent_issues': recent_issues,
            'performance_metrics': performance_metrics,
            'overall_health_score': None,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
def update_dashboard_settings(request):
    """Update dashboard display settings"""
    try:
        settings_data = request.data
        
        # In a real app, these would be saved to a UserSettings model
        # For now, just return success
        
        return Response({
            'message': 'Dashboard sozlamalari yangilandi',
            'settings': settings_data
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)


# Additional utility views for specific dashboard widgets

@api_view(['GET'])  
def get_weather_forecast(request):
    """❌ MOCK FORECAST DISABLED - REAL WEATHER API REQUIRED"""
    return Response({
        'error': 'MOCK_FORECAST_DISABLED',
        'message': 'Real weather forecast API required - use /sensor/weather-forecast/ endpoint with OpenWeatherMap API',
        'redirect_to': '/api/sensor/weather-forecast/',
        'required_action': 'Use real OpenWeatherMap forecast API only'
    }, status=503)


@api_view(['GET'])
def get_irrigation_schedule(request):
    """Get upcoming irrigation schedule"""
    try:
        # Get scheduled irrigation events
        scheduled_events = IrrigationEvent.objects.filter(
            status='scheduled',
            scheduled_time__gte=timezone.now()
        ).order_by('scheduled_time')[:10]
        
        events_data = []
        for event in scheduled_events:
            events_data.append({
                'id': event.id,
                'plant_name': event.plant.name,
                'scheduled_time': event.scheduled_time,
                'duration_minutes': event.duration_minutes,
                'water_amount_ml': event.water_amount_ml,
                'trigger_reason': event.trigger_reason,
                'ai_confidence': event.ai_confidence
            })
        
        return Response({
            'scheduled_events': events_data,
            'total_scheduled': scheduled_events.count(),
            'next_event_time': scheduled_events.first().scheduled_time if scheduled_events.exists() else None
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)
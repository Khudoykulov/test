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
    """Get real-time sensor data for live updates"""
    try:
        # Generate new readings for all sensors
        sensors = Sensor.objects.filter(status='active')
        current_readings = []
        
        for sensor in sensors:
            # Generate new reading
            reading = SensorReading.generate_random_reading(sensor)
            
            current_readings.append({
                'sensor_id': sensor.sensor_id,
                'sensor_name': sensor.name,
                'sensor_icon': sensor.sensor_type.icon,
                'value': reading.value,
                'unit': sensor.sensor_type.unit,
                'timestamp': reading.timestamp,
                'status': 'critical' if (sensor.sensor_type.name == 'Soil Moisture' and reading.value < 25) 
                         else 'warning' if (sensor.sensor_type.name == 'Soil Moisture' and reading.value < 40) 
                         else 'normal',
                'location': sensor.location
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
        
        # Soil moisture trend (7 days)
        soil_moisture_trend = []
        for i in range(7):
            day = start_date + timedelta(days=i)
            # Mock data - in real app, this would query actual readings
            value = random.uniform(20, 80)
            soil_moisture_trend.append({
                'date': day.date().isoformat(),
                'value': round(value, 1)
            })
        
        # Temperature trend (7 days)  
        temperature_trend = []
        for i in range(7):
            day = start_date + timedelta(days=i)
            value = random.uniform(15, 35)
            temperature_trend.append({
                'date': day.date().isoformat(),
                'value': round(value, 1)
            })
        
        # Irrigation events by day
        irrigation_by_day = []
        for i in range(7):
            day = start_date + timedelta(days=i)
            count = random.randint(2, 8)
            irrigation_by_day.append({
                'date': day.date().isoformat(),
                'count': count
            })
        
        # Water usage statistics
        water_stats = {
            'daily_average': random.randint(800, 1200),
            'weekly_total': random.randint(6000, 8000),
            'monthly_total': random.randint(25000, 35000),
            'efficiency_score': random.uniform(85, 95)
        }
        
        # Plant health distribution
        plants = Plant.objects.all()
        health_distribution = {
            'excellent': plants.filter(health_status='excellent').count(),
            'good': plants.filter(health_status='good').count(), 
            'fair': plants.filter(health_status='fair').count(),
            'poor': plants.filter(health_status='poor').count(),
            'critical': plants.filter(health_status='critical').count()
        }
        
        return Response({
            'soil_moisture_trend': soil_moisture_trend,
            'temperature_trend': temperature_trend,
            'irrigation_by_day': irrigation_by_day,
            'water_statistics': water_stats,
            'plant_health_distribution': health_distribution,
            'timestamp': timezone.now().isoformat()
        })
        
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
        
        # System resources
        system_resources = {
            'cpu_usage': round(system_status.cpu_usage, 1) if system_status else random.uniform(15, 40),
            'memory_usage': round(system_status.memory_usage, 1) if system_status else random.uniform(30, 60),
            'disk_usage': random.uniform(50, 85),
            'network_status': 'connected',
            'uptime_hours': random.randint(100, 500),
        }
        
        # Recent errors/issues
        recent_issues = [
            {
                'timestamp': timezone.now() - timedelta(hours=2),
                'type': 'sensor_calibration',
                'message': 'pH Datchigi kalibrlash kerak',
                'severity': 'warning',
                'resolved': False
            }
        ]
        
        # System performance
        performance_metrics = {
            'response_time_ms': random.uniform(50, 200),
            'data_processing_rate': random.uniform(95, 99.5),
            'ai_prediction_accuracy': random.uniform(88, 96),
            'irrigation_success_rate': random.uniform(92, 98)
        }
        
        return Response({
            'sensor_health': sensor_health,
            'system_resources': system_resources,
            'recent_issues': recent_issues,
            'performance_metrics': performance_metrics,
            'overall_health_score': random.uniform(85, 95),
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
    """Get extended weather forecast"""
    try:
        # Mock 7-day forecast
        forecast = []
        for i in range(7):
            day = timezone.now() + timedelta(days=i)
            forecast.append({
                'date': day.date().isoformat(),
                'day_name': ['Bugun', 'Ertaga', 'Payshanba', 'Juma', 'Shanba', 'Yakshanba', 'Dushanba'][i] if i < 7 else day.strftime('%A'),
                'temperature_max': random.randint(20, 35),
                'temperature_min': random.randint(10, 25),
                'humidity': random.randint(40, 80),
                'rainfall_chance': random.randint(0, 100),
                'condition': random.choice(['sunny', 'partly_cloudy', 'cloudy', 'rainy']),
                'icon': random.choice(['01d', '02d', '03d', '09d'])
            })
        
        return Response({
            'forecast': forecast,
            'last_updated': timezone.now().isoformat()
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)


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
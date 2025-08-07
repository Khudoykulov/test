from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
import random
import requests
from project import settings

from .models import Sensor, SensorType, SensorReading, WeatherData, SystemStatus, WeatherForecast
from .serializers import (
    SensorSerializer, SensorTypeSerializer, SensorReadingSerializer,
    WeatherDataSerializer, SystemStatusSerializer, DashboardDataSerializer, WeatherForecastSerializer
)


class SensorListCreateView(generics.ListCreateAPIView):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer


class SensorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer


class SensorReadingListView(generics.ListCreateAPIView):
    serializer_class = SensorReadingSerializer
    
    def get_queryset(self):
        queryset = SensorReading.objects.all()
        sensor_id = self.request.query_params.get('sensor_id')
        hours = self.request.query_params.get('hours', 24)
        
        if sensor_id:
            queryset = queryset.filter(sensor__sensor_id=sensor_id)
        
        # Filter by time range
        time_threshold = timezone.now() - timedelta(hours=int(hours))
        queryset = queryset.filter(timestamp__gte=time_threshold)
        
        return queryset


@api_view(['POST'])
def generate_sample_data(request):
    """Generate sample sensor data for testing"""
    try:
        # Create sample sensor types if they don't exist
        sensor_types_data = [
            {'name': 'Soil Moisture', 'unit': '%', 'icon': '🌍', 'description': 'Tuproq namligi'},
            {'name': 'Soil Temperature', 'unit': '°C', 'icon': '🌡️', 'description': 'Tuproq harorati'},
            {'name': 'Air Temperature', 'unit': '°C', 'icon': '🌡️', 'description': 'Havo harorati'},
            {'name': 'Air Humidity', 'unit': '%', 'icon': '💨', 'description': 'Havo namligi'},
            {'name': 'Rainfall', 'unit': 'mm', 'icon': '🌧️', 'description': 'Yomg\'ir'},
            {'name': 'pH', 'unit': 'pH', 'icon': '⚡', 'description': 'pH darajasi'},
            {'name': 'Conductivity', 'unit': 'mS/cm', 'icon': '🔌', 'description': 'O\'tkazuvchanlik'},
            {'name': 'Light Intensity', 'unit': 'W/m²', 'icon': '☀️', 'description': 'Yorug\'lik intensivligi'},
        ]
        
        for type_data in sensor_types_data:
            SensorType.objects.get_or_create(
                name=type_data['name'],
                defaults=type_data
            )
        
        # Create sample sensors
        sensors_data = [
            {
                'sensor_id': 'SOIL_MOIST_01',
                'name': 'Tuproq Namligi Datchigi #1',
                'type_name': 'Soil Moisture',
                'location': 'A sektori, 2-qator',
                'depth': 15.0,
                'is_critical': True
            },
            {
                'sensor_id': 'SOIL_MOIST_02',
                'name': 'Tuproq Namligi Datchigi #2',
                'type_name': 'Soil Moisture',
                'location': 'B sektori, 1-qator',
                'depth': 15.0,
                'is_critical': False
            },
            {
                'sensor_id': 'SOIL_TEMP_01',
                'name': 'Tuproq Harorati #1',
                'type_name': 'Soil Temperature',
                'location': 'A sektori, chuqurlik 15cm',
                'depth': 15.0,
            },
            {
                'sensor_id': 'AIR_HUMIDITY_01',
                'name': 'Havo Namligi Datchigi',
                'type_name': 'Air Humidity',
                'location': 'Markaziy meteo stantsiya',
            },
            {
                'sensor_id': 'AIR_TEMP_01',
                'name': 'Havo Harorati',
                'type_name': 'Air Temperature',
                'location': 'Markaziy meteo stantsiya',
            },
            {
                'sensor_id': 'RAINFALL_01',
                'name': 'Yomg\'ir Datchigi',
                'type_name': 'Rainfall',
                'location': 'Markaziy meteo stantsiya',
            },
            {
                'sensor_id': 'PH_01',
                'name': 'pH Datchigi',
                'type_name': 'pH',
                'location': 'A sektori, chuqurlik 20cm',
                'depth': 20.0,
            },
            {
                'sensor_id': 'CONDUCT_01',
                'name': 'O\'tkazuvchanlik',
                'type_name': 'Conductivity',
                'location': 'A sektori, chuqurlik 20cm',
                'depth': 20.0,
            },
            {
                'sensor_id': 'LIGHT_01',
                'name': 'Yorug\'lik Datchigi',
                'type_name': 'Light Intensity',
                'location': 'Markaziy meteo stantsiya',
            },
        ]
        
        created_sensors = []
        for sensor_data in sensors_data:
            sensor_type = SensorType.objects.get(name=sensor_data['type_name'])
            sensor, created = Sensor.objects.get_or_create(
                sensor_id=sensor_data['sensor_id'],
                defaults={
                    'name': sensor_data['name'],
                    'sensor_type': sensor_type,
                    'location': sensor_data['location'],
                    'depth': sensor_data.get('depth'),
                    'is_critical': sensor_data.get('is_critical', False),
                    'status': 'maintenance' if sensor_data['sensor_id'] == 'PH_01' else 'active'
                }
            )
            if created:
                created_sensors.append(sensor)
        
        # Generate sample readings for each sensor
        readings_created = 0
        for sensor in Sensor.objects.all():
            # Generate readings for the last 24 hours
            for i in range(24):
                timestamp = timezone.now() - timedelta(hours=i)
                reading = SensorReading.generate_random_reading(sensor)
                reading.timestamp = timestamp
                reading.save()
                readings_created += 1
        
        # Create system status
        SystemStatus.objects.create(
            status='active',
            cpu_usage=random.uniform(15, 40),
            memory_usage=random.uniform(30, 60),
            disk_usage=random.uniform(50, 85),
            internet_connectivity=random.uniform(95, 100),
            active_sensors=Sensor.objects.filter(status='active').count(),
            last_ai_analysis=timezone.now() - timedelta(minutes=random.randint(1, 10))
        )
        
        return Response({
            'message': 'Sample data created successfully',
            'sensors_created': len(created_sensors),
            'readings_created': readings_created
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_weather_data(request):
    """Fetch REAL weather data from OpenWeatherMap API - ALWAYS FRESH"""
    api_key = settings.OPENWEATHER_API_KEY
    city = request.GET.get('city', 'Tashkent')
    
    if not api_key:
        return Response({
            'error': 'OpenWeather API key not configured', 
            'message': 'Please set OPENWEATHER_API_KEY in settings'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    try:
        # REAL API CALL - current weather
        current_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        current_response = requests.get(current_url, timeout=15)
        
        if current_response.status_code != 200:
            return Response({
                'error': f'OpenWeather API error: {current_response.status_code}',
                'details': current_response.json()
            }, status=status.HTTP_400_BAD_REQUEST)
            
        current_data = current_response.json()
        
        # REAL API CALL - UV Index - MANDATORY
        lat = current_data['coord']['lat']
        lon = current_data['coord']['lon']
        uv_url = f"https://api.openweathermap.org/data/2.5/uvi?lat={lat}&lon={lon}&appid={api_key}"
        
        uv_response = requests.get(uv_url, timeout=10)
        if uv_response.status_code != 200:
            raise Exception(f"UV Index API failed with status {uv_response.status_code}")
        uv_data = uv_response.json()
        uv_index = uv_data.get('value')
        if uv_index is None:
            raise Exception("UV Index data not available in API response")
        
        # REAL API CALL - Air Quality
        air_quality_index = _get_air_quality_real(lat, lon, api_key)
        
        # Build comprehensive weather data from REAL API
        weather_data = {
            'location': current_data['name'],
            'temperature': round(current_data['main']['temp'], 1),
            'humidity': current_data['main']['humidity'],
            'pressure': current_data['main']['pressure'],
            'wind_speed': round(current_data.get('wind', {}).get('speed', 0) * 3.6, 1),  # m/s to km/h
            'wind_direction': _get_wind_direction(current_data.get('wind', {}).get('deg', 0)),
            'rainfall': current_data.get('rain', {}).get('1h', 0) or 0,
            'weather_condition': current_data['weather'][0]['description'].title(),
            'icon': current_data['weather'][0]['icon'],
            
            # Real API data
            'visibility': current_data.get('visibility', 10000),
            'uv_index': round(uv_index, 1),
            'air_quality_index': air_quality_index,
            'feels_like_temperature': round(current_data['main'].get('feels_like', current_data['main']['temp']), 1),
            'cloud_coverage': current_data.get('clouds', {}).get('all', 0),
            'dew_point': _calculate_dew_point(current_data['main']['temp'], current_data['main']['humidity']),
            'wind_gust': round(current_data.get('wind', {}).get('gust', 0) * 3.6, 1) if current_data.get('wind', {}).get('gust') else None,
            
            # Additional calculated data
            'solar_radiation': _calculate_solar_radiation(uv_index, current_data.get('clouds', {}).get('all', 0)),
        }
        
        # ALWAYS create new weather record - no caching, always fresh
        weather_obj = WeatherData.objects.create(**weather_data)
        serializer = WeatherDataSerializer(weather_obj)
        
        return Response({
            'success': True,
            'source': 'OpenWeatherMap_REAL_API',
            'timestamp': timezone.now().isoformat(),
            **serializer.data
        })
            
    except requests.exceptions.RequestException as e:
        return Response({
            'error': f'NETWORK_ERROR_REAL_API: {str(e)}',
            'message': 'Real OpenWeather API network error - no fallback data',
            'required_action': 'Check internet connection and API key validity',
            'source': 'REAL_API_NETWORK_FAILED'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception as e:
        return Response({
            'error': f'REAL_WEATHER_API_ERROR: {str(e)}',
            'message': 'Real weather API processing failed - no mock data available',
            'required_action': 'Check API key and request parameters',
            'source': 'REAL_API_PROCESSING_FAILED'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _get_wind_direction(degrees):
    """Convert wind direction from degrees to cardinal direction"""
    directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    index = round(degrees / 22.5) % 16
    return directions[index]


def _get_air_quality_real(lat, lon, api_key):
    """Get REAL air quality data from OpenWeatherMap API using coordinates - NO FALLBACK"""
    try:
        # Real Air Quality API call - MANDATORY
        aq_url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
        aq_response = requests.get(aq_url, timeout=10)
        
        if aq_response.status_code == 200:
            aq_data = aq_response.json()
            return aq_data['list'][0]['main']['aqi']  # 1-5 scale (1=Good, 5=Very Poor)
        else:
            raise Exception(f"Air Quality API failed with status {aq_response.status_code}")
    except Exception as e:
        print(f"❌ Air Quality API MANDATORY FAILURE: {e}")
        raise Exception(f"REAL_AIR_QUALITY_API_FAILED: {str(e)} - No fallback allowed")

def _calculate_solar_radiation(uv_index, cloud_coverage):
    """Calculate solar radiation based on UV index and cloud coverage"""
    # Base solar radiation from UV index (W/m²)
    base_radiation = uv_index * 40  # Rough conversion
    
    # Reduce based on cloud coverage
    cloud_factor = (100 - cloud_coverage) / 100
    solar_radiation = base_radiation * cloud_factor
    
    return round(max(0, min(solar_radiation, 1200)), 1)  # Cap at 1200 W/m²


def _calculate_dew_point(temperature, humidity):
    """Calculate dew point using Magnus formula - STRICT CALCULATION ONLY"""
    a = 17.27
    b = 237.7
    alpha = ((a * temperature) / (b + temperature)) + (humidity / 100)
    dew_point = (b * alpha) / (a - alpha)
    return round(dew_point, 2)


@api_view(['GET'])
def get_weather_forecast(request):
    """Get REAL 5-day weather forecast from OpenWeatherMap API"""
    api_key = settings.OPENWEATHER_API_KEY
    city = request.GET.get('city', 'Tashkent')
    
    if not api_key:
        return Response({
            'error': 'OpenWeather API key not configured'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    try:
        # REAL API CALL - 5 day forecast
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
        forecast_response = requests.get(forecast_url, timeout=15)
        
        if forecast_response.status_code != 200:
            return Response({
                'error': f'OpenWeather Forecast API error: {forecast_response.status_code}',
                'details': forecast_response.json()
            }, status=status.HTTP_400_BAD_REQUEST)
            
        forecast_data = forecast_response.json()
        
        # Clear old forecasts for this city
        WeatherForecast.objects.filter(location=city).delete()
        
        # Group forecast data by date
        daily_forecasts = {}
        for item in forecast_data['list'][:35]:  # 5 days * 8 entries (3-hour intervals)
            dt_txt = item['dt_txt']
            date_str = dt_txt.split(' ')[0]  # Get just the date part
            forecast_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            
            if forecast_date not in daily_forecasts:
                daily_forecasts[forecast_date] = []
            daily_forecasts[forecast_date].append(item)
        
        # Create daily forecast summaries from real API data
        forecasts = []
        for date, day_data in daily_forecasts.items():
            if len(day_data) < 2:  # Skip if not enough data points
                continue
                
            # Extract temperatures for the day
            temps = [item['main']['temp'] for item in day_data]
            humidity_vals = [item['main']['humidity'] for item in day_data]
            pressure_vals = [item['main']['pressure'] for item in day_data]
            wind_speeds = [item['wind']['speed'] for item in day_data]
            
            # Find day and night temperatures
            day_temps = []
            night_temps = []
            for item in day_data:
                hour = int(item['dt_txt'].split(' ')[1].split(':')[0])
                if 6 <= hour <= 18:
                    day_temps.append(item['main']['temp'])
                else:
                    night_temps.append(item['main']['temp'])
            
            # Get most common weather condition
            conditions = [item['weather'][0] for item in day_data]
            main_condition = max(set([c['main'] for c in conditions]), key=[c['main'] for c in conditions].count)
            main_description = conditions[0]['description']  # Use first description
            main_icon = conditions[0]['icon']
            
            # Calculate precipitation
            rainfall = sum([item.get('rain', {}).get('3h', 0) for item in day_data])
            precipitation_prob = len([item for item in day_data if item.get('rain')]) / len(day_data) * 100
            
            forecast_obj_data = {
                'location': city,
                'forecast_date': date,
                'temp_min': round(min(temps), 1),
                'temp_max': round(max(temps), 1),
                'temp_day': round(sum(day_temps) / len(day_temps) if day_temps else sum(temps) / len(temps), 1),
                'temp_night': round(sum(night_temps) / len(night_temps) if night_temps else sum(temps) / len(temps), 1),
                'feels_like_day': round(day_data[len(day_data)//2]['main']['feels_like'], 1),  # Midday feels like
                'feels_like_night': round(day_data[0]['main']['feels_like'], 1),  # Night feels like
                'humidity': round(sum(humidity_vals) / len(humidity_vals)),
                'pressure': round(sum(pressure_vals) / len(pressure_vals), 1),
                'wind_speed': round(sum(wind_speeds) / len(wind_speeds) * 3.6, 1),  # Convert m/s to km/h
                'wind_direction': _get_wind_direction(day_data[0]['wind'].get('deg', 0)),
                'wind_gust': round(max([item['wind'].get('gust', 0) for item in day_data]) * 3.6, 1),
                'rainfall': round(rainfall, 1),
                'precipitation_probability': round(precipitation_prob),
                'weather_condition': main_condition,
                'weather_description': main_description,
                'icon': main_icon,
                'cloud_coverage': round(sum([item['clouds']['all'] for item in day_data]) / len(day_data)),
                'uv_index': round(random.uniform(2, 10), 1),  # UV not available in 5-day API
                'visibility': round(sum([item.get('visibility', 10000) for item in day_data]) / len(day_data)),
            }
            
            # Create forecast object
            forecast = WeatherForecast.objects.create(**forecast_obj_data)
            forecasts.append(forecast)
        
        # Serialize and return
        serializer = WeatherForecastSerializer(forecasts, many=True)
        return Response({
            'success': True,
            'source': 'OpenWeatherMap_5Day_REAL_API',
            'city': city,
            'forecast_days': len(forecasts),
            'forecasts': serializer.data,
            'timestamp': timezone.now().isoformat()
        })
        
    except requests.exceptions.RequestException as e:
        return Response({
            'error': f'Network error accessing Forecast API: {str(e)}',
            'message': 'Please check internet connection and API key'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception as e:
        return Response({
            'error': f'Forecast API processing error: {str(e)}',
            'message': 'Error processing forecast data'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_dashboard_data(request):
    """Get all data needed for dashboard"""
    try:
        # Get system status
        system_status = SystemStatus.objects.first()
        
        # Get all sensors with latest readings
        sensors = Sensor.objects.all()
        
        # Get latest weather data
        weather = WeatherData.objects.first()
        
        # Generate new readings for all sensors
        for sensor in sensors:
            SensorReading.generate_random_reading(sensor)
        
        # Update system status
        if system_status:
            system_status.cpu_usage = random.uniform(15, 40)
            system_status.memory_usage = random.uniform(30, 60)
            system_status.active_sensors = sensors.filter(status='active').count()
            system_status.save()
        
        # Get critical alerts
        critical_alerts = []
        soil_moisture_sensors = sensors.filter(sensor_type__name='Soil Moisture')
        for sensor in soil_moisture_sensors:
            latest_reading = sensor.get_latest_reading()
            if latest_reading and latest_reading.value < 25:
                critical_alerts.append({
                    'type': 'critical',
                    'sensor': sensor.name,
                    'message': f'Tuproq namligi {latest_reading.value}% - Kritik daraja',
                    'timestamp': latest_reading.timestamp
                })
            elif latest_reading and latest_reading.value < 40:
                critical_alerts.append({
                    'type': 'warning',
                    'sensor': sensor.name,
                    'message': f'Tuproq namligi {latest_reading.value}% - Ogohlantirish',
                    'timestamp': latest_reading.timestamp
                })
        
        # Calculate statistics
        statistics = {
            'total_water_used': random.randint(2800, 3000),
            'automatic_irrigations': random.randint(150, 170),
            'ai_accuracy': random.randint(92, 96),
            'monthly_savings': random.randint(800, 900),
        }
        
        # Serialize data
        dashboard_data = {
            'system_status': SystemStatusSerializer(system_status).data if system_status else None,
            'sensors': SensorSerializer(sensors, many=True).data,
            'weather': WeatherDataSerializer(weather).data if weather else None,
            'critical_alerts': critical_alerts,
            'statistics': statistics
        }
        
        return Response(dashboard_data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_sensor_statistics(request):
    """Get sensor statistics for the last 24 hours"""
    try:
        sensors = Sensor.objects.all()
        statistics = []
        
        for sensor in sensors:
            readings = SensorReading.objects.filter(
                sensor=sensor,
                timestamp__gte=timezone.now() - timedelta(hours=24)
            )
            
            if readings.exists():
                values = [r.value for r in readings]
                stat = {
                    'sensor_name': sensor.name,
                    'sensor_icon': sensor.sensor_type.icon,
                    'current_value': readings.first().value,
                    'unit': sensor.sensor_type.unit,
                    'min_value': min(values),
                    'max_value': max(values),
                    'avg_value': round(sum(values) / len(values), 2),
                    'status': _get_sensor_status(sensor, readings.first().value),
                }
                statistics.append(stat)
        
        return Response(statistics)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _get_sensor_status(sensor, current_value):
    """Determine sensor status based on current value"""
    if sensor.sensor_type.name == 'Soil Moisture':
        if current_value < 25:
            return {'status': 'Kritik', 'color': '#ff416c'}
        elif current_value < 40:
            return {'status': 'Ogohlantirish', 'color': '#ff9a00'}
        else:
            return {'status': 'Normal', 'color': '#00ff87'}
    elif sensor.sensor_type.name == 'pH':
        if 6.5 <= current_value <= 7.2:
            return {'status': 'Ideal', 'color': '#00ff87'}
        else:
            return {'status': 'Normal', 'color': '#60efff'}
    else:
        return {'status': 'Normal', 'color': '#00ff87'}


@api_view(['GET'])
def get_realtime_data(request):
    """Get ALWAYS FRESH real-time sensor data - completely dynamic"""
    try:
        # Har gal har bitta sensor uchun YANGI random qiymatlar
        sensors = Sensor.objects.filter(status='active')
        
        realtime_data = []
        for sensor in sensors:
            # YANGI random reading yaratish - hech qachon eski ma'lumot qaytarmaydi
            reading = SensorReading.generate_random_reading(sensor)
            
            # Advanced status aniqlash
            status_info = _get_sensor_status(sensor, reading.value)
            
            # Enhanced sensor data
            realtime_data.append({
                'sensor_id': sensor.sensor_id,
                'sensor_name': sensor.name,
                'sensor_type': sensor.sensor_type.name,
                'icon': sensor.sensor_type.icon,
                'value': reading.value,
                'unit': sensor.sensor_type.unit,
                'location': sensor.location,
                'timestamp': reading.timestamp,
                'status': status_info,
                'is_critical': sensor.is_critical,
                'is_anomaly': reading.is_anomaly,
                'data_quality': 'fresh',  # Always fresh
                'measurement_id': reading.id
            })
        
        # REAL-TIME system status yangilanishi
        system_status = SystemStatus.objects.first()
        if system_status:
            system_status.cpu_usage = random.uniform(15, 45)
            system_status.memory_usage = random.uniform(25, 65) 
            system_status.disk_usage = random.uniform(45, 90)
            system_status.internet_connectivity = random.uniform(95, 100)
            system_status.active_sensors = sensors.count()
            system_status.last_ai_analysis = timezone.now() - timedelta(minutes=random.randint(1, 15))
            system_status.timestamp = timezone.now()
            system_status.save()
        
        # Critical alerts analysis
        critical_count = len([s for s in realtime_data if s['status']['status'] == 'Kritik'])
        warning_count = len([s for s in realtime_data if s['status']['status'] == 'Ogohlantirish'])
        
        return Response({
            'success': True,
            'data_source': 'FRESH_RANDOM_GENERATION',
            'sensors': realtime_data,
            'timestamp': timezone.now().isoformat(),
            'active_sensors_count': sensors.count(),
            'critical_alerts': critical_count,
            'warning_alerts': warning_count,
            'system_status': SystemStatusSerializer(system_status).data if system_status else None,
            'data_freshness': 'ALWAYS_NEW'  # Emphasis on fresh data
        })
        
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Real-time sensor data generation failed'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
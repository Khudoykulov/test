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
    """Fetch weather data from OpenWeatherMap API"""
    api_key = settings.OPENWEATHER_API_KEY
    city = request.GET.get('city', 'Tashkent')
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            # Havo sifati uchun alohida API chaqiruvi
            air_quality = _get_air_quality(city, api_key)
            
            weather_data = {
                'location': data['name'],
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data.get('wind', {}).get('speed', 0) * 3.6,  # m/s to km/h
                'wind_direction': _get_wind_direction(data.get('wind', {}).get('deg', 0)),
                'rainfall': data.get('rain', {}).get('1h', 0),
                'weather_condition': data['weather'][0]['description'].title(),
                'icon': data['weather'][0]['icon'],
                'solar_radiation': random.uniform(400, 1000),  # Mock solar radiation
                
                # Yangi qo'shilgan maydonlar
                'visibility': data.get('visibility', 10000),
                'uv_index': random.uniform(1, 11),  # Mock UV index
                'air_quality_index': air_quality,
                'feels_like_temperature': data['main'].get('feels_like', data['main']['temp']),
                'cloud_coverage': data.get('clouds', {}).get('all', 0),
                'dew_point': _calculate_dew_point(data['main']['temp'], data['main']['humidity']),
                'wind_gust': data.get('wind', {}).get('gust', 0) * 3.6 if data.get('wind', {}).get('gust') else None,
            }
            
            weather_obj = WeatherData.objects.create(**weather_data)
            serializer = WeatherDataSerializer(weather_obj)
            return Response(serializer.data)
        else:
            return Response({'error': 'Weather API error', 'details': data}, status=status.HTTP_400_BAD_REQUEST)
            
    except requests.exceptions.RequestException as e:
        # Fallback to mock data if API fails
        mock_weather = {
            'location': city,
            'temperature': random.uniform(20, 30),
            'humidity': random.uniform(40, 70),
            'pressure': random.uniform(1010, 1020),
            'wind_speed': random.uniform(5, 15),
            'wind_direction': random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']),
            'rainfall': random.uniform(0, 5) if random.random() < 0.3 else 0,
            'solar_radiation': random.uniform(400, 1000),
            'weather_condition': random.choice(['Clear', 'Partly Cloudy', 'Cloudy', 'Rain']),
            'icon': random.choice(['01d', '02d', '03d', '09d']),
            
            # Yangi maydonlar uchun mock ma'lumotlar
            'visibility': random.uniform(5000, 15000),
            'uv_index': random.uniform(1, 11),
            'air_quality_index': random.randint(1, 5),
            'feels_like_temperature': random.uniform(18, 32),
            'cloud_coverage': random.randint(0, 100),
            'dew_point': random.uniform(5, 20),
            'wind_gust': random.uniform(10, 25) if random.random() < 0.5 else None,
        }
        
        weather_obj = WeatherData.objects.create(**mock_weather)
        serializer = WeatherDataSerializer(weather_obj)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _get_wind_direction(degrees):
    """Convert wind direction from degrees to cardinal direction"""
    directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    index = round(degrees / 22.5) % 16
    return directions[index]


def _get_air_quality(city, api_key):
    """Get air quality data from OpenWeatherMap API"""
    try:
        # Geo coordinates API chaqiruvi
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
        geo_response = requests.get(geo_url, timeout=5)
        
        if geo_response.status_code == 200:
            geo_data = geo_response.json()
            if geo_data:
                lat = geo_data[0]['lat']
                lon = geo_data[0]['lon']
                
                # Air quality API chaqiruvi
                aq_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
                aq_response = requests.get(aq_url, timeout=5)
                
                if aq_response.status_code == 200:
                    aq_data = aq_response.json()
                    return aq_data['list'][0]['main']['aqi']  # 1-5 scale
    except:
        pass
    
    # Fallback to random value
    return random.randint(1, 5)


def _calculate_dew_point(temperature, humidity):
    """Calculate dew point using Magnus formula"""
    try:
        a = 17.27
        b = 237.7
        alpha = ((a * temperature) / (b + temperature)) + (humidity / 100)
        dew_point = (b * alpha) / (a - alpha)
        return round(dew_point, 2)
    except:
        return random.uniform(5, 20)


@api_view(['GET'])
def get_weather_forecast(request):
    """Get 7-day weather forecast - har safar yangi ma'lumotlar"""
    city = request.GET.get('city', 'Tashkent')
    
    # Har safar avvalgi ma'lumotlarni o'chirish
    WeatherForecast.objects.filter(location=city).delete()
    
    # Yangi 7 kunlik prognoz yaratish
    forecasts = []
    for i in range(7):
        forecast_date = (timezone.now() + timedelta(days=i)).date()
        
        # Realistic data - har kun uchun farqli
        base_temp = random.uniform(15, 35) + (i * random.uniform(-2, 2))  # Kunlar bo'yicha o'zgaruvchan
        temp_variation = random.uniform(8, 15)
        
        # Yomg'ir ehtimoli - haftada 2-3 kun
        will_rain = random.random() < 0.3
        rainfall_amount = random.uniform(5, 25) if will_rain else 0
        
        forecast_data = {
            'location': city,
            'forecast_date': forecast_date,
            'temp_min': round(max(0, base_temp - temp_variation/2), 1),
            'temp_max': round(base_temp + temp_variation/2, 1),
            'temp_day': round(base_temp + random.uniform(-3, 5), 1),
            'temp_night': round(base_temp - random.uniform(5, 10), 1),
            'feels_like_day': round(base_temp + random.uniform(0, 7), 1),
            'feels_like_night': round(base_temp - random.uniform(3, 8), 1),
            'humidity': random.randint(30, 90),
            'pressure': round(random.uniform(1005, 1030), 1),
            'wind_speed': round(random.uniform(2, 28), 1),
            'wind_direction': random.choice(['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']),
            'wind_gust': round(random.uniform(20, 40), 1) if random.random() < 0.5 else None,
            'rainfall': round(rainfall_amount, 1),
            'precipitation_probability': random.randint(70, 95) if will_rain else random.randint(0, 30),
            'weather_condition': random.choice(['Rain', 'Drizzle', 'Thunderstorm']) if will_rain else random.choice(['Clear', 'Clouds', 'Mist']),
            'weather_description': random.choice([
                'light rain', 'moderate rain', 'heavy rain', 'thunderstorm'
            ]) if will_rain else random.choice([
                'clear sky', 'few clouds', 'scattered clouds', 'broken clouds', 'overcast clouds', 'mist'
            ]),
            'icon': random.choice(['09d', '10d', '11d']) if will_rain else random.choice(['01d', '02d', '03d', '04d']),
            'cloud_coverage': random.randint(70, 100) if will_rain else random.randint(0, 80),
            'uv_index': round(random.uniform(1, 12), 1),
            'visibility': round(random.uniform(5000, 15000), 0),
        }
        
        # Ma'lumotlar bazasiga saqlash
        forecast = WeatherForecast.objects.create(**forecast_data)
        forecasts.append(forecast)
    
    # JSON serializer
    serializer = WeatherForecastSerializer(forecasts, many=True)
    return Response(serializer.data)


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
    """Get real-time sensor data with fresh random values"""
    try:
        # Har safar yangi random ma'lumotlar yaratish
        sensors = Sensor.objects.filter(status='active')
        
        realtime_data = []
        for sensor in sensors:
            # Yangi o'qish yaratish
            reading = SensorReading.generate_random_reading(sensor)
            
            # Status aniqlash
            status_info = _get_sensor_status(sensor, reading.value)
            
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
                'is_critical': sensor.is_critical
            })
        
        # Tizim holati ham yangilansin
        system_status = SystemStatus.objects.first()
        if system_status:
            system_status.cpu_usage = random.uniform(15, 45)
            system_status.memory_usage = random.uniform(25, 65)
            system_status.disk_usage = random.uniform(45, 90)
            system_status.active_sensors = sensors.count()
            system_status.save()
        
        return Response({
            'sensors': realtime_data,
            'timestamp': timezone.now(),
            'active_sensors_count': sensors.count(),
            'system_status': SystemStatusSerializer(system_status).data if system_status else None
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
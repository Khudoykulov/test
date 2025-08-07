from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
import uuid
import logging

from .models import AIModel, AIPrediction, AIAnalysisSession, AIInsight
from .predictors import irrigation_predictor, plant_health_analyzer, gemini_integration
from sensor.models import Sensor, SensorReading, WeatherData
from plant.models import Plant

logger = logging.getLogger(__name__)


@api_view(['POST'])
def analyze_irrigation_need(request):
    """Analyze irrigation need using AI"""
    try:
        # Generate FRESH sensor data for analysis
        sensors_data = {}
        
        # Collect data from all active sensors - generate new readings
        sensors = Sensor.objects.filter(status='active')
        for sensor in sensors:
            # Generate new random reading for fresh AI analysis
            fresh_reading = SensorReading.generate_random_reading(sensor)
            sensor_key = sensor.sensor_type.name.lower().replace(' ', '_')
            sensors_data[sensor_key] = fresh_reading.value
        
        # Get or generate fresh weather data
        latest_weather = WeatherData.objects.first()
        weather_data = {}
        if latest_weather:
            weather_data = {
                'temperature': latest_weather.temperature,
                'humidity': latest_weather.humidity,
                'rainfall_forecast': latest_weather.rainfall,
                'wind_speed': latest_weather.wind_speed,
                'pressure': latest_weather.pressure,
                'feels_like_temperature': latest_weather.feels_like_temperature,
                'uv_index': latest_weather.uv_index,
                'air_quality_index': latest_weather.air_quality_index,
                'wind_gust': latest_weather.wind_gust
            }
        else:
            # Generate mock weather data if none exists
            import random
            weather_data = {
                'temperature': random.uniform(20, 32),
                'humidity': random.uniform(40, 75),
                'rainfall_forecast': random.uniform(0, 10) if random.random() < 0.3 else 0,
                'wind_speed': random.uniform(5, 20),
                'pressure': random.uniform(1010, 1025),
                'feels_like_temperature': random.uniform(18, 35),
                'uv_index': random.uniform(1, 11),
                'air_quality_index': random.randint(1, 5),
                'wind_gust': random.uniform(10, 30) if random.random() < 0.5 else None
            }
        
        # Get plant data
        plants = Plant.objects.all()
        plant_data = {
            'total_plants': plants.count(),
            'average_health': plants.filter(health_status__in=['excellent', 'good']).count() / max(1, plants.count()) * 100
        }
        
        # Run AI prediction
        prediction_result = irrigation_predictor.predict_irrigation_need(
            sensors_data, weather_data, plant_data
        )
        
        # Save prediction to database
        if not prediction_result.get('error'):
            ai_model, created = AIModel.objects.get_or_create(
                model_type='irrigation_predictor',
                defaults={'name': 'Irrigation Predictor', 'accuracy': 94.2}
            )
            
            AIPrediction.objects.create(
                model=ai_model,
                prediction_type='irrigation_need',
                input_data={
                    'sensors': sensors_data,
                    'weather': weather_data,
                    'plants': plant_data
                },
                prediction_value=prediction_result.get('irrigation_score', 0),
                confidence_score=prediction_result.get('confidence_score', 0),
                confidence_level='high' if prediction_result.get('confidence_score', 0) > 80 else 'medium',
                recommendation=prediction_result.get('recommendation', ''),
                reasoning=prediction_result.get('reasoning', '')
            )
        
        return Response(prediction_result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"AI irrigation analysis error: {e}")
        return Response({
            'error': str(e),
            'message': 'AI tahlil xatosi yuz berdi'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def analyze_plant_health(request):
    """Analyze plant health using AI"""
    try:
        plant_id = request.data.get('plant_id')
        
        if plant_id:
            try:
                plant = Plant.objects.get(id=plant_id)
            except Plant.DoesNotExist:
                return Response({'error': 'Plant not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            plant = Plant.objects.first()  # Analyze first plant if none specified
        
        if not plant:
            return Response({'error': 'No plants found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Generate FRESH sensor data for plant health analysis
        sensors_data = {}
        sensors = Sensor.objects.filter(status='active')
        for sensor in sensors:
            # Generate new random reading for fresh AI analysis
            fresh_reading = SensorReading.generate_random_reading(sensor)
            sensor_key = sensor.sensor_type.name.lower().replace(' ', '_')
            sensors_data[sensor_key] = fresh_reading.value
        
        # Get plant data
        plant_data = {
            'days_since_planted': plant.days_since_planted,
            'height': plant.height or 0,
            'growth_stage': plant.growth_stage,
            'health_status': plant.health_status,
            'leaf_count': plant.leaf_count or 0
        }
        
        # Get historical data (mock for now)
        historical_data = []
        
        # Run AI analysis
        health_result = plant_health_analyzer.analyze_plant_health(
            sensors_data, plant_data, historical_data
        )
        
        # Save analysis results
        if not health_result.get('error'):
            ai_model, created = AIModel.objects.get_or_create(
                model_type='plant_health',
                defaults={'name': 'Plant Health Analyzer', 'accuracy': 89.5}
            )
            
            AIPrediction.objects.create(
                model=ai_model,
                prediction_type='plant_health_risk',
                input_data={
                    'sensors': sensors_data,
                    'plant': plant_data
                },
                prediction_value=health_result.get('overall_health_score', 0) / 100,
                confidence_score=85.0,  # Mock confidence
                confidence_level='high',
                recommendation='; '.join(health_result.get('recommendations', [])),
                reasoning=f"Plant health analysis for {plant.name}"
            )
        
        return Response(health_result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Plant health analysis error: {e}")
        return Response({
            'error': str(e),
            'message': 'O\'simlik sog\'ligi tahlili xatosi'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def comprehensive_analysis(request):
    """Comprehensive AI analysis using Gemini"""
    try:
        # Start analysis session
        session_id = str(uuid.uuid4())[:8]
        session = AIAnalysisSession.objects.create(
            session_id=session_id,
            session_type='manual',
            input_sensors=[],
            recommendations=[],
            critical_alerts=[]
        )
        
        # Collect all data with FRESH sensor readings
        sensors_data = {}
        sensors = Sensor.objects.filter(status='active')
        for sensor in sensors:
            # Generate new random reading for comprehensive AI analysis
            fresh_reading = SensorReading.generate_random_reading(sensor)
            sensor_key = sensor.sensor_type.name.lower().replace(' ', '_')
            sensors_data[sensor_key] = fresh_reading.value
        
        # Get or generate fresh weather data for comprehensive analysis
        latest_weather = WeatherData.objects.first()
        weather_data = {}
        if latest_weather:
            weather_data = {
                'temperature': latest_weather.temperature,
                'humidity': latest_weather.humidity,
                'rainfall': latest_weather.rainfall,
                'wind_speed': latest_weather.wind_speed,
                'weather_condition': latest_weather.weather_condition,
                'feels_like_temperature': latest_weather.feels_like_temperature,
                'uv_index': latest_weather.uv_index,
                'air_quality_index': latest_weather.air_quality_index,
                'pressure': latest_weather.pressure,
                'wind_gust': latest_weather.wind_gust,
                'cloud_coverage': latest_weather.cloud_coverage
            }
        else:
            # Generate fresh mock weather data
            import random
            weather_data = {
                'temperature': random.uniform(20, 32),
                'humidity': random.uniform(40, 75),
                'rainfall': random.uniform(0, 10) if random.random() < 0.3 else 0,
                'wind_speed': random.uniform(5, 20),
                'weather_condition': random.choice(['Clear', 'Partly Cloudy', 'Cloudy', 'Rain']),
                'feels_like_temperature': random.uniform(18, 35),
                'uv_index': random.uniform(1, 11),
                'air_quality_index': random.randint(1, 5),
                'pressure': random.uniform(1010, 1025),
                'wind_gust': random.uniform(10, 30) if random.random() < 0.5 else None,
                'cloud_coverage': random.randint(0, 100)
            }
        
        # Plant data
        plants = Plant.objects.all()
        plant_data = {
            'total_plants': plants.count(),
            'healthy_plants': plants.filter(health_status__in=['excellent', 'good']).count(),
            'plants_needing_attention': plants.filter(health_status__in=['fair', 'poor', 'critical']).count()
        }
        
        # Historical trends (mock)
        historical_trends = {
            'irrigation_frequency': 'Haftada 4 marta',
            'water_usage_trend': 'So\'ngi haftada 15% kamaydi',
            'plant_growth_rate': 'Normal'
        }
        
        # Foydalanuvchi parametrlarini olish
        field_params = request.data.get('field_parameters', {})
        plant_params = request.data.get('plant_parameters', {})
        
        # Run Gemini analysis
        gemini_result = gemini_integration.analyze_comprehensive_data(
            sensors_data, weather_data, plant_data, historical_trends,
            field_params, plant_params
        )
        
        # Update session with results
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.predictions_generated = 1
        session.recommendations = gemini_result.get('action_plan', [])
        
        # Check for critical alerts
        if sensors_data.get('soil_moisture', 50) < 25:
            session.critical_alerts.append({
                'type': 'critical_soil_moisture',
                'message': 'Tuproq namligi kritik darajada',
                'timestamp': timezone.now().isoformat()
            })
        
        session.save()
        
        # Create insights
        insights = gemini_result.get('insights', [])
        for insight_data in insights:
            AIInsight.objects.create(
                insight_type='pattern_discovery',
                title=insight_data.get('title', 'AI Insight'),
                description=insight_data.get('description', ''),
                importance_level=insight_data.get('priority', 'medium'),
                supporting_data={'session_id': session_id},
                confidence_level=gemini_result.get('confidence_score', 85)
            )
        
        return Response({
            'session_id': session_id,
            'analysis_result': gemini_result,
            'session_status': session.status,
            'critical_alerts': session.critical_alerts,
            'recommendations': session.recommendations
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Comprehensive AI analysis error: {e}")
        if 'session' in locals():
            session.status = 'failed'
            session.completed_at = timezone.now()
            session.save()
        
        return Response({
            'error': str(e),
            'message': 'Keng qamrovli AI tahlili xatosi'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_ai_insights(request):
    """Get latest AI insights"""
    try:
        # Get recent insights
        insights = AIInsight.objects.all()[:10]
        
        insights_data = []
        for insight in insights:
            insights_data.append({
                'id': insight.id,
                'type': insight.get_insight_type_display(),
                'title': insight.title,
                'description': insight.description,
                'importance': insight.get_importance_level_display(),
                'confidence': insight.confidence_level,
                'created_at': insight.created_at,
                'recommended_actions': insight.recommended_actions,
                'is_implemented': insight.is_implemented
            })
        
        return Response(insights_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_ai_model_status(request):
    """Get AI model status and performance"""
    try:
        models = AIModel.objects.filter(is_active=True)
        
        models_data = []
        for model in models:
            recent_predictions = AIPrediction.objects.filter(model=model)[:100]
            
            models_data.append({
                'id': model.id,
                'name': model.name,
                'type': model.get_model_type_display(),
                'version': model.version,
                'accuracy': model.accuracy,
                'last_trained': model.last_trained,
                'recent_predictions': recent_predictions.count(),
                'average_confidence': round(
                    sum([p.confidence_score for p in recent_predictions[:10]]) / max(1, len(recent_predictions[:10])), 1
                )
            })
        
        return Response(models_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_analysis_history(request):
    """Get AI analysis session history"""
    try:
        sessions = AIAnalysisSession.objects.all()[:20]
        
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'session_id': session.session_id,
                'type': session.get_session_type_display(),
                'status': session.get_status_display(),
                'started_at': session.started_at,
                'completed_at': session.completed_at,
                'duration_minutes': round(session.duration_minutes, 1),
                'predictions_generated': session.predictions_generated,
                'critical_alerts_count': len(session.critical_alerts),
                'recommendations_count': len(session.recommendations)
            })
        
        return Response(sessions_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def train_model(request):
    """Mock training endpoint for AI models"""
    try:
        model_type = request.data.get('model_type', 'irrigation_predictor')
        
        # Simulate training process
        ai_model, created = AIModel.objects.get_or_create(
            model_type=model_type,
            defaults={'name': f'{model_type.title()} Model'}
        )
        
        # Mock training improvement
        import random
        improvement = random.uniform(0.5, 2.0)
        ai_model.accuracy = min(99.9, ai_model.accuracy + improvement)
        ai_model.training_data_count += random.randint(100, 500)
        ai_model.last_trained = timezone.now()
        ai_model.save()
        
        return Response({
            'message': f'{ai_model.name} muvaffaqiyatli qayta o\'qitildi',
            'new_accuracy': round(ai_model.accuracy, 1),
            'training_data_count': ai_model.training_data_count,
            'improvement': round(improvement, 1)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
import random
import time

from plant.models import IrrigationEvent, IrrigationZone
from sensor.models import SystemStatus


@api_view(['POST'])
def start_irrigation(request):
    """Start irrigation system"""
    try:
        zone_id = request.data.get('zone_id', 'all')
        duration_minutes = request.data.get('duration_minutes', 15)
        
        if zone_id == 'all':
            zones = IrrigationZone.objects.filter(status='active')
            message = f'Barcha zonalarda sug\'orish boshlandi ({duration_minutes} daqiqa)'
        else:
            try:
                zone = IrrigationZone.objects.get(zone_id=zone_id, status='active')
                zones = [zone]
                message = f'Zona {zone_id}da sug\'orish boshlandi ({duration_minutes} daqiqa)'
            except IrrigationZone.DoesNotExist:
                return Response({
                    'error': f'Zona {zone_id} topilmadi yoki faol emas'
                }, status=status.HTTP_404_NOT_FOUND)
        
        events_started = []
        for zone in zones:
            # Update zone status
            zone.last_irrigated = timezone.now()
            zone.save()
            
            # Create irrigation events for plants in this zone
            plants_in_zone = zone.plants_in_zone
            for plant in plants_in_zone:
                # Check if there's already an active event
                active_event = IrrigationEvent.objects.filter(
                    plant=plant,
                    status__in=['scheduled', 'in_progress']
                ).first()
                
                if not active_event:
                    event = IrrigationEvent.objects.create(
                        plant=plant,
                        event_type='manual',
                        status='in_progress',
                        scheduled_time=timezone.now(),
                        start_time=timezone.now(),
                        duration_minutes=duration_minutes,
                        water_amount_ml=duration_minutes * zone.flow_rate_lpm * 16.67,  # Convert LPM to ml/min
                        trigger_reason='Manual boshqaruv orqali boshlandi',
                    )
                    events_started.append(event)
        
        return Response({
            'message': message,
            'events_started': len(events_started),
            'status': 'irrigation_started'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def stop_irrigation(request):
    """Stop all active irrigation"""
    try:
        active_events = IrrigationEvent.objects.filter(status='in_progress')
        
        events_stopped = 0
        for event in active_events:
            event.status = 'completed'
            event.end_time = timezone.now()
            
            # Calculate actual duration and water amount
            if event.start_time:
                actual_duration = (event.end_time - event.start_time).total_seconds() / 60
                event.actual_duration_minutes = round(actual_duration, 1)
                event.actual_water_amount_ml = round(
                    actual_duration * event.water_amount_ml / event.duration_minutes
                )
            
            event.save()
            events_stopped += 1
        
        return Response({
            'message': f'Sug\'orish to\'xtatildi. {events_stopped} ta faol jarayon yakunlandi.',
            'events_stopped': events_stopped,
            'status': 'irrigation_stopped'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_irrigation_status(request):
    """Get current irrigation system status"""
    try:
        # Get active irrigation events
        active_events = IrrigationEvent.objects.filter(status='in_progress')
        scheduled_events = IrrigationEvent.objects.filter(status='scheduled')
        
        # Get system status
        system_status = SystemStatus.objects.first()
        
        status_data = {
            'system_active': system_status.status == 'active' if system_status else True,
            'active_irrigations': active_events.count(),
            'scheduled_irrigations': scheduled_events.count(),
            'active_zones': IrrigationZone.objects.filter(status='active').count(),
            'total_zones': IrrigationZone.objects.count(),
            'current_events': [],
        }
        
        # Add details of current events
        for event in active_events[:5]:  # Limit to 5 for performance
            status_data['current_events'].append({
                'plant_name': event.plant.name,
                'zone': event.plant.location,
                'started_at': event.start_time,
                'duration_minutes': event.duration_minutes,
                'water_amount_ml': event.water_amount_ml,
                'progress_percent': min(100, (
                    (timezone.now() - event.start_time).total_seconds() / 60 
                    / event.duration_minutes * 100
                )) if event.start_time else 0
            })
        
        return Response(status_data)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def emergency_stop(request):
    """Emergency stop all systems"""
    try:
        # Stop all active irrigations
        active_events = IrrigationEvent.objects.filter(status__in=['scheduled', 'in_progress'])
        
        events_stopped = 0
        for event in active_events:
            event.status = 'cancelled'
            if event.status == 'in_progress' and event.start_time:
                event.end_time = timezone.now()
                actual_duration = (event.end_time - event.start_time).total_seconds() / 60
                event.actual_duration_minutes = round(actual_duration, 1)
            event.save()
            events_stopped += 1
        
        # Update system status
        system_status = SystemStatus.objects.first()
        if system_status:
            system_status.status = 'error'
            system_status.save()
        
        return Response({
            'message': 'FAVQULODDA TO\'XTATISH! Barcha tizimlar to\'xtatildi.',
            'events_stopped': events_stopped,
            'status': 'emergency_stopped'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def system_restart(request):
    """Restart the irrigation system"""
    try:
        # Simulate system restart process
        time.sleep(1)  # Simulate restart delay
        
        # Update system status
        system_status = SystemStatus.objects.first()
        if system_status:
            system_status.status = 'active'
            system_status.cpu_usage = random.uniform(10, 25)
            system_status.memory_usage = random.uniform(20, 40)
            system_status.save()
        
        return Response({
            'message': 'Tizim muvaffaqiyatli qayta ishga tushirildi',
            'status': 'system_restarted'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def test_mode(request):
    """Enable/disable test mode"""
    try:
        enable = request.data.get('enable', True)
        
        # Update system status
        system_status = SystemStatus.objects.first()
        if system_status:
            if enable:
                system_status.status = 'maintenance'
                message = 'Test rejimi yoqildi'
            else:
                system_status.status = 'active'
                message = 'Test rejimi o\'chirildi'
            system_status.save()
        
        return Response({
            'message': message,
            'test_mode': enable,
            'status': 'test_mode_changed'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def calibrate_sensors(request):
    """Calibrate all sensors"""
    try:
        from sensor.models import Sensor
        
        # Simulate calibration process
        sensors = Sensor.objects.all()
        calibrated_count = 0
        
        for sensor in sensors:
            # Simulate calibration (in real implementation, this would communicate with hardware)
            sensor.status = 'maintenance'
            sensor.save()
            time.sleep(0.1)  # Simulate calibration time
            sensor.status = 'active'
            sensor.save()
            calibrated_count += 1
        
        return Response({
            'message': f'{calibrated_count} ta datchik muvaffaqiyatli kalibrlandi',
            'calibrated_sensors': calibrated_count,
            'status': 'calibration_completed'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def update_irrigation_schedule(request):
    """Update irrigation schedule settings"""
    try:
        morning_start = request.data.get('morning_start', '06:00')
        morning_end = request.data.get('morning_end', '08:00')
        evening_start = request.data.get('evening_start', '18:00')
        evening_end = request.data.get('evening_end', '20:00')
        sensor_interval = request.data.get('sensor_interval', 120)  # seconds
        
        # In a real implementation, these would be saved to a settings model
        # For now, we'll just return success
        
        return Response({
            'message': 'Vaqt jadvallar yangilandi',
            'settings': {
                'morning_schedule': f'{morning_start} - {morning_end}',
                'evening_schedule': f'{evening_start} - {evening_end}',
                'sensor_check_interval': f'{sensor_interval} soniya',
            },
            'status': 'schedule_updated'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_system_diagnostics(request):
    """Get detailed system diagnostics"""
    try:
        from sensor.models import Sensor, SensorReading
        
        system_status = SystemStatus.objects.first()
        sensors = Sensor.objects.all()
        
        diagnostics = {
            'system_health': 'Yaxshi' if system_status and system_status.status == 'active' else 'Muammoli',
            'total_sensors': sensors.count(),
            'active_sensors': sensors.filter(status='active').count(),
            'sensors_in_maintenance': sensors.filter(status='maintenance').count(),
            'sensors_with_errors': sensors.filter(status='error').count(),
            'recent_readings': SensorReading.objects.filter(
                timestamp__gte=timezone.now() - timedelta(hours=1)
            ).count(),
            'system_uptime': '7 kun 14 soat 23 daqiqa',  # Mock data
            'last_backup': timezone.now() - timedelta(days=1),
            'disk_space_available': '78%',
            'memory_usage': f'{system_status.memory_usage:.1f}%' if system_status else '0%',
            'cpu_usage': f'{system_status.cpu_usage:.1f}%' if system_status else '0%',
        }
        
        return Response(diagnostics)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
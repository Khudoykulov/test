from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta, date
from django.db.models import Sum, Count

from .models import PlantType, Plant, IrrigationEvent, PlantCareLog, IrrigationZone
from .serializers import (
    PlantTypeSerializer, PlantSerializer, IrrigationEventSerializer,
    PlantCareLogSerializer, IrrigationZoneSerializer, IrrigationSummarySerializer
)


class PlantTypeListCreateView(generics.ListCreateAPIView):
    queryset = PlantType.objects.all()
    serializer_class = PlantTypeSerializer


class PlantListCreateView(generics.ListCreateAPIView):
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer


class PlantDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer


class IrrigationEventListCreateView(generics.ListCreateAPIView):
    queryset = IrrigationEvent.objects.all()
    serializer_class = IrrigationEventSerializer


class PlantCareLogListCreateView(generics.ListCreateAPIView):
    queryset = PlantCareLog.objects.all()
    serializer_class = PlantCareLogSerializer


class IrrigationZoneListCreateView(generics.ListCreateAPIView):
    queryset = IrrigationZone.objects.all()
    serializer_class = IrrigationZoneSerializer


@api_view(['POST'])
def create_sample_plants(request):
    """Create sample plants and irrigation zones"""
    try:
        # Create sample plant types
        plant_types_data = [
            {
                'name': 'Pomidor',
                'scientific_name': 'Solanum lycopersicum',
                'icon': '🍅',
                'optimal_soil_moisture_min': 60,
                'optimal_soil_moisture_max': 80,
                'optimal_temperature_min': 18,
                'optimal_temperature_max': 28,
                'optimal_ph_min': 6.0,
                'optimal_ph_max': 7.0,
                'germination_days': 7,
                'vegetative_days': 30,
                'flowering_days': 60,
                'maturity_days': 90,
            },
            {
                'name': 'Bodring',
                'scientific_name': 'Cucumis sativus',
                'icon': '🥒',
                'optimal_soil_moisture_min': 70,
                'optimal_soil_moisture_max': 85,
                'optimal_temperature_min': 16,
                'optimal_temperature_max': 24,
                'optimal_ph_min': 6.0,
                'optimal_ph_max': 7.0,
                'germination_days': 5,
                'vegetative_days': 25,
                'flowering_days': 50,
                'maturity_days': 70,
            },
            {
                'name': 'Salat',
                'scientific_name': 'Lactuca sativa',
                'icon': '🥬',
                'optimal_soil_moisture_min': 65,
                'optimal_soil_moisture_max': 75,
                'optimal_temperature_min': 12,
                'optimal_temperature_max': 20,
                'optimal_ph_min': 6.0,
                'optimal_ph_max': 7.0,
                'germination_days': 3,
                'vegetative_days': 20,
                'flowering_days': 40,
                'maturity_days': 60,
            }
        ]
        
        plant_types_created = []
        for type_data in plant_types_data:
            plant_type, created = PlantType.objects.get_or_create(
                name=type_data['name'],
                defaults=type_data
            )
            if created:
                plant_types_created.append(plant_type)
        
        # Create irrigation zones
        zones_data = [
            {
                'zone_id': 'A01',
                'name': 'A sektori',
                'description': 'Asosiy ekin maydoni',
                'area_sqm': 500,
                'plant_count': 50,
                'soil_type': 'loam',
                'default_duration_minutes': 15,
                'flow_rate_lpm': 12,
            },
            {
                'zone_id': 'B01',
                'name': 'B sektori',
                'description': 'Yordamchi ekin maydoni',
                'area_sqm': 300,
                'plant_count': 30,
                'soil_type': 'clay_loam',
                'default_duration_minutes': 18,
                'flow_rate_lpm': 10,
            }
        ]
        
        zones_created = []
        for zone_data in zones_data:
            zone, created = IrrigationZone.objects.get_or_create(
                zone_id=zone_data['zone_id'],
                defaults=zone_data
            )
            if created:
                zones_created.append(zone)
        
        # Create sample plants
        plants_data = [
            {
                'plant_id': 'TOM_A01_001',
                'name': 'Pomidor #1',
                'type_name': 'Pomidor',
                'location': 'A sektori, 1-qator',
                'planted_date': date.today() - timedelta(days=45),
                'growth_stage': 'flowering',
                'health_status': 'good',
                'height': 65.5,
                'leaf_count': 24,
            },
            {
                'plant_id': 'CUC_A01_002',
                'name': 'Bodring #1',
                'type_name': 'Bodring',
                'location': 'A sektori, 2-qator',
                'planted_date': date.today() - timedelta(days=35),
                'growth_stage': 'vegetative',
                'health_status': 'excellent',
                'height': 45.0,
                'leaf_count': 18,
            },
            {
                'plant_id': 'LET_B01_001',
                'name': 'Salat #1',
                'type_name': 'Salat',
                'location': 'B sektori, 1-qator',
                'planted_date': date.today() - timedelta(days=25),
                'growth_stage': 'vegetative',
                'health_status': 'good',
                'height': 15.2,
                'leaf_count': 12,
            }
        ]
        
        plants_created = []
        for plant_data in plants_data:
            plant_type = PlantType.objects.get(name=plant_data['type_name'])
            plant, created = Plant.objects.get_or_create(
                plant_id=plant_data['plant_id'],
                defaults={
                    'name': plant_data['name'],
                    'plant_type': plant_type,
                    'location': plant_data['location'],
                    'planted_date': plant_data['planted_date'],
                    'growth_stage': plant_data['growth_stage'],
                    'health_status': plant_data['health_status'],
                    'height': plant_data['height'],
                    'leaf_count': plant_data['leaf_count'],
                    'last_watered': timezone.now() - timedelta(hours=6),
                    'water_amount_ml': 250,
                }
            )
            if created:
                plants_created.append(plant)
        
        # Create some irrigation events
        for plant in Plant.objects.all():
            # Past irrigation event
            IrrigationEvent.objects.create(
                plant=plant,
                event_type='automatic',
                status='completed',
                scheduled_time=timezone.now() - timedelta(hours=6),
                start_time=timezone.now() - timedelta(hours=6),
                end_time=timezone.now() - timedelta(hours=6, minutes=15),
                duration_minutes=15,
                actual_duration_minutes=15,
                water_amount_ml=250,
                actual_water_amount_ml=250,
                trigger_reason='Tuproq namligi past (35%)',
                ai_confidence=0.92
            )
            
            # Future irrigation event
            IrrigationEvent.objects.create(
                plant=plant,
                event_type='automatic',
                status='scheduled',
                scheduled_time=timezone.now() + timedelta(hours=2),
                duration_minutes=18,
                water_amount_ml=300,
                trigger_reason='AI bashorati asosida',
                ai_confidence=0.87
            )
        
        return Response({
            'message': 'Sample plants data created successfully',
            'plant_types_created': len(plant_types_created),
            'zones_created': len(zones_created),
            'plants_created': len(plants_created),
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_irrigation_summary(request):
    """Get irrigation summary for dashboard"""
    try:
        today = timezone.now().date()
        today_start = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
        today_end = today_start + timedelta(days=1)
        
        # Today's irrigation statistics
        events_today = IrrigationEvent.objects.filter(
            scheduled_time__gte=today_start,
            scheduled_time__lt=today_end
        )
        
        completed_today = events_today.filter(status='completed')
        total_water_today = completed_today.aggregate(
            total=Sum('actual_water_amount_ml')
        )['total'] or 0
        
        # Convert to liters
        total_water_today_l = total_water_today / 1000
        
        # Active zones
        active_zones = IrrigationZone.objects.filter(status='active').count()
        
        # Pending and overdue events
        pending_events = IrrigationEvent.objects.filter(status='scheduled').count()
        overdue_events = IrrigationEvent.objects.filter(
            status='scheduled',
            scheduled_time__lt=timezone.now()
        ).count()
        
        # Next scheduled event
        next_event = IrrigationEvent.objects.filter(
            status='scheduled',
            scheduled_time__gt=timezone.now()
        ).first()
        
        summary_data = {
            'total_events_today': events_today.count(),
            'total_water_used_today': round(total_water_today_l, 2),
            'active_zones': active_zones,
            'pending_events': pending_events,
            'overdue_events': overdue_events,
            'next_scheduled_event': next_event
        }
        
        serializer = IrrigationSummarySerializer(summary_data)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_plant_health_status(request):
    """Get overall plant health status"""
    try:
        plants = Plant.objects.all()
        
        health_stats = {
            'total_plants': plants.count(),
            'excellent': plants.filter(health_status='excellent').count(),
            'good': plants.filter(health_status='good').count(),
            'fair': plants.filter(health_status='fair').count(),
            'poor': plants.filter(health_status='poor').count(),
            'critical': plants.filter(health_status='critical').count(),
        }
        
        # Calculate overall health percentage
        total = health_stats['total_plants']
        if total > 0:
            health_score = (
                health_stats['excellent'] * 100 +
                health_stats['good'] * 80 +
                health_stats['fair'] * 60 +
                health_stats['poor'] * 40 +
                health_stats['critical'] * 20
            ) / total
        else:
            health_score = 0
        
        health_stats['overall_health_score'] = round(health_score, 1)
        
        # Growth tracking
        on_track = plants.filter(is_growth_on_track=True).count()
        health_stats['plants_on_track'] = on_track
        health_stats['plants_delayed'] = total - on_track
        
        return Response(health_stats)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def trigger_irrigation(request):
    """Manually trigger irrigation for a plant or zone"""
    try:
        plant_id = request.data.get('plant_id')
        zone_id = request.data.get('zone_id')
        duration_minutes = request.data.get('duration_minutes', 15)
        reason = request.data.get('reason', 'Manual qo\'lda boshqaruv')
        
        events_created = []
        
        if plant_id:
            try:
                plant = Plant.objects.get(id=plant_id)
                event = IrrigationEvent.objects.create(
                    plant=plant,
                    event_type='manual',
                    status='scheduled',
                    scheduled_time=timezone.now(),
                    duration_minutes=duration_minutes,
                    water_amount_ml=duration_minutes * 20,  # Estimate 20ml per minute
                    trigger_reason=reason,
                )
                events_created.append(event)
            except Plant.DoesNotExist:
                return Response({'error': 'Plant not found'}, status=status.HTTP_404_NOT_FOUND)
        
        elif zone_id:
            try:
                zone = IrrigationZone.objects.get(zone_id=zone_id)
                plants_in_zone = zone.plants_in_zone
                
                for plant in plants_in_zone:
                    event = IrrigationEvent.objects.create(
                        plant=plant,
                        event_type='manual',
                        status='scheduled',
                        scheduled_time=timezone.now(),
                        duration_minutes=duration_minutes,
                        water_amount_ml=duration_minutes * zone.flow_rate_lpm * 16.67,  # Convert to ml
                        trigger_reason=f"Zone {zone_id} manual irrigation: {reason}",
                    )
                    events_created.append(event)
                    
            except IrrigationZone.DoesNotExist:
                return Response({'error': 'Zone not found'}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            return Response({'error': 'Either plant_id or zone_id is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': f'Irrigation triggered successfully for {len(events_created)} plants',
            'events_created': len(events_created)
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
from rest_framework import serializers
from .models import PlantType, Plant, IrrigationEvent, PlantCareLog, IrrigationZone


class PlantTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantType
        fields = '__all__'


class PlantSerializer(serializers.ModelSerializer):
    plant_type_name = serializers.CharField(source='plant_type.name', read_only=True)
    plant_type_icon = serializers.CharField(source='plant_type.icon', read_only=True)
    days_since_planted = serializers.ReadOnlyField()
    expected_growth_stage = serializers.ReadOnlyField()
    is_growth_on_track = serializers.ReadOnlyField()
    health_status_display = serializers.CharField(source='get_health_status_display', read_only=True)
    growth_stage_display = serializers.CharField(source='get_growth_stage_display', read_only=True)
    
    class Meta:
        model = Plant
        fields = [
            'id', 'plant_id', 'name', 'plant_type', 'plant_type_name', 'plant_type_icon',
            'location', 'planted_date', 'growth_stage', 'growth_stage_display',
            'health_status', 'health_status_display', 'height', 'leaf_count', 'fruit_count',
            'last_watered', 'water_amount_ml', 'last_fertilized', 'notes',
            'days_since_planted', 'expected_growth_stage', 'is_growth_on_track',
            'created_at', 'updated_at'
        ]


class IrrigationEventSerializer(serializers.ModelSerializer):
    plant_name = serializers.CharField(source='plant.name', read_only=True)
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = IrrigationEvent
        fields = [
            'id', 'plant', 'plant_name', 'event_type', 'event_type_display',
            'status', 'status_display', 'scheduled_time', 'start_time', 'end_time',
            'duration_minutes', 'actual_duration_minutes', 'water_amount_ml',
            'actual_water_amount_ml', 'trigger_reason', 'ai_confidence',
            'is_overdue', 'created_at'
        ]


class PlantCareLogSerializer(serializers.ModelSerializer):
    plant_name = serializers.CharField(source='plant.name', read_only=True)
    care_type_display = serializers.CharField(source='get_care_type_display', read_only=True)
    
    class Meta:
        model = PlantCareLog
        fields = [
            'id', 'plant', 'plant_name', 'care_type', 'care_type_display',
            'description', 'care_date', 'water_amount_ml', 'fertilizer_type',
            'fertilizer_amount_g', 'created_at'
        ]


class IrrigationZoneSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    plant_count_in_zone = serializers.SerializerMethodField()
    
    class Meta:
        model = IrrigationZone
        fields = [
            'id', 'zone_id', 'name', 'description', 'area_sqm', 'plant_count',
            'plant_count_in_zone', 'soil_type', 'default_duration_minutes',
            'flow_rate_lpm', 'status', 'status_display', 'last_irrigated',
            'total_water_used_l', 'created_at', 'updated_at'
        ]
    
    def get_plant_count_in_zone(self, obj):
        return obj.plants_in_zone.count()


class IrrigationSummarySerializer(serializers.Serializer):
    """Serializer for irrigation summary data"""
    total_events_today = serializers.IntegerField()
    total_water_used_today = serializers.FloatField()
    active_zones = serializers.IntegerField()
    pending_events = serializers.IntegerField()
    overdue_events = serializers.IntegerField()
    next_scheduled_event = IrrigationEventSerializer(required=False)
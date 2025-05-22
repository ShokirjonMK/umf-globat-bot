from rest_framework import serializers
from .models import ScheduleInterview

class ScheduleInterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleInterview
        fields = '__all__'

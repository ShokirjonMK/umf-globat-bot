from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import (
    ScheduleInterview, TelegramUser, Company, OrientationType,
    Truck, TruckOrientation, Driver, AllowedGroup
)
from django_celery_beat.models import (
    ClockedSchedule,
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
    SolarSchedule
)

# Django auth qismlarini olib tashlash
admin.site.unregister(Group)
admin.site.unregister(User)

# Celery periodic task qismlarini olib tashlash
admin.site.unregister(ClockedSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(PeriodicTask)
admin.site.unregister(SolarSchedule)

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'full_name', 'username', 'language_code', 'is_bot', 'joined_at')
    search_fields = ('first_name', 'last_name', 'username', 'telegram_id')
    list_filter = ('is_bot', 'language_code', 'joined_at')
    ordering = ('-joined_at',)

    def full_name(self, obj):
        return obj.full_name()


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')
    search_fields = ('title',)
    list_filter = ('is_active',)


@admin.register(OrientationType)
class OrientationTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(AllowedGroup)
class AllowedGroupAdmin(admin.ModelAdmin):
    list_display = ('group_id',)
    search_fields = ('group_id',)

@admin.register(Truck)
class TruckAdmin(admin.ModelAdmin):
    list_display = ('number', 'plate_number', 'make', 'model', 'year', 'status')
    search_fields = ('number', 'plate_number', 'vin_number')
    list_filter = ('status', 'make', 'model', 'year')
    ordering = ('number',)


@admin.register(TruckOrientation)
class TruckOrientationAdmin(admin.ModelAdmin):
    list_display = ('truck', 'orientation_type', 'status', 'updated_at')
    search_fields = ('truck__number', 'orientation_type__name')
    list_filter = ('status', 'orientation_type')
    ordering = ('-updated_at',)


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'date', 'mode', 'driver_type',
        'company', 'truck', 'confirmation', 'sign', 'docusign'
    )
    search_fields = ('full_name', 'company__title', 'truck__number')
    list_filter = ('mode', 'driver_type', 'company', 'date', 'sign', 'docusign')
    ordering = ('-date',)



@admin.register(ScheduleInterview)
class ScheduleInterviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
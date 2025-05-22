from django.db import models


class AllowedGroup(models.Model):
    group_id = models.CharField(max_length=100, unique=True, help_text="Group id")

    def __str__(self):
        return self.group_id
    

class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    language_code = models.CharField(max_length=100, blank=True, null=True)
    is_bot = models.BooleanField(default=False)

    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip()

    def __str__(self):
        return f"{self.full_name()} (@{self.username}) - {self.telegram_id}"


class Company(models.Model):
    title = models.CharField(max_length=100, unique=True, help_text="Kompaniya nomi (masalan: MUNISA)")
    is_active = models.BooleanField(default=True, help_text="Kompaniya hozirda faolmi?")

    def __str__(self):
        return self.title


class OrientationType(models.Model):
    """
    Har xil orientation turlari: ELD, DISPATCH, SAFETY, boshqalar.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Orientation nomi (masalan: DISPATCH)")

    def __str__(self):
        return self.name

class TruckStatus(models.Model):
    title = models.CharField(max_length=100, unique=True, help_text="Holat nomi (masalan: Enroute, In Maintenance, Active)")
    
    def __str__(self):
        return self.title


class Truck(models.Model):
    number = models.CharField(max_length=100, null=True, blank=True, help_text="Truck ichki raqami (masalan: TRK-245)")
    plate_number = models.CharField(max_length=100, blank=True, null=True, help_text="Davlat raqami (masalan: TX 98325 AB)")
    vin_number = models.CharField(max_length=100, blank=True, null=True, help_text="VIN (Vehicle Identification Number)")
    
    make = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    tm_or_b = models.CharField(max_length=100, blank=True, null=True, help_text="TM/B (masalan: AT, MT)")
    color = models.CharField(max_length=100, blank=True, null=True)
    
    status = models.ForeignKey(TruckStatus, on_delete=models.SET_NULL, null=True, blank=True, help_text="Truck status (masalan: Enroute)")
    notes = models.TextField(blank=True, null=True)
    
    year = models.PositiveIntegerField(blank=True, null=True)
    st = models.CharField(max_length=100, blank=True, null=True, help_text="ST (masalan: TX, IL)")
    whose_truck = models.CharField(max_length=100, blank=True, null=True, help_text="Whose Truck (masalan: Owner)")
    
    owner_name = models.CharField(max_length=100, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    driver_name = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.number



class TruckOrientation(models.Model):
    """
    Har bir Truck uchun har bir OrientationType bo‘yicha status.
    """
    class Status(models.TextChoices):
        NOT_DONE = 'not_done', 'Not Done'
        DONE = 'done', 'Done'

    truck = models.ForeignKey(Truck, on_delete=models.CASCADE, related_name='orientations')
    orientation_type = models.ForeignKey(OrientationType, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=100,
        choices=Status.choices,
        default=Status.NOT_DONE,
        help_text="Orientation holati"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('truck', 'orientation_type')

    def __str__(self):
        return f"{self.truck.number} - {self.orientation_type.name} - {self.status}"


class Driver(models.Model):
    """
    Driverlar haqida ma'lumotlar, kompaniya, truck, docusign va boshqalar bilan birga.
    """
    DRIVER_TYPE_CHOICES = [
        ('company', 'Company Driver'),
        ('owner', 'Owner Operator'),
        ('reefer', 'Reefer Driver')
    ]

    MODE_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline')
    ]

    full_name = models.CharField(max_length=100, help_text="Haydovchining to‘liq ismi")
    date = models.DateField(help_text="Kiritilgan sana")
    mode = models.CharField(max_length=100, choices=MODE_CHOICES, default='offline', help_text="Driverning hozirgi holati")
    driver_type = models.CharField(max_length=100, choices=DRIVER_TYPE_CHOICES, blank=True, null=True, help_text="Driver turi")
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    truck = models.ForeignKey(Truck, on_delete=models.SET_NULL, null=True, blank=True)
    confirmation = models.CharField(max_length=100, blank=True, null=True, help_text="Confirmation status")
    sign = models.CharField(max_length=100, blank=True, null=True, help_text="Sign (masalan: signed)")
    docusign = models.CharField(max_length=100, blank=True, null=True, help_text="DocuSign status")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name



class TruckInsurance(models.Model):
    truck = models.OneToOneField("Truck", on_delete=models.CASCADE, related_name="insurance")
    proof_of_ownership = models.BooleanField(default=False)
    safety_carrier = models.BooleanField(default=False)
    liability_and_cargo = models.BooleanField(default=False)
    physical_damage = models.BooleanField(default=False)
    physical_exp = models.DateField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)

class TruckInspection(models.Model):
    truck = models.OneToOneField("Truck", on_delete=models.CASCADE, related_name="inspection")
    registration = models.CharField(max_length=100)
    annual_inspection = models.CharField(max_length=100)
    rental_agreement = models.CharField(max_length=100)
    outbound_inspection = models.CharField(max_length=100)






class ScheduleInterview(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"